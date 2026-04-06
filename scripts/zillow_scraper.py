"""
KBros Zillow Lead Scraper — 50-Mile Radius
Scrapes distressed listings within 50 miles of Springfield MO
and pushes results to Google Sheets.

Requirements:
  py -m pip install requests gspread google-auth

Usage:
  py scripts/zillow_scraper.py

Needs: scripts/zillow-bot-key.json  (service account JSON key)
"""

import requests
import json
import time
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import math

# ─── CONFIG ───────────────────────────────────────────────────────────────────

SHEET_ID   = "18oJwsncdmlaDrT2O_q3sOoOJwfB7SdKRWLO37HWAgSo"
KEY_FILE   = os.path.join(os.path.dirname(__file__), "zillow-bot-key.json")
SHEET_TAB  = "Sheet1"

# Springfield MO center + 50-mile bounding box
CENTER_LAT  = 37.2153
CENTER_LNG  = -93.2982
RADIUS_MI   = 50

def _bounding_box(lat, lng, miles):
    lat_deg  = miles / 69.0
    lng_deg  = miles / (math.cos(math.radians(lat)) * 69.0)
    return {
        "north": round(lat + lat_deg, 4),
        "south": round(lat - lat_deg, 4),
        "east":  round(lng + lng_deg, 4),
        "west":  round(lng - lng_deg, 4),
    }

BOUNDS = _bounding_box(CENTER_LAT, CENTER_LNG, RADIUS_MI)

DISTRESS_KEYWORDS = [
    "as-is", "as is", "motivated", "must sell", "price reduced", "price drop",
    "fixer", "fixer upper", "needs work", "needs tlc", "tlc", "handyman",
    "estate sale", "trust sale", "probate", "foreclosure", "bank owned",
    "reo", "cash only", "investor special", "bring offers", "below market",
    "vacant", "abandoned", "distressed", "divorce", "relocating", "relocation",
    "fsbo", "for sale by owner", "quick close", "motivated seller",
    "inherited", "fire damage", "water damage", "foundation",
]

SHEET_HEADERS = [
    "Date Added", "Address", "Price", "Price Drop", "Beds", "Baths",
    "Sqft", "Days on Market", "Distress Signals", "Motivation Score",
    "Zestimate", "Zillow URL", "Status", "Notes"
]

# ─── ZILLOW API ────────────────────────────────────────────────────────────────

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "referer": "https://www.zillow.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

BASE_SEARCH_URL = "https://www.zillow.com/homes/for_sale/Springfield-MO/"

def _make_session():
    s = requests.Session()
    s.get(BASE_SEARCH_URL, headers=HEADERS, timeout=20)
    time.sleep(2)
    return s

def fetch_page(session, page_num):
    url = "https://www.zillow.com/async-create-search-page-state"
    payload = {
        "searchQueryState": {
            "pagination":    {"currentPage": page_num},
            "isMapVisible":  False,
            "mapBounds":     BOUNDS,
            "filterState": {
                "sort": {"value": "days"},   # newest first
                "ah":   {"value": True},      # for sale
            },
            "isListVisible": True,
            "usersSearchTerm": "Springfield, MO",
        },
        "wants": {
            "cat1": ["listResults", "mapResults"],
            "cat2": ["total"],
        },
        "requestId":      page_num,
        "isDebugRequest": False,
    }

    api_headers = {
        **HEADERS,
        "content-type": "application/json",
        "referer":       BASE_SEARCH_URL,
    }

    resp = session.put(url, headers=api_headers, json=payload, timeout=20)

    if resp.status_code == 429:
        print("  [!] Rate limited — waiting 30 seconds...")
        time.sleep(30)
        resp = session.put(url, headers=api_headers, json=payload, timeout=20)

    if resp.status_code != 200:
        print(f"  [!] HTTP {resp.status_code} on page {page_num}")
        return [], 0

    try:
        data     = resp.json()
        cat1     = data.get("cat1", {})
        results  = cat1.get("searchResults", {}).get("listResults", [])
        total    = cat1.get("searchResults", {}).get("totalResultCount", 0) or 0
        return results, total
    except Exception as e:
        print(f"  [!] Parse error page {page_num}: {e}")
        return [], 0

