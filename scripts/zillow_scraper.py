"""
KBros Zillow Lead Scraper - 50-Mile Radius Springfield MO
Targets distressed listings, calculates profit per deal, outputs clean call sheet.

Requirements:
  py -m pip install requests gspread google-auth

Usage:
  py scripts/zillow_scraper.py
"""

import requests
import json
import time
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# ---- CONFIG ------------------------------------------------------------------

SHEET_ID      = "18oJwsncdmlaDrT2O_q3sOoOJwfB7SdKRWLO37HWAgSo"
KEY_FILE      = os.path.join(os.path.dirname(__file__), "zillow-bot-key.json")
SHEET_TAB     = "Sheet1"
YOUR_NUMBER   = "(417) 834-1226"
ASSIGNMENT_FEE = 5000
AVG_REPAIRS    = 15000

# --- sort-by-days query string (surfaces oldest/most distressed first) ---
_DAYS = "?searchQueryState=%7B%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22days%22%7D%7D%7D"

SEARCH_URLS = [
    # Springfield ZIPs — base pass
    ("SPR 65802",           "https://www.zillow.com/springfield-mo-65802/"),
    ("SPR 65803",           "https://www.zillow.com/springfield-mo-65803/"),
    ("SPR 65804",           "https://www.zillow.com/springfield-mo-65804/"),
    ("SPR 65807",           "https://www.zillow.com/springfield-mo-65807/"),
    ("SPR 65809",           "https://www.zillow.com/springfield-mo-65809/"),
    # Springfield — sorted by oldest DOM (guaranteed distressed)
    ("SPR 65802 OLD",       "https://www.zillow.com/springfield-mo-65802/" + _DAYS),
    ("SPR 65803 OLD",       "https://www.zillow.com/springfield-mo-65803/" + _DAYS),
    ("SPR 65804 OLD",       "https://www.zillow.com/springfield-mo-65804/" + _DAYS),
    ("SPR 65807 OLD",       "https://www.zillow.com/springfield-mo-65807/" + _DAYS),
    # Springfield FSBO (owner = motivated seller almost by definition)
    ("SPR FSBO",            "https://www.zillow.com/springfield-mo/fsbo/"),
    # Springfield foreclosures
    ("SPR Foreclosures",    "https://www.zillow.com/springfield-mo/foreclosures/"),
    # 50-mile suburbs — base
    ("Nixa",                "https://www.zillow.com/nixa-mo/"),
    ("Ozark",               "https://www.zillow.com/ozark-mo/"),
    ("Republic",            "https://www.zillow.com/republic-mo/"),
    ("Willard",             "https://www.zillow.com/willard-mo/"),
    ("Strafford",           "https://www.zillow.com/strafford-mo/"),
    ("Rogersville",         "https://www.zillow.com/rogersville-mo/"),
    ("Marshfield",          "https://www.zillow.com/marshfield-mo/"),
    ("Bolivar",             "https://www.zillow.com/bolivar-mo/"),
    ("Branson",             "https://www.zillow.com/branson-mo/"),
    # Suburbs — sorted oldest first
    ("Nixa OLD",            "https://www.zillow.com/nixa-mo/" + _DAYS),
    ("Ozark OLD",           "https://www.zillow.com/ozark-mo/" + _DAYS),
    ("Republic OLD",        "https://www.zillow.com/republic-mo/" + _DAYS),
    # More surrounding towns within 50 miles
    ("Battlefield",         "https://www.zillow.com/battlefield-mo/"),
    ("Fair Grove",          "https://www.zillow.com/fair-grove-mo/"),
    ("Clever",              "https://www.zillow.com/clever-mo/"),
    ("Aurora",              "https://www.zillow.com/aurora-mo/"),
    ("Monett",              "https://www.zillow.com/monett-mo/"),
    ("Mountain Grove",      "https://www.zillow.com/mountain-grove-mo/"),
    ("Ava",                 "https://www.zillow.com/ava-mo/"),
    ("Cassville",           "https://www.zillow.com/cassville-mo/"),
    ("West Plains",         "https://www.zillow.com/west-plains-mo/"),
]

