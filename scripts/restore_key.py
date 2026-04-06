"""
Run this if zillow-bot-key.json is missing (new PC, wiped drive, etc.)
Paste the JSON key content when prompted and it saves it to the right place.

Usage: py scripts/restore_key.py
"""
import json
import os

KEY_PATH = os.path.join(os.path.dirname(__file__), "zillow-bot-key.json")

if os.path.exists(KEY_PATH):
    print(f"[✓] Key already exists at {KEY_PATH}")
else:
    print("Paste your zillow-bot service account JSON key below.")
    print("(Paste everything including the curly braces, then press Enter twice)\n")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    raw = "\n".join(lines).strip()
    try:
        data = json.loads(raw)
        with open(KEY_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n[✓] Key saved to {KEY_PATH}")
    except json.JSONDecodeError as e:
        print(f"\n[!] Invalid JSON: {e}")
        print("    Make sure you pasted the full key including {{ and }}")
