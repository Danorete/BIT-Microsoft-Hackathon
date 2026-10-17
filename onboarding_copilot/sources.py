"""Turn [table.column] citations in an answer into records the new hire can check.

A citation that does not match the loaded schema is kept and marked unverified, so a
made up source is visible instead of silently dropped.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .profiler import TableProfile

_BRACKET = re.compile(r"\[([^\[\]]+)\]")
_REF = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\.([A-Za-z_][A-Za-z0-9_]*))?$")


@dataclass
class Source:
    ref: str  # the citation as written, e.g. "orders.customer_id"
    table: str
    column: str | None
    found: bool
    rows: int | None = None
    dtype: str | None = None
    null_pct: float | None = None
    distinct: int | None = None
    samples: list[str] | None = None  # None when masked or not applicable
    sensitive_kinds: list[str] | None = None
    columns: list[str] | None = None  # for table level citations


def extract_citations(text: str) -> list[str]:
    """Return unique citation refs in order of first appearance."""
    refs: list[str] = []
    for inner in _BRACKET.findall(text):
        for part in re.split(r"[,;]\s*", inner):
            part = part.strip()
            if _REF.match(part) and part not in refs:
                refs.append(part)
    return refs


def resolve_sources(text: str, profiles: dict[str, TableProfile]) -> list[Source]:
    sources: list[Source] = []
    for ref in extract_citations(text):
        table_name, col_name = _REF.match(ref).groups()
        table = profiles.get(table_name)
        if table is None:
            # A bare word in brackets (e.g. [masked]) is not a citation; only dotted refs count.
            if col_name is not None:
                sources.append(Source(ref, table_name, col_name, found=False))
            continue
        if col_name is None:
            sources.append(
                Source(ref, table_name, None, True, rows=table.rows, columns=[c.name for c in table.columns])
            )
            continue
        col = table.column(col_name)
        if col is None:
            sources.append(Source(ref, table_name, col_name, found=False))
            continue
        sources.append(
            Source(
                ref,
                table_name,
                col_name,
                True,
                rows=table.rows,
                dtype=col.dtype,
                null_pct=col.null_pct,
                distinct=col.distinct,
                samples=None if col.sensitive_kinds else col.samples,
                sensitive_kinds=col.sensitive_kinds or None,
            )
        )
    return sources