DISTRESS_KEYWORDS = [
    # Condition signals
    "as-is", "as is", "fixer", "fixer upper", "needs work", "needs tlc", "tlc",
    "handyman", "handyman special", "needs repair", "needs updating", "needs renovation",
    "fire damage", "water damage", "flood damage", "storm damage", "foundation",
    "mold", "roof", "structural", "unfinished", "incomplete",
    # Seller motivation signals
    "motivated", "motivated seller", "must sell", "must close", "price reduced",
    "reduced", "bring offers", "all offers considered", "below market",
    "below appraised", "priced to sell", "priced below", "sell fast",
    "quick close", "quick sale", "cash only", "investor special",
    # Life event signals (highest motivation)
    "estate sale", "trust sale", "probate", "inherited", "inheritance",
    "divorce", "bankruptcy", "foreclosure", "pre-foreclosure", "bank owned",
    "reo", "short sale", "auction", "lien", "behind on payments",
    "relocating", "relocation", "job transfer", "downsizing",
    # Ownership signals
    "vacant", "abandoned", "empty", "unoccupied",
    "fsbo", "for sale by owner", "owner will carry",
]

SHEET_HEADERS = [
    "Date Added", "Address", "Asking Price", "Offer Price", "Your Profit",
    "MAO", "Price Drop", "Beds", "Baths", "Sqft", "Days on Market",
    "Distress Signals", "Score", "Agent Phone", "Your Number",
    "Zillow URL", "Status", "Notes"
]

LEADS_JSON = os.path.join(os.path.dirname(__file__), "..", "public", "leads.json")

# ---- SCRAPER -----------------------------------------------------------------

BROWSER_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "referer": "https://www.google.com/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "upgrade-insecure-requests": "1",
}


def fetch_listings(session, url):
    try:
        resp = session.get(url, headers=BROWSER_HEADERS, timeout=20)
        if resp.status_code != 200:
            return []

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            resp.text, re.DOTALL
        )
        if not match:
            return []

        data        = json.loads(match.group(1))
        search_state = (
            data.get("props", {})
                .get("pageProps", {})
                .get("searchPageState", {})
        )
        return (
            search_state.get("cat1", {})
                        .get("searchResults", {})
                        .get("listResults", [])
        )
    except Exception:
        return []


def fetch_agent_phone(session, detail_url):
    """Fetch the listing detail page and extract agent phone number."""
    if not detail_url:
        return ""
    try:
        full_url = detail_url if detail_url.startswith("http") else "https://www.zillow.com" + detail_url
        resp = session.get(full_url, headers=BROWSER_HEADERS, timeout=15)
        if resp.status_code != 200:
            return ""

        # Phone patterns on Zillow detail pages
        patterns = [
            r'"phoneNumber"\s*:\s*"([^"]+)"',
            r'"phone"\s*:\s*"([^"]+)"',
            r'tel:([0-9\-\(\)\s]{10,15})',
            r'(\(\d{3}\)\s*\d{3}[-\s]\d{4})',
            r'(\d{3}[-\.]\d{3}[-\.]\d{4})',
        ]
        for pat in patterns:
            m = re.search(pat, resp.text)
            if m:
                phone = m.group(1).strip()
                if len(re.sub(r'\D', '', phone)) >= 10:
                    digits = re.sub(r'\D', '', phone)
                    return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        return ""
    except Exception:
        return ""


# ---- SCORING & MATH ----------------------------------------------------------

def calc_deal(price_raw):
    if not price_raw or price_raw <= 0:
        return None, None, None
    arv        = price_raw
    mao        = int(arv * 0.70 - AVG_REPAIRS)
    offer_at   = mao - ASSIGNMENT_FEE
    profit     = mao - price_raw  # positive = already a deal at asking
    return mao, offer_at, profit


