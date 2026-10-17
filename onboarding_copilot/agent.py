"""The question answering agent.

Safety design, in order:
1. Scan the new hire's question for sensitive values and redact them before anything leaves the app.
2. Send the model only the schema and masked samples, never raw rows of sensitive columns.
3. Require every claim to cite [table.column] so the new hire can check it.
4. If no API key is set, fall back to an offline keyword answer so the demo never breaks.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from .profiler import TableProfile
from .sensitivity import Finding, redact, scan_text

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

SYSTEM_PROMPT = """You are an onboarding assistant for a new hire who has just been given access to a company's data.
Rules:
1. Answer only from the schema context provided. If the context does not contain the answer, say so and suggest what to ask and who might know.
2. Cite every claim in the form [table.column] or [table]. Never state a fact without a citation.
3. Never ask for, repeat, or guess sensitive values. If the question needs a sensitive column, say so and suggest an aggregate or masked alternative.
4. Be plain and short. The reader is new and does not know the company's vocabulary yet.
5. Mark anything you are inferring from column names as an assumption."""


@dataclass
class Answer:
    text: str
    mode: str  # "live" when the model answered, "offline" when the keyword fallback answered
    flags: list[Finding] = field(default_factory=list)
    redacted_question: str = ""


def build_context(
    profiles: dict[str, TableProfile],
    relationships: list[tuple[str, str, str]],
) -> str:
    """Describe the data for the model. Sensitive columns get masked samples."""
    lines: list[str] = []
    for table in profiles.values():
        lines.append(f"TABLE {table.name} ({table.rows} rows)")
        for col in table.columns:
            samples = "[masked]" if col.sensitive_kinds else ", ".join(col.samples)
            note = f" SENSITIVE({'/'.join(col.sensitive_kinds)})" if col.sensitive_kinds else ""
            lines.append(
                f"  {table.name}.{col.name} type={col.dtype} nulls={col.null_pct}% "
                f"distinct={col.distinct} samples=[{samples}]{note}"
            )
    for a, b, col in relationships:
        lines.append(f"LIKELY JOIN {a}.{col} = {b}.{col}")
    return "\n".join(lines)


STOPWORDS = {
    "what", "which", "where", "when", "how", "the", "this", "that", "with", "from", "into",
    "and", "are", "for", "does", "have", "has", "can", "you", "your", "about", "there",
    "removed", "column", "table", "data", "mean", "means",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    stems = {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words}
    return {w for w in stems if w not in STOPWORDS and len(w) > 1}


def _offline_answer(question: str, profiles: dict[str, TableProfile]) -> str:
    """Keyword fallback. A column name match scores 2, a table name match scores 1."""
    wanted = _tokens(question)
    scored: list[tuple[int, str]] = []
    for table in profiles.values():
        table_match = bool(_tokens(table.name.replace("_", " ")) & wanted)
        for col in table.columns:
            col_match = bool(_tokens(col.name.replace("_", " ")) & wanted)
            score = (2 if col_match else 0) + (1 if table_match else 0)
            if score:
                tag = " (sensitive, ask the data owner before using it)" if col.sensitive_kinds else ""
                scored.append(
                    (score, f"[{table.name}.{col.name}] type {col.dtype}, {col.distinct} distinct values{tag}")
                )
    if not scored:
        return (
            "I could not match your question to any table or column. "
            "Try naming a table or a field, or ask a teammate who owns this data."
        )
    scored.sort(key=lambda item: -item[0])
    return "Offline mode (no model connected). Closest matches I can see:\n" + "\n".join(
        line for _, line in scored[:6]
    )


def answer_question(
    question: str,
    profiles: dict[str, TableProfile],
    relationships: list[tuple[str, str, str]],
    client=None,
    model: str = DEFAULT_MODEL,
) -> Answer:
    flags = scan_text(question)
    safe_question = redact(question) if flags else question

    if client is None and os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        client = anthropic.Anthropic()

    if client is None:
        return Answer(_offline_answer(safe_question, profiles), "offline", flags, safe_question)

    context = build_context(profiles, relationships)
    response = client.messages.create(
        model=model,
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Schema context:\n{context}\n\nQuestion: {safe_question}"}
        ],
    )
    text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    return Answer(text, "live", flags, safe_question)
