# KYROS Global Brain — Always Loaded

> This file lives at ~/.claude/CLAUDE.md and loads in EVERY Claude Code session regardless of directory.
> Full project context: ~/Desktop/my-project/CLAUDE.md
> Memory notes: ~/Desktop/my-project/memory/MEMORY.md
> Session logs: ~/Desktop/my-project/logs/

---

## Who I Am
- Name: Vadim (Windows username: Vad)
- Business: K Brothers Renovation LLC — real estate wholesaling
- Location: Springfield, MO (zip codes 65802, 65803)
- GitHub: https://github.com/fakevadimusa-ui/-my-project
- Git identity: name=Vadim, email=Fakevadimusa@gmail.com

## If I Say "I Lost Everything" — Run This Recovery
```bash
cd ~/Desktop
git clone https://github.com/fakevadimusa-ui/-my-project.git my-project
cd my-project
cat CLAUDE.md
cat memory/MEMORY.md
ls logs/
```
Everything comes back from GitHub. That's the source of truth.

## Active Projects
- `~/Desktop/my-project` — main repo (CLAUDE.md, memory, logs, scripts)
- `~/Desktop/kbros-app` — React app (KBros Command Center, runs on localhost:5173)
  - Start it: `cd ~/Desktop/kbros-app && npm run dev`

## Current Business Stage
- KYROS Phase 1 (Super Memory) — ACTIVE, just set up
- Wholesaling Phase 1 (Foundation) — IN PROGRESS
- No deals closed yet, building the machine

## MAO Formula
ARV × 0.70 − estimated repairs − assignment fee = Max Offer

## Coding Rules
- React + inline styles, no Tailwind
- localStorage (never window.storage)
- Plain JavaScript, no TypeScript
- Inter or DM Sans font
- Single-file components when possible

## Session Start Checklist
1. `cd ~/Desktop/my-project && git pull`
2. Read CLAUDE.md + memory/MEMORY.md
3. Check latest log in logs/

## Session End Checklist
1. `git add . && git commit -m "brief note" && git push`
2. Hook auto-logs to logs/YYYY-MM-DD.md