def score_listing(listing):
    address    = listing.get("address", "N/A")
    price      = listing.get("price", "")
    price_raw  = listing.get("unformattedPrice") or 0
    beds       = listing.get("beds", "")
    baths      = listing.get("baths", "")
    sqft       = listing.get("area", "")
    dom        = listing.get("daysOnZillow") or 0
    price_drop = listing.get("priceReduction", "")
    url        = listing.get("detailUrl", "")

    var_data   = listing.get("variableData") or {}
    text_blob  = " ".join([
        str(listing.get("statusText", "")),
        str(var_data.get("text", "") if isinstance(var_data, dict) else ""),
        str(listing.get("listingSubType", "")),
        str(listing.get("statusType", "")),
    ]).lower()

    signals = [kw for kw in DISTRESS_KEYWORDS if kw in text_blob]
    score   = len(signals)

    if price_drop:
        score += 3
        signals.insert(0, f"price cut ({price_drop})")
    # DOM scoring — the older the listing, the more desperate the seller
    if dom >= 365:
        score += 8
        signals.append(f"DOM {dom}d *** ANCIENT ***")
    elif dom >= 180:
        score += 6
        signals.append(f"DOM {dom}d ** VERY OLD **")
    elif dom >= 90:
        score += 4
        signals.append(f"DOM {dom}d * OLD *")
    elif dom >= 60:
        score += 2
        signals.append(f"DOM {dom}d")
    elif dom >= 30:
        score += 1

    mao, offer_at, profit = calc_deal(price_raw)

    return {
        "address":    address,
        "price":      price,
        "price_raw":  price_raw,
        "price_drop": price_drop or "",
        "beds":       beds,
        "baths":      baths,
        "sqft":       sqft,
        "dom":        dom,
        "signals":    ", ".join(signals) if signals else "",
        "score":      score,
        "mao":        f"${mao:,}" if mao else "",
        "mao_raw":    mao or 0,
        "offer_at":   f"${offer_at:,}" if offer_at else "",
        "profit":     profit or 0,
        "url":        url,
        "agent_phone": "",
    }


# ---- GOOGLE SHEETS -----------------------------------------------------------

def connect_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds  = Credentials.from_service_account_file(KEY_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_TAB)


def format_sheet(sheet):
    """Apply professional formatting to the sheet."""
    try:
        import gspread.utils as gu
        # Freeze header row
        sheet.spreadsheet.batch_update({"requests": [{
            "updateSheetProperties": {
                "properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }
        }]})
        # Bold + dark header
        sheet.format("A1:R1", {
            "backgroundColor": {"red": 0.18, "green": 0.18, "blue": 0.22},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}, "fontSize": 10},
            "horizontalAlignment": "CENTER",
        })
        # Column widths
        col_widths = [90, 240, 100, 100, 140, 100, 90, 45, 45, 60, 80, 280, 55, 120, 110, 260, 80, 160]
        requests = []
        for i, w in enumerate(col_widths):
            requests.append({"updateDimensionProperties": {
                "range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
                "properties": {"pixelSize": w},
                "fields": "pixelSize"
            }})
        sheet.spreadsheet.batch_update({"requests": requests})
    except Exception as e:
        print(f"  (sheet formatting skipped: {e})")


def color_rows(sheet, leads):
    """Color rows by score: green=deal, red=hot, yellow=warm, white=cold."""
    try:
        all_rows = sheet.get_all_values()
        requests = []
        for i, row in enumerate(all_rows[1:], start=2):
            if len(row) < 13:
                continue
            try:
                score = int(row[12])
                profit_cell = row[4]
                is_deal = "DEAL NOW" in profit_cell
            except Exception:
                continue

            if is_deal:
                bg = {"red": 0.85, "green": 0.97, "blue": 0.87}  # green
            elif score >= 3:
                bg = {"red": 1.0, "green": 0.92, "blue": 0.92}   # red
            elif score >= 1:
                bg = {"red": 1.0, "green": 0.97, "blue": 0.84}   # yellow
            else:
                continue

            requests.append({"repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": i - 1, "endRowIndex": i, "startColumnIndex": 0, "endColumnIndex": 18},
                "cell": {"userEnteredFormat": {"backgroundColor": bg}},
                "fields": "userEnteredFormat.backgroundColor"
            }})

        if requests:
            sheet.spreadsheet.batch_update({"requests": requests})
    except Exception as e:
        print(f"  (row coloring skipped: {e})")


