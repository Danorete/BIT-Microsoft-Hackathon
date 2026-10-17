# CLAUDE.md: project context for Onboarding Copilot

Read this first. It summarizes the planning conversation that produced this repo, so you can keep building without re-asking what was already decided.

## The event

HackATL 2026, Oct 16 to 18, hosted by Emory, Goizueta CEI, and EEVM. Theme: Designing the World After AI. The challenge: choose a person, community, or organization whose needs have changed or remain unmet in a world transformed by AI, then build a venture for them. Judges say "begin with a person." AI inside the product is optional. A meaningful theme connection is required. The test judges use: what changed because of AI, and how does that shape the solution?

Schedule: team registration was due online Friday 10:30 p.m. Saturday is build day, with a mentor round table 11 a.m. to 1 p.m. Sunday: pitch prep 9 to 10 a.m., preliminary pitches 10 a.m. to noon, finalists announced 1:30 p.m., final pitches 2 to 3 p.m., closing 4 to 5 p.m.

## How we are judged

100 points across 20 criteria, each scored 1 to 5.

| Category | Points | Criteria |
| --- | --- | --- |
| Problem and Impact | 25 | Problem Definition, User Understanding, Evidence of Need, Theme Relevance, Meaningful User Impact |
| Innovation and Solution | 15 | Original Contribution, Advantage over Alternatives, Thoughtful Approach |
| Prototype and Execution | 25 | Core Functionality, Problem Solution Fit, Build Quality and Appropriate Technology, Usability and Accessibility, Testing and Limitations |
| Business and Scale | 25 | Market or Beneficiary Sizing, Revenue or Funding Model, Costs and Sustainability, Adoption and First Pilot, Roadmap and Scale |
| Presentation and Pitch | 10 | Clear Story and Evidence, Q and A and Assumptions |

Tiebreaker: Prototype and Execution first, then Business and Scale. Complexity alone earns no bonus. Delivered value does.

Pitch format: preliminary is 5 minutes of pitch plus demo and 4 minutes of Q and A. Final is 8 plus 6. The demo counts inside pitch time. Judges are told to favor clarity and credible answers over energy or polish. In Q and A, "we don't know yet, and here is how we would find out" is a strong answer.

## Rules that affect every change

Originality: all competition specific work starts at kickoff. Existing tools and libraries are allowed with disclosure. Prebuilt team projects and previously submitted ventures are ineligible. Keep docs/DISCLOSURE.md accurate. Do not copy in code from earlier personal or class projects.

Honest labeling: every feature in the demo and slides is labeled Working, Simulated, or Planned. Judges are asked to tell these apart. Keep the status table in README.md current.

Data: demo data is synthetic only. Never load real data from any past employer, internship, or client, even for testing. Real data would go in data/private, which git ignores. Never commit keys or .env.

Evidence: keep findings (heard, saw, measured) separate from assumptions in docs/EVIDENCE_LOG.md. Do not invent statistics, market sizes, or prices. Cite current sources for any number, and verify it first.

## How the idea evolved

The team started with a security training tool: learners write prompts for coding tasks, see the scanner results on the AI generated code, and get scored on how much security context the prompt carried. Mentor feedback on Saturday reshaped it. The mentor advised focusing on the pain point of a new hire dropped into a large company dataset or codebase they cannot yet understand, and building an agent that helps them grasp it and ask accurate, safe questions. This matches the team's own internship experiences. The team agreed to pivot. The security idea survives as the differentiator: safe use means catching sensitive data before it leaves and making every answer verifiable.

Earlier concerns from teammates, and the answers we settled on:

It is not an "AI on top of an AI" gimmick. The safety checks are deterministic rules, so a manager can audit why something was flagged. The model only answers questions.

Why would a company buy it rather than build in house? Larger companies with mature security teams may build their own, so they are not the first target. First targets are smaller employers and fast growing teams that onboard junior hires without a training team. Upkeep, cross company benchmarks, and speed are the reasons to buy. This is an assumption until interviews support it.

## The product

Person: a new hire in week one, handed hundreds of tables or a large codebase with no map and no idea what to ask.

Core action, end to end: point the app at a dataset, get a day one orientation (tables, joins, sensitive fields, first questions), then ask a question and get an answer with citations to the table and column, with a warning if sensitive values were in the question.

One sentence pitch: "We're building an onboarding assistant that helps a new hire make sense of a company's data or code on day one, answering with sources and flagging sensitive information, and employers buy it to get new hires productive faster and safer."

Venture model draft: the user is the new hire. The buyer is the employer onboarding junior hires. Costs include API and hosting per new hire, so token usage feeds the unit economics slide. Sizing must be bottom up (reachable employers or cohorts times seats times price) with cited sources. First pilot idea: one named cohort for about four weeks, measured by time to first useful question and sensitive data mistakes. Mark it hypothetical until someone agrees.

## What exists in the repo

onboarding_copilot/profiler.py reads CSVs and describes tables, columns, and likely joins. sensitivity.py holds the rule based column and text detection plus redaction. orientation.py builds the day one map and starter questions. agent.py redacts the question, sends only schema and masked samples to the model, requires [table.column] citations, and falls back to an offline keyword mode without an API key. app/streamlit_app.py has three tabs: Orientation (Working), Ask (Working with a key, Simulated without), Manager view (Planned mockup). scripts/make_sample_data.py regenerates the synthetic dataset. tests/test_core.py has 7 passing tests. Run pytest from the repo root.

The model defaults to claude-sonnet-5-5 and can be overridden with ANTHROPIC_MODEL. Set ANTHROPIC_API_KEY for live answers.

## Suggested next steps, in rubric order

1. Make the core demo path rock solid on the sample data, and test it with someone who did not build it (Core Functionality, Usability and Accessibility, Testing and Limitations).
2. Add a source view so a new hire can open the cited table and column from an answer (Problem Solution Fit, Advantage over Alternatives).
3. Write a short, honest limitations list: rule based detection misses things, answers can still be wrong, the manager view is a mockup.
4. Support a second kind of input, such as a small code repository, only if the first path is finished. Otherwise list it as Planned.
5. Support the business lane with a cost per new hire estimate from real token counts from our own test runs.
6. Rehearse the demo inside the 5 minute clock. Freeze the demo before Sunday 9 a.m.

## Working style for the team lead

Write prose and avoid dashes as punctuation in documents and chat replies. Keep replies short and concrete. Say plainly when something is not done or not verified. Ask before making decisions that cannot be undone.
