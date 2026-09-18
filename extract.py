"""
extract.py
Uses Google Gemini (FREE tier, no credit card needed) to pull structured
experimental parameters (compound, concentration, target, assay method,
key finding) out of a paper abstract.

Requires: pip install google-generativeai
Requires: a GEMINI_API_KEY environment variable set to your own free API key
          (get one at https://aistudio.google.com/apikey - no payment needed)
"""

import os
import json
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model_client = genai.GenerativeModel("gemini-3.6-flash")

EXTRACTION_PROMPT = """You are a research-methodology extraction assistant for bioscience/pharmacology papers.

Given the paper title and abstract below, extract the following fields if present.
If a field is not mentioned in the abstract, use null. Do not guess or invent values.

Return ONLY valid JSON, no other text, no markdown code fences, in this exact structure:
{{
  "compound": "<main compound/extract studied, or null>",
  "concentration": "<concentration or dose used, with units, or null>",
  "target": "<biological target / pathway / enzyme studied, or null>",
  "assay_method": "<experimental method used, e.g. MIC, DPPH, docking, cell viability assay, or null>",
  "organism_or_model": "<organism, cell line, or model used, or null>",
  "key_finding": "<one short sentence summarizing the main result, or null>"
}}

Title: {title}

Abstract: {abstract}
"""


def extract_from_abstract(title: str, abstract: str, model: str = None):
    prompt = EXTRACTION_PROMPT.format(title=title, abstract=abstract)
    raw_text = ""

    try:
        response = model_client.generate_content(prompt)
        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        parsed = json.loads(raw_text.strip())
        return parsed

    except json.JSONDecodeError:
        return {"error": "Could not parse LLM output as JSON", "raw": raw_text}
    except Exception as e:
        return {"error": str(e)}


def extract_from_papers(papers: list, model: str = None):
    results = []
    for paper in papers:
        extracted = extract_from_abstract(paper["title"], paper["abstract"])
        combined = {
            "title": paper["title"],
            "year": paper["year"],
            "authors": paper["authors"],
            "url": paper["url"],
            **extracted
        }
        results.append(combined)
    return results


if __name__ == "__main__":
    sample = extract_from_abstract(
        "Curcumin inhibits COX-2 in acne-related inflammation",
        "This study evaluated curcumin at concentrations of 10-50 micromolar against "
        "COX-2 activity using an in-vitro enzyme inhibition assay in HaCaT keratinocytes. "
        "Results showed dose-dependent inhibition with IC50 of 28 micromolar."
    )
    print(json.dumps(sample, indent=2))
