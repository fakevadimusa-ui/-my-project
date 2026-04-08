"""
KBros Lead Cleaner + Refresher
- Moves weak/non-distressed leads from Sheet1 to an Archive tab
- Then runs the Zillow scraper to pull in fresh distressed replacements

Weak = DOM < 30 AND score 0 AND no price drop AND no notes written
Never deletes — only archives. Nothing is permanently lost.

Usage:
  py scripts/clean_and_refresh.py
"""

import os
import sys
import re
import time
import gspread
from google.oauth2.service_account import Credentials

KEY_FILE  = os.path.join(os.path.dirname(__file__), "zillow-bot-key.json")
SHEET_ID  = "18oJwsncdmlaDrT2O_q3sOoOJwfB7SdKRWLO37HWAgSo"
SCOPES    = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

DISTRESS_WORDS = [
    "as-is","as is","fixer","estate","probate","foreclosure","vacant","motivated",
    "needs","tlc","divorce","inherited","cash only","fire","water","reo","bank owned",
    "abandoned","distressed","handyman","reduced","auction","pre-foreclosure","fsbo",
    "must sell","below market","price cut","investor","relocat"
]

def is_weak(row, headers):
    """Return True if this lead has no real distress signals."""
    def get(col):
        cols = [c.lower() for c in headers]
        for name in ([col] if isinstance(col, str) else col):
            try:
                i = cols.index(name.lower())
                return str(row[i]).strip() if i < len(row) else ""
            except ValueError:
                pass
        return ""

    notes      = get("notes")
    price_drop = get(["price drop","price reduction"])
    dom_raw    = get("days on market")
    score_raw  = get(["score","motivation score"])
    signals    = get("distress signals").lower()
    status     = get("status").lower()

    # Always keep leads already worked
    if notes.strip():
        return False

    # Always keep leads with hot status
    if any(w in status for w in ["hot","callback","contract","signing"]):
        return False

    dom   = int(re.sub(r"\D","",dom_raw) or 0)
    score = int(re.sub(r"\D","",score_raw) or 0)

    # Keep if price was dropped (seller is moving)
    if price_drop.strip():
        return False

    # Keep if any distress keyword appears
    if any(w in signals for w in DISTRESS_WORDS):
        return False

    # Keep if DOM is meaningful (sitting on market)
    if dom >= 45:
        return False

    # Keep if score is decent
    if score >= 3:
        return False

    # Everything else = weak
    return True


def get_or_create_archive(spreadsheet):
    """Get the Archive tab, create it if it doesn't exist."""
    try:
        return spreadsheet.worksheet("Archive")
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title="Archive", rows=2000, cols=30)
        print("  Created Archive tab.")
        return ws


def main():
    if not os.path.exists(KEY_FILE):
        print(f"[!] Missing key: {KEY_FILE}\n    Run: py scripts/restore_key.py")
        return

    print("=" * 60)
    print("  KBros Lead Cleaner + Refresher")
    print("=" * 60)

    creds       = Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    client      = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet1      = spreadsheet.worksheet("Sheet1")
    archive     = get_or_create_archive(spreadsheet)

    all_values = sheet1.get_all_values()
    if not all_values:
        print("Sheet is empty.")
        return

    headers   = all_values[0]
    data_rows = all_values[1:]

    # Copy headers to Archive if empty
    if not archive.get_all_values():
        archive.insert_row(headers, 1)

    weak_rows   = []
    strong_rows = []
    weak_indices = []  # 1-based row numbers in sheet1

    for i, row in enumerate(data_rows, start=2):
        if not any(row):  # skip blank rows
            continue
        if is_weak(row, headers):
            weak_rows.append(row)
            weak_indices.append(i)
        else:
            strong_rows.append(row)

    print(f"\n  Found {len(data_rows)} leads total")
    print(f"  Weak / non-distressed: {len(weak_rows)}")
    print(f"  Strong / keeping:      {len(strong_rows)}")

    if not weak_rows:
        print("\n  Nothing to clean — all leads look distressed. Good sheet!")
        run_scraper()
        return

    print(f"\n  Moving {len(weak_rows)} weak leads to Archive tab...")

    # Append weak rows to archive in batches
    BATCH = 50
    for i in range(0, len(weak_rows), BATCH):
        archive.append_rows(weak_rows[i:i+BATCH], value_input_option="USER_ENTERED")
        time.sleep(1)

    # Delete from Sheet1 in reverse order (so indices stay valid)
    print(f"  Removing from Sheet1...")
    for idx in reversed(weak_indices):
        sheet1.delete_rows(idx)
        time.sleep(0.3)  # avoid API rate limit

    print(f"\n  Done. {len(weak_rows)} leads archived, {len(strong_rows)} remain in Sheet1.")
    print(f"  Archive tab has your history if you ever need it back.\n")

    run_scraper()


def run_scraper():
    print("  Running Zillow scraper to pull fresh distressed leads...")
    import subprocess
    scraper = os.path.join(os.path.dirname(__file__), "zillow_scraper.py")
    result  = subprocess.run([sys.executable, scraper], capture_output=False)
    if result.returncode == 0:
        print("\n  Fresh leads added. Sync your dashboard to see them.")
    else:
        print("\n  [!] Scraper exited with an error — check output above.")


if __name__ == "__main__":
    main()
