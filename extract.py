"""
extract.py
Uses Google Gemini (FREE tier, no credit card needed) to pull structured
experimental parameters (compound, concentration, target, assay method,
key finding) out of a paper abstract.

Requires: pip install google-generativeai
Requires: a GEMINI_API_KEY environment variable set to your own free API key
          (get one at https://aistudio.google.com/apikey - no payment needed)

NOTE: The free tier of Gemini has a limit on requests-per-minute. When
processing multiple papers in a row, this module automatically waits and
retries if that limit is hit, instead of failing silently.
"""

import os
import json
import time
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model_client = genai.GenerativeModel("gemini-2.5-flash")

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

RATE_LIMIT_MARKERS = ["429", "rate limit", "resource_exhausted", "quota"]


def extract_from_abstract(title: str, abstract: str, model: str = None, max_retries: int = 4):
    prompt = EXTRACTION_PROMPT.format(title=title, abstract=abstract)
    raw_text = ""

    for attempt in range(max_retries):
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
            error_text = str(e).lower()
            is_rate_limit = any(marker in error_text for marker in RATE_LIMIT_MARKERS)

            if is_rate_limit and attempt < max_retries - 1:
                wait = 8 * (attempt + 1)
                print(f"[extract] Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
                continue
            else:
                return {"error": str(e)}

    return {"error": "Failed after multiple retries (rate limited)"}


def extract_from_papers(papers: list, model: str = None):
    results = []
    for i, paper in enumerate(papers):
        extracted = extract_from_abstract(paper["title"], paper["abstract"])
        combined = {
            "title": paper["title"],
            "year": paper["year"],
            "authors": paper["authors"],
            "url": paper["url"],
            **extracted
        }
        results.append(combined)

        if i < len(papers) - 1:
            time.sleep(2)

    return results


if __name__ == "__main__":
    sample = extract_from_abstract(
        "Curcumin inhibits COX-2 in acne-related inflammation",
        "This study evaluated curcumin at concentrations of 10-50 micromolar against "
        "COX-2 activity using an in-vitro enzyme inhibition assay in HaCaT keratinocytes. "
        "Results showed dose-dependent inhibition with IC50 of 28 micromolar."
    )
    print(json.dumps(sample, indent=2))