def write_leads_json(leads):
    """Write top leads to public/leads.json for the React app to consume."""
    top = [l for l in leads if l["score"] > 0][:50]
    output = []
    for l in top:
        profit_val = l.get("profit", 0)
        output.append({
            "id":         l["address"].replace(" ", "-").lower()[:40],
            "address":    l["address"],
            "price":      l["price"],
            "priceRaw":   l.get("price_raw", 0),
            "offerAt":    l["offer_at"],
            "mao":        l["mao"],
            "profit":     profit_val,
            "profitLabel": f"+${profit_val:,} — DEAL NOW" if profit_val > 0 else f"Need ${abs(profit_val):,} off asking",
            "isDeal":     profit_val > 0,
            "priceDrop":  l["price_drop"],
            "beds":       l["beds"],
            "baths":      l["baths"],
            "sqft":       l["sqft"],
            "dom":        l["dom"],
            "signals":    l["signals"],
            "score":      l["score"],
            "agentPhone": l.get("agent_phone", ""),
            "yourNumber": YOUR_NUMBER,
            "url":        ("https://www.zillow.com" + l["url"]) if l["url"] and not l["url"].startswith("http") else l["url"],
            "status":     "New",
        })
    try:
        os.makedirs(os.path.dirname(LEADS_JSON), exist_ok=True)
        with open(LEADS_JSON, "w") as f:
            json.dump({"updated": datetime.now().isoformat(), "leads": output}, f, indent=2)
        print(f"  Wrote {len(output)} leads to public/leads.json")
    except Exception as e:
        print(f"  (leads.json write failed: {e})")


def push_leads(sheet, leads):
    first_row = sheet.row_values(1)
    if not first_row or first_row[0] != "Date Added":
        sheet.clear()
        sheet.insert_row(SHEET_HEADERS, 1)

    existing = {row[1] for row in sheet.get_all_values()[1:] if len(row) > 1}
    today    = datetime.now().strftime("%m/%d/%Y")
    new_rows = []

    for lead in leads:
        if lead["address"] in existing:
            continue
        # Only keep distressed leads — skip clean normal listings
        if lead["score"] < 1:
            continue
        profit_display = (
            f"+${lead['profit']:,} (DEAL NOW)" if lead["profit"] > 0
            else f"-${abs(lead['profit']):,} to negotiate"
        ) if lead["profit"] != 0 else ""

        new_rows.append([
            today,
            lead["address"],
            lead["price"],
            lead["offer_at"],
            profit_display,
            lead["mao"],
            lead["price_drop"],
            lead["beds"],
            lead["baths"],
            lead["sqft"],
            lead["dom"],
            lead["signals"],
            lead["score"],
            lead["agent_phone"],
            YOUR_NUMBER,
            ("https://www.zillow.com" + lead["url"]) if lead["url"] and not lead["url"].startswith("http") else lead["url"],
            "New",
            "",
        ])

    if new_rows:
        sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    return len(new_rows)


# ---- DISPLAY -----------------------------------------------------------------

def print_call_sheet(leads):
    hot  = [l for l in leads if l["score"] >= 3]
    warm = [l for l in leads if 0 < l["score"] < 3]
    deal = [l for l in leads if l["profit"] > 0]

    W = 90
    print("\n" + "=" * W)
    print("  KBROS LEAD REPORT — Springfield MO 50-Mile Radius".center(W))
    print(f"  {datetime.now().strftime('%B %d, %Y')}   |   Your Number: {YOUR_NUMBER}".center(W))
    print("=" * W)

    stats = [
        ("Total Scraped",        len(leads)),
        ("Hot Leads (score 3+)", len(hot)),
        ("Warm Leads",           len(warm)),
        ("Deals at Asking",      len(deal)),
    ]
    print("")
    for label, val in stats:
        bar = "#" * min(val, 40)
        print(f"  {label:<24} {val:>4}  {bar}")
    print("")

    # Deals at asking price (rare gold)
    if deal:
        print("=" * W)
        print("  *** DEALS AT ASKING PRICE — CALL THESE FIRST ***".center(W))
        print("=" * W)
        _print_leads(deal[:10], show_profit=True)

    # Hot distressed leads
    if hot:
        print("-" * W)
        print("  HOT DISTRESSED LEADS (Score 3+)".center(W))
        print("-" * W)
        _print_leads(hot[:15], show_profit=True)

    # Warm leads
    if warm:
        print("-" * W)
        print("  WARM LEADS (Score 1-2) — Watch These".center(W))
        print("-" * W)
        _print_leads(warm[:10], show_profit=False)

    print("=" * W)
    print(f"  Your Number: {YOUR_NUMBER}  |  Tell sellers: 'I'm a local cash buyer, quick close, as-is'")
    print("=" * W + "\n")


