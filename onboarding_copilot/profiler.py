"""Turn a folder of CSV files into a plain description of what data exists."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .sensitivity import classify_column


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    null_pct: float
    distinct: int
    samples: list[str]
    sensitive_kinds: list[str]


@dataclass
class TableProfile:
    name: str
    rows: int
    columns: list[ColumnProfile]

    def column(self, name: str) -> ColumnProfile | None:
        return next((c for c in self.columns if c.name == name), None)


def load_dataset(folder: str | Path) -> dict[str, pd.DataFrame]:
    """Load every CSV in a folder. The file name (without extension) becomes the table name."""
    frames: dict[str, pd.DataFrame] = {}
    for path in sorted(Path(folder).glob("*.csv")):
        frames[path.stem] = pd.read_csv(path)
    return frames


def profile_table(name: str, df: pd.DataFrame, max_samples: int = 3) -> TableProfile:
    columns: list[ColumnProfile] = []
    for col in df.columns:
        series = df[col]
        non_null = series.dropna()
        samples = [str(v) for v in non_null.head(50).tolist()]
        columns.append(
            ColumnProfile(
                name=col,
                dtype=str(series.dtype),
                null_pct=round(float(series.isna().mean()) * 100, 1),
                distinct=int(series.nunique()),
                samples=samples[:max_samples],
                sensitive_kinds=classify_column(col, samples),
            )
        )
    return TableProfile(name=name, rows=len(df), columns=columns)


def profile_dataset(frames: dict[str, pd.DataFrame]) -> dict[str, TableProfile]:
    return {name: profile_table(name, df) for name, df in frames.items()}


def find_relationships(profiles: dict[str, TableProfile]) -> list[tuple[str, str, str]]:
    """Guess joins: the same column name ending in _id appearing in two tables."""
    relationships: list[tuple[str, str, str]] = []
    names = list(profiles)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            shared = {c.name for c in profiles[a].columns} & {c.name for c in profiles[b].columns}
            for col in sorted(shared):
                if col.endswith("_id"):
                    relationships.append((a, b, col))
    return relationships
