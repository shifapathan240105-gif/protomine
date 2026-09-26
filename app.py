"""
app.py
Streamlit frontend for ProtoMine - Literature Mining & Protocol Assistant.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from search import search_papers
from extract import extract_from_papers

st.set_page_config(page_title="ProtoMine", layout="wide")

st.title("ProtoMine")
st.caption(
    "An automated literature-mining tool for evidence-based experimental protocol design. "
    "Type a research question about a compound, target, or assay. This tool searches "
    "PubMed and extracts the experimental parameters researchers actually used - "
    "concentrations, methods, models - so you don't have to read every paper manually."
)

with st.sidebar:
    st.header("Settings")
    num_papers = st.slider("Number of papers to analyze", min_value=3, max_value=12, value=6)
    st.markdown("---")
    st.markdown(
        "**Note:** This tool requires a `GEMINI_API_KEY` environment variable "
        "to be set before running, and an internet connection to reach PubMed."
    )

query = st.text_input(
    "Research question",
    placeholder="e.g. curcumin concentration used against COX-2 in acne studies"
)

run_button = st.button("Search & Extract Protocols", type="primary")

if run_button and query.strip():
    with st.spinner(f"Searching papers for: {query} ..."):
        papers = search_papers(query, limit=num_papers)

    if not papers:
        st.error("No papers with usable abstracts were found. Try rephrasing your query.")
    else:
        st.success(f"Found {len(papers)} papers with abstracts. Extracting protocol data...")

        progress = st.progress(0)
        results = []
        for i, paper in enumerate(papers):
            extracted = extract_from_papers([paper])[0]
            results.append(extracted)
            progress.progress((i + 1) / len(papers))

        df = pd.DataFrame(results)

        st.subheader("Extracted Protocol Comparison")
        display_cols = [c for c in
                         ["title", "year", "compound", "concentration", "target",
                          "assay_method", "organism_or_model", "key_finding"]
                         if c in df.columns]
        st.dataframe(df[display_cols], width='stretch', hide_index=True)

        if "concentration" in df.columns:
            st.subheader("Concentrations Reported Across Papers")
            conc_df = df[["title", "compound", "concentration"]].dropna(subset=["concentration"])
            if not conc_df.empty:
                st.table(conc_df)
            else:
                st.info("No concentration values were explicitly reported in these abstracts.")

        st.subheader("Source Papers")
        for r in results:
            with st.expander(f"{r.get('title', 'Untitled')} ({r.get('year', 'N/A')})"):
                if r.get("error"):
                    st.error(f"Extraction error: {r['error']}")
                st.write(f"**Authors:** {r.get('authors', 'N/A')}")
                st.write(f"**Key finding:** {r.get('key_finding', 'N/A')}")
                if r.get("url"):
                    st.markdown(f"[View paper]({r['url']})")

        st.download_button(
            "Download results as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="protomine_extraction.csv",
            mime="text/csv"
        )

elif run_button:
    st.warning("Please enter a research question first.")
