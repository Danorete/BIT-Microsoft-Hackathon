# Contributing

Read CLAUDE.md first. It has the rules and the context behind them.

## Get running in five minutes

```bash
git clone https://github.com/Danorete/HackATL-VibeCoders
cd HackATL-VibeCoders
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app/streamlit_app.py
```

The app works without an API key in offline (Simulated) mode. For live answers, put `ANTHROPIC_API_KEY` in your own shell or in `.env`. Never commit it, and never share a key in chat or a PR.

## How we work

1. Pick a lane from docs/TEAM_LANES.md and put your name next to it.
2. Make a branch from `main` named `yourname/short-topic`. Do not push straight to `main`.
3. Keep changes small. Open a pull request early, and ask one teammate to review.
4. Tests must pass. CI runs `pytest` on every pull request.
5. Merge your own pull request once it is reviewed and green. Use squash merge to keep history short.

## Rules that cannot bend

Synthetic data only in `data/sample`. Never load data from a past employer, internship, or client, even to test. CI fails if files appear in `data/private`, `data/real`, or if a `.env` file is committed.

Label every feature Working, Simulated, or Planned, and keep the table in README.md current.

Do not invent statistics, market sizes, or prices. Anything heard goes in docs/EVIDENCE_LOG.md as a finding, and anything guessed goes there as an assumption.

If you used a new library, tool, or AI assistance for something that matters, add it to docs/DISCLOSURE.md.

## Freeze

The demo freezes Sunday 9 a.m. After that, only fix bugs in the demo path, and label anything unfinished as Planned.
