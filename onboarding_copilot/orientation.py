"""Build the day one orientation: a map of the data, what is sensitive, and what to ask first."""
from __future__ import annotations

from dataclasses import dataclass

from .profiler import TableProfile


@dataclass
class Orientation:
    tables: list[dict]
    relationships: list[tuple[str, str, str]]
    sensitive_fields: list[tuple[str, str, list[str]]]
    starter_questions: list[str]


def build_orientation(
    profiles: dict[str, TableProfile],
    relationships: list[tuple[str, str, str]],
    max_questions: int = 6,
) -> Orientation:
    tables = []
    sensitive_fields: list[tuple[str, str, list[str]]] = []
    for table in profiles.values():
        id_cols = [c.name for c in table.columns if c.name.endswith("_id")]
        tables.append(
            {
                "table": table.name,
                "rows": table.rows,
                "columns": len(table.columns),
                "id_columns": id_cols,
            }
        )
        for col in table.columns:
            if col.sensitive_kinds:
                sensitive_fields.append((table.name, col.name, col.sensitive_kinds))

    questions: list[str] = []
    for table in profiles.values():
        questions.append(
            f"What does one row in {table.name} represent, and which column identifies it?"
        )
    for a, b, col in relationships:
        questions.append(f"How do {a} and {b} connect through {col}?")
    if sensitive_fields:
        questions.append(
            "Which columns are sensitive, and what am I allowed to do with them?"
        )
    return Orientation(
        tables=tables,
        relationships=relationships,
        sensitive_fields=sensitive_fields,
        starter_questions=questions[:max_questions],
    )