def scrape_all():
    print(f"\n[*] Bounding box (50-mile radius):")
    print(f"    N {BOUNDS['north']}  S {BOUNDS['south']}  E {BOUNDS['east']}  W {BOUNDS['west']}")

    session  = _make_session()
    all_raw  = []
    page     = 1
    MAX_PAGE = 20  # Zillow caps around 800 results (20 pages × 40)

    while page <= MAX_PAGE:
        print(f"  [*] Page {page}...", end=" ", flush=True)
        results, total = fetch_page(session, page)

        if not results:
            print("no results — done.")
            break

        if page == 1:
            print(f"(~{total} total listings found)")
        else:
            print(f"{len(results)} listings")

        all_raw.extend(results)

        # Stop if we've collected everything
        if len(all_raw) >= total or len(results) < 20:
            break

        page += 1
        time.sleep(3)   # be polite — avoid IP bans

    return all_raw

# ─── SCORING ──────────────────────────────────────────────────────────────────

def score_listing(listing):
    address       = listing.get("address", "N/A")
    price         = listing.get("price", "")
    beds          = listing.get("beds", "")
    baths         = listing.get("baths", "")
    sqft          = listing.get("area", "")
    dom           = listing.get("daysOnZillow", 0) or 0
    zestimate     = listing.get("zestimate", "")
    price_drop    = listing.get("priceReduction", "")

    detail_url = listing.get("detailUrl", "")
    if detail_url and not detail_url.startswith("http"):
        detail_url = "https://www.zillow.com" + detail_url

    # Build a text blob to search for distress keywords
    var_data = listing.get("variableData", {}) or {}
    text_blob = " ".join([
        str(listing.get("statusText", "")),
        str(var_data.get("text", "")),
        str(listing.get("listingSubType", "")),
    ]).lower()

    signals = []
    for kw in DISTRESS_KEYWORDS:
        if kw in text_blob:
            signals.append(kw)

    score = len(signals)

    if price_drop:
        score += 2
        signals.insert(0, f"price reduced ({price_drop})")

    if dom >= 90:
        score += 3
        signals.append(f"high DOM ({dom}d)")
    elif dom >= 60:
        score += 2
        signals.append(f"high DOM ({dom}d)")
    elif dom >= 30:
        score += 1

    return {
        "address":    address,
        "price":      price,
        "price_drop": price_drop,
        "beds":       beds,
        "baths":      baths,
        "sqft":       sqft,
        "dom":        dom,
        "signals":    ", ".join(signals) if signals else "",
        "score":      score,
        "zestimate":  zestimate,
        "url":        detail_url,
    }

# ─── GOOGLE SHEETS ─────────────────────────────────────────────────────────────

def connect_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds  = Credentials.from_service_account_file(KEY_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_TAB)

def push_leads(sheet, leads):
    first_row = sheet.row_values(1)
    if not first_row or first_row[0] != "Date Added":
        sheet.insert_row(SHEET_HEADERS, 1)

    existing  = {row[1] for row in sheet.get_all_values()[1:] if row}
    today     = datetime.now().strftime("%m/%d/%Y")
    new_rows  = []

    for lead in leads:
        if lead["address"] in existing:
            continue
        new_rows.append([
            today,
            lead["address"],
            lead["price"],
            lead["price_drop"],
            lead["beds"],
            lead["baths"],
            lead["sqft"],
            lead["dom"],
            lead["signals"],
            lead["score"],
            lead["zestimate"],
            lead["url"],
            "New",
            "",
        ])

    if new_rows:
        sheet.append_rows(new_rows, value_input_option="USER_ENTERED")

    return len(new_rows)

# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  KBros Zillow Scraper — 50-Mile Radius Springfield MO")
    print("=" * 55)

    if not os.path.exists(KEY_FILE):
        print(f"\n[!] Missing key file: {KEY_FILE}")
        print("    Download from GCP Console:")
        print("    IAM & Admin → Service Accounts → zillow-bot → Keys → Add Key → JSON")
        print("    Save as: scripts/zillow-bot-key.json")
        return

    # 1. Scrape
    raw_listings = scrape_all()
    print(f"\n[*] Total raw listings fetched: {len(raw_listings)}")

    # 2. Score
    leads = [score_listing(l) for l in raw_listings]
    leads.sort(key=lambda x: x["score"], reverse=True)

    distressed = [l for l in leads if l["score"] > 0]
    print(f"[*] Leads with distress signals: {len(distressed)}")

    # Preview top 10
    print("\n── Top Leads ──────────────────────────────────────────")
    for l in leads[:10]:
        print(f"  Score {l['score']:2d} | {l['address'][:40]:<40} | {l['price']} | DOM: {l['dom']}")

    # 3. Push to sheet
    print("\n[*] Connecting to Google Sheets...")
    try:
        sheet  = connect_sheet()
        added  = push_leads(sheet, leads)
        print(f"[✓] Done — {added} new leads added.")
        print(f"    https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    except Exception as e:
        print(f"[!] Sheet error: {e}")

if __name__ == "__main__":
    main()
