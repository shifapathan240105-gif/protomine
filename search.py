"""
search.py
Fetches relevant paper abstracts from PubMed for a given research query.
No API key required. PubMed is the U.S. National Library of Medicine's database,
specifically for biomedical/pharmacology research.
"""

import requests
import time
import xml.etree.ElementTree as ET

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def search_papers(query: str, limit: int = 8, max_retries: int = 3):
    """
    Search PubMed for papers relevant to the query.
    Returns a list of dicts: {title, abstract, year, authors, url}
    """
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": limit,
        "retmode": "json",
        "sort": "relevance"
    }

    pmids = []
    for attempt in range(max_retries):
        try:
            resp = requests.get(ESEARCH_URL, params=search_params, timeout=15)
            if resp.status_code == 429:
                wait = 3 * (attempt + 1)
                print(f"[search_papers] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            pmids = resp.json().get("esearchresult", {}).get("idlist", [])
            break
        except requests.exceptions.RequestException as e:
            print(f"[search_papers] esearch failed: {e}")
            return []

    if not pmids:
        return []

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    try:
        resp = requests.get(EFETCH_URL, params=fetch_params, timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        print(f"[search_papers] efetch failed: {e}")
        return []

    papers = []
    for article in root.findall(".//PubmedArticle"):
        title_el = article.find(".//ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else "Untitled"

        abstract_parts = article.findall(".//AbstractText")
        abstract = " ".join("".join(a.itertext()).strip() for a in abstract_parts) if abstract_parts else ""
        if not abstract:
            continue

        year_el = article.find(".//PubDate/Year")
        year = year_el.text if year_el is not None else "N/A"

        authors = []
        for author in article.findall(".//Author")[:3]:
            last = author.find("LastName")
            fore = author.find("ForeName")
            if last is not None:
                name = last.text
                if fore is not None:
                    name = f"{fore.text} {name}"
                authors.append(name)

        pmid_el = article.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None else ""
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

        papers.append({
            "title": title,
            "abstract": abstract,
            "year": year,
            "authors": ", ".join(authors),
            "venue": "PubMed",
            "url": url
        })

    return papers


if __name__ == "__main__":
    results = search_papers("curcumin concentration COX-2 inhibition acne", limit=5)
    for r in results:
        print(r["title"], "-", r["year"])
