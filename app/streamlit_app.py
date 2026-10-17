"""Onboarding Copilot demo app. Run:  streamlit run app/streamlit_app.py"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from onboarding_copilot.agent import answer_question
from onboarding_copilot.orientation import build_orientation
from onboarding_copilot.profiler import find_relationships, load_dataset, profile_dataset
from onboarding_copilot.sources import resolve_sources

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "sample"

st.set_page_config(page_title="Onboarding Copilot", layout="wide")
st.title("Onboarding Copilot")
st.caption("Your first week with a company's data: a map, a safety check, and answers you can verify.")

with st.sidebar:
    st.header("Dataset")
    data_dir = st.text_input("Folder of CSV files", str(DEFAULT_DATA))
    st.caption("Demo data is synthetic. Never load real company data into a demo.")


@st.cache_data(show_spinner=False)
def load(folder: str):
    frames = load_dataset(folder)
    profiles = profile_dataset(frames)
    return profiles, find_relationships(profiles)


try:
    profiles, relationships = load(data_dir)
except Exception as exc:  # shown to the user instead of a stack trace
    st.error(f"Could not load that folder: {exc}")
    st.stop()

if not profiles:
    st.warning("No CSV files found in that folder.")
    st.stop()

orientation = build_orientation(profiles, relationships)
tab_map, tab_ask, tab_manager = st.tabs(["1. Orientation", "2. Ask a question", "3. Manager view"])

with tab_map:
    st.caption("Status: Working")
    st.subheader("What is in here")
    st.dataframe(orientation.tables, width="stretch", hide_index=True)

    st.subheader("How the tables connect")
    if orientation.relationships:
        for a, b, col in orientation.relationships:
            st.write(f"{a} and {b} share `{col}`")
    else:
        st.write("No shared id columns found.")

    st.subheader("Handle with care")
    if orientation.sensitive_fields:
        st.dataframe(
            [
                {"table": t, "column": c, "looks like": ", ".join(k)}
                for t, c, k in orientation.sensitive_fields
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.write("No sensitive columns detected.")

    st.subheader("Good first questions")
    for q in orientation.starter_questions:
        st.write(q)

with tab_ask:
    st.caption("Status: Working with an API key set, Simulated offline mode without one")
    question = st.text_area("Ask about the data", placeholder="How do orders connect to customers?")
    if st.button("Ask") and question.strip():
        result = answer_question(question, profiles, relationships)
        for flag in result.flags:
            st.warning(f"Sensitive {flag.kind} found in your message and removed. {flag.advice}")
        st.markdown(result.text)
        st.caption(f"Answer mode: {result.mode}. Citations in [table.column] form point to the schema.")

        sources = resolve_sources(result.text, profiles)
        if sources:
            st.subheader("Check the sources")
            for src in sources:
                if not src.found:
                    st.error(f"`{src.ref}` is not in this dataset. Treat that part of the answer as unverified.")
                    continue
                with st.expander(f"{src.ref}"):
                    if src.column is None:
                        st.write(f"Table with {src.rows} rows. Columns: {', '.join(src.columns)}")
                        continue
                    st.write(
                        f"Type `{src.dtype}`, {src.null_pct}% empty, {src.distinct} distinct values, "
                        f"{src.rows} rows in `{src.table}`."
                    )
                    if src.sensitive_kinds:
                        st.warning(
                            f"Sensitive ({', '.join(src.sensitive_kinds)}). Sample values are hidden. "
                            "Ask the data owner before using this column."
                        )
                    else:
                        st.write("Example values: " + ", ".join(f"`{v}`" for v in src.samples))
        elif result.mode == "live":
            st.info("This answer cites no sources. Treat it as unverified.")

with tab_manager:
    st.caption("Status: Planned (mockup only, no live data)")
    st.write(
        "A manager would see which tables a new hire has explored, which questions they asked, "
        "and where they were warned about sensitive data."
    )