def _print_leads(leads, show_profit):
    for i, l in enumerate(leads, 1):
        addr    = l["address"][:45]
        price   = l["price"][:10]
        offer   = l["offer_at"][:10] if l["offer_at"] else "N/A"
        mao     = l["mao"][:10] if l["mao"] else "N/A"
        dom     = str(l["dom"]) + "d"
        phone   = l["agent_phone"] or "visit Zillow"
        signals = l["signals"][:35] if l["signals"] else "check listing"

        print(f"\n  [{i:02d}] {addr}")
        print(f"       Asking: {price:<12} Offer At: {offer:<12} MAO: {mao:<12} DOM: {dom}")
        if show_profit and l["profit"] != 0:
            verdict = "DEAL NOW - call immediately!" if l["profit"] > 0 else f"Need ${abs(l['profit']):,} off asking"
            print(f"       Profit: {verdict}")
        print(f"       Signals: {signals}")
        print(f"       Agent:  {phone:<20} Your #: {YOUR_NUMBER}")


# ---- MAIN --------------------------------------------------------------------

def main():
    W = 90
    print("=" * W)
    print("  KBros Zillow Scraper  |  50-Mile Radius Springfield MO".center(W))
    print(f"  Running: {datetime.now().strftime('%B %d, %Y %I:%M %p')}".center(W))
    print("=" * W)

    if not os.path.exists(KEY_FILE):
        print(f"\n  [!] Missing key file: {KEY_FILE}")
        print("      Run: py scripts/restore_key.py")
        return

    # Scrape
    session  = requests.Session()
    try:
        session.get("https://www.zillow.com/", headers=BROWSER_HEADERS, timeout=15)
        time.sleep(1)
    except Exception:
        pass

    all_listings = []
    seen_ids     = set()

    print("\n  Scraping listings...\n")
    for label, url in SEARCH_URLS:
        print(f"  {label:<20}", end=" ", flush=True)
        listings  = fetch_listings(session, url)
        new_count = 0
        for l in listings:
            uid = l.get("zpid") or l.get("address", "")
            if uid not in seen_ids:
                seen_ids.add(uid)
                all_listings.append(l)
                new_count += 1
        print(f"{new_count} listings")
        time.sleep(2)

    # Score
    leads = [score_listing(l) for l in all_listings]
    leads.sort(key=lambda x: (x["profit"] > 0, x["score"], x["dom"]), reverse=True)

    # Fetch phones for top scored leads only
    top_leads = [l for l in leads if l["score"] >= 1][:50]
    if top_leads:
        print(f"\n  Fetching agent phones for top {len(top_leads)} leads...")
        for i, lead in enumerate(top_leads):
            phone = fetch_agent_phone(session, lead["url"])
            lead["agent_phone"] = phone
            marker = "+" if phone else "."
            print(f"  {marker}", end="" if (i + 1) % 20 != 0 else "\n", flush=True)
            time.sleep(1.5)
        print()

    # Display
    print_call_sheet(leads)

    # Write leads.json for React app
    write_leads_json(leads)

    # Push to sheet + format
    print("  Pushing to Google Sheets...", end=" ", flush=True)
    try:
        sheet = connect_sheet()
        added = push_leads(sheet, leads)
        print(f"{added} new leads added.")
        print("  Formatting sheet...", end=" ", flush=True)
        format_sheet(sheet)
        color_rows(sheet, leads)
        print("done.")
        print(f"  Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}\n")
    except Exception as e:
        print(f"\n  [!] Sheet error: {e}\n")


if __name__ == "__main__":
    main()
