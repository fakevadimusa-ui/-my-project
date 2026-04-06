# KYROS Recovery Guide
> If everything dies — new PC, fresh install, wiped drive — run this top to bottom.

## Step 1 — Install tools
```bash
# Install Node.js first from nodejs.org, then:
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
git clone https://github.com/fakevadimusa-ui/-my-project.git my-project
```

## Step 4 — Restore global Claude brain
```bash
cp ~/Desktop/my-project/.claude-global/CLAUDE.md ~/.claude/CLAUDE.md
```

## Step 5 — Restore React app
```bash
cd ~/Desktop
# kbros-app is a separate folder — re-clone or rebuild if lost
# All source code is in the GitHub repo under kbros-app/ if moved there
```

## Step 6 — Verify memory
```bash
cat ~/Desktop/my-project/CLAUDE.md
cat ~/Desktop/my-project/memory/MEMORY.md
ls ~/Desktop/my-project/logs/
```

## You're back. Claude knows everything again.
