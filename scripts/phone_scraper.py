"""
KBros Phone Scraper
Reads Zillow URLs from the existing sheet → scrapes phone number from each listing → writes to new 'Phone' column.

Usage:
  cd C:\\Users\\vu1025070\\-my-project
  py scripts/phone_scraper.py

Resumes where it left off — skips rows that already have a phone.
"""

import re
import time
import random
import os
import requests
import gspread
from google.oauth2.service_account import Credentials

# ---- CONFIG ------------------------------------------------------------------

SHEET_ID  = "18oJwsncdmlaDrT2O_q3sOoOJwfB7SdKRWLO37HWAgSo"
KEY_FILE  = os.path.join(os.path.dirname(__file__), "zillow-bot-key.json")
SHEET_TAB = "Sheet1"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

BROWSER_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "referer": "https://www.zillow.com/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "upgrade-insecure-requests": "1",
}

# ---- PHONE SCRAPING ----------------------------------------------------------

def scrape_phone(session, url):
    """Hit the Zillow listing page and extract any phone number found."""
    if not url or not url.startswith("http"):
        return "No URL"
    try:
        resp = session.get(url, headers=BROWSER_HEADERS, timeout=18)
        if resp.status_code == 403:
            return "Blocked (403)"
        if resp.status_code != 200:
            return f"HTTP {resp.status_code}"

        html = resp.text

        # Method 1: tel: links (most reliable — FSBO and agent direct lines)
        tel = re.findall(r'href=["\']tel:([+\d\s\-\(\).]{7,})["\']', html)
        if tel:
            return fmt_phone(tel[0])

        # Method 2: JSON fields — "phoneNumber", "phone", "agentPhone", etc.
        json_patterns = [
            r'"phoneNumber"\s*:\s*"([^"]{7,20})"',
            r'"phone"\s*:\s*"([^"]{7,20})"',
            r'"agentPhone"\s*:\s*"([^"]{7,20})"',
            r'"contactPhone"\s*:\s*"([^"]{7,20})"',
            r'"sellerPhone"\s*:\s*"([^"]{7,20})"',
            r'"listingPhone"\s*:\s*"([^"]{7,20})"',
        ]
        for pat in json_patterns:
            m = re.search(pat, html)
            if m:
                candidate = m.group(1).strip()
                if len(re.sub(r"\D", "", candidate)) >= 10:
                    return fmt_phone(candidate)

        # Method 3: Raw US phone patterns in visible text
        raw = re.findall(r'\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}', html)
        if raw:
            return fmt_phone(raw[0])

        return "No phone found"

    except requests.exceptions.Timeout:
        return "Timeout"
    except Exception as e:
        return f"Error: {str(e)[:35]}"


def fmt_phone(raw):
    """Normalize any phone string to (XXX) XXX-XXXX format."""
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return raw.strip()


# ---- GOOGLE SHEETS -----------------------------------------------------------

def connect_sheet():
    creds  = Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_TAB)


def find_col(headers, names):
    """Return 0-based index of the first matching header name (case-insensitive)."""
    for name in names:
        for i, h in enumerate(headers):
            if name in h.lower():
                return i
    return None


# ---- MAIN --------------------------------------------------------------------

def main(new_only=False, limit=50):
    print("=" * 65)
    print("  KBros Phone Scraper - Zillow URL -> Phone Column")
    print("=" * 65)

    if not os.path.exists(KEY_FILE):
        print(f"\n[!] Missing key: {KEY_FILE}")
        print("    Run: py scripts/restore_key.py")
        return

    print("\nConnecting to Google Sheet...", end=" ", flush=True)
    sheet      = connect_sheet()
    all_values = sheet.get_all_values()
    headers    = [h.strip().lower() for h in all_values[0]]
    print("connected.")

    # Find Zillow URL column
    zillow_col = find_col(headers, ["zillow url", "zillow", "url"])
    if zillow_col is None:
        print("[!] Could not find a Zillow URL column. Aborting.")
        return

    # Find or create Phone column
    phone_col = find_col(headers, ["phone", "agent phone", "contact phone"])
    if phone_col is None:
        # Add it right after the last column
        phone_col = len(all_values[0])
        sheet.update_cell(1, phone_col + 1, "Phone")
        print(f"Created 'Phone' column at column {phone_col + 1} ({chr(64 + phone_col + 1)}).")
    else:
        print(f"Found existing Phone column at column {phone_col + 1}.")

    # Find Notes column
    notes_col = find_col(headers, ["notes"])
    if notes_col is None:
        print("[!] Could not find a Notes column. Aborting.")
        return

    # Count workload
    rows_to_do = []
    skipped_worked = 0
    skipped_has_phone = 0

    data_rows = list(enumerate(all_values[1:], start=2))
    if new_only:
        data_rows = list(reversed(data_rows))  # scan newest first

    for row_idx, row in data_rows:
        url   = row[zillow_col].strip() if zillow_col < len(row) else ""
        notes = row[notes_col].strip()  if notes_col  < len(row) else ""
        phone = row[phone_col].strip()  if phone_col  < len(row) else ""

        if not url.startswith("http"):
            continue
        if notes:
            skipped_worked += 1
            continue
        if phone and phone not in ("No phone found", "No URL", ""):
            skipped_has_phone += 1
            continue
        rows_to_do.append((row_idx, url, row[1] if len(row) > 1 else ""))
        if new_only and len(rows_to_do) >= limit:
            break

    print(f"  Skipped {skipped_worked} leads (Notes filled = already worked)")
    print(f"  Skipped {skipped_has_phone} leads (phone already scraped)")

    print(f"\n{len(rows_to_do)} listings to scrape ({len(all_values) - 1 - len(rows_to_do)} already have phone or no URL).\n")

    if not rows_to_do:
        print("Nothing to do — all rows already scraped!")
        return

    # Warm up cookies
    session = requests.Session()
    try:
        session.get("https://www.zillow.com/", headers=BROWSER_HEADERS, timeout=15)
        time.sleep(2)
    except Exception:
        pass

    found  = 0
    missed = 0
    errors = 0

    for i, (row_idx, url, address) in enumerate(rows_to_do, start=1):
        short_addr = address[:48].ljust(48)
        print(f"[{i:>4}/{len(rows_to_do)}] {short_addr}", end=" -> ", flush=True)

        phone = scrape_phone(session, url)
        print(phone)

        sheet.update_cell(row_idx, phone_col + 1, phone)

        if re.search(r"\(\d{3}\)", phone):
            found += 1
        elif "No phone" in phone or "No URL" in phone:
            missed += 1
        else:
            errors += 1

        # Polite delays — avoid getting IP-banned
        if i % 25 == 0:
            pause = random.randint(25, 40)
            print(f"\n  --- Pausing {pause}s to stay under Zillow radar ({i}/{len(rows_to_do)} done) ---\n")
            time.sleep(pause)
        else:
            time.sleep(random.uniform(3.5, 6.5))

    print("\n" + "=" * 65)
    print(f"  Done!  Found: {found}  |  Not listed: {missed}  |  Errors/Blocked: {errors}")
    print(f"  Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    print("=" * 65)


if __name__ == "__main__":
    import sys
    new_only = "--new" in sys.argv
    main(new_only=new_only, limit=50)
