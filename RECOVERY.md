# KYROS Recovery Guide
> If everything dies — new PC, fresh install, wiped drive — run this top to bottom.

---

## Step 1 — Install tools
```bash
# Install Node.js from nodejs.org (includes npm)
# Install Python from python.org (3.12+)
npm install -g @anthropic-ai/claude-code
```

## Step 2 — Restore Git identity
```bash
git config --global user.name "Vadim"
git config --global user.email "Fakevadimusa@gmail.com"
```

## Step 3 — Clone the repo
```bash
cd ~/Desktop
git clone https://github.com/fakevadimusa-ui/-my-project.git
```

## Step 4 — Restore global Claude brain
```bash
cp ~/Desktop/-my-project/.claude-global/CLAUDE.md ~/.claude/CLAUDE.md
```

## Step 5 — Launch KBros Command Center (React App)
```bash
cd ~/Desktop/-my-project
npm install
npm run dev
# Open browser: http://localhost:5173
```

## Step 6 — Run Zillow Scraper
```bash
# Install Python dependencies (one time)
py -m pip install requests gspread google-auth

# Put your service account key here:
# ~/Desktop/-my-project/scripts/zillow-bot-key.json
# (Download from GCP Console → IAM → Service Accounts → zillow-bot → Keys → JSON)

# Run the scraper
cd ~/Desktop/-my-project
py scripts/zillow_scraper.py

# Results go to:
# https://docs.google.com/spreadsheets/d/18oJwsncdmlaDrT2O_q3sOoOJwfB7SdKRWLO37HWAgSo
```

## Step 7 — Verify memory
```bash
cat ~/Desktop/-my-project/CLAUDE.md
cat ~/Desktop/-my-project/memory/MEMORY.md
ls ~/Desktop/-my-project/logs/
```

## You're back. Claude knows everything again.
