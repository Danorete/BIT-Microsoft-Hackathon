# Onboarding Copilot

HackATL 2026, theme: Designing the World After AI.

## The person

A new hire in week one. They are given access to hundreds of tables or a large codebase, no map, and no idea what to ask. AI tools could help, but they answer confidently without knowing the company's data, and the new hire does not yet know enough to catch a wrong answer or to notice when they are about to paste something sensitive into an AI tool.

## What we are building

An onboarding assistant that does one thing end to end: a new hire points it at a dataset and gets a day one orientation, then asks questions and gets answers they can verify.

1. Orientation: what tables exist, how they connect, which fields are sensitive, and good first questions to ask.
2. Safe questions: sensitive values in a question are caught and removed before anything is sent to a model.
3. Verifiable answers: every claim cites the table and column it came from, so the new hire can check it.

## Status of each feature

Judges are asked to tell these apart, so we label everything. Update this table as the build changes.

| Feature | Status | Notes |
| --- | --- | --- |
| Dataset profiler (tables, columns, joins) | Working | Reads any folder of CSV files |
| Sensitive field detection | Working | Rule based and auditable, no model involved |
| Question redaction before sending | Working | Emails, SSNs, phones, cards, API keys |
| Cited answers from a model | Working with an API key | Offline keyword mode otherwise (Simulated) |
| Source view (open a cited table or column, flags citations not in the data) | Working | Sample values hidden for sensitive columns |
| Manager view | Planned | Mockup only |
| Real company data connectors | Planned | Demo uses synthetic data only |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add ANTHROPIC_API_KEY for live answers
python scripts/make_sample_data.py   # only if data/sample is missing
streamlit run app/streamlit_app.py
pytest
```

Load the key with `export ANTHROPIC_API_KEY=...` or your preferred env loader. Never commit it.

## Rules for this repo

Only synthetic data goes in `data/sample`. Do not load data from any past employer, internship, or client, even for testing. Real data goes in `data/private`, which git ignores.

## Where to look

| File | Purpose |
| --- | --- |
| CONTRIBUTING.md | Setup and how we work together |
| docs/TEAM_LANES.md | Who owns what, mapped to the judging rubric |
| docs/EVIDENCE_LOG.md | Findings versus assumptions, interview script |
| docs/PITCH_OUTLINE.md | Five minute pitch with demo inside the clock |
| docs/DISCLOSURE.md | Built at HackATL versus started with |
