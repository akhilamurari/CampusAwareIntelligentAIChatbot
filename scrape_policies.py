"""
La Trobe Policy Library Scraper
Fetches full policy text from the La Trobe Policy Library website
and saves each policy as a .txt file ready for RAG ingestion.
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re

OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

POLICIES = [
    ("Academic_Dress_Policy",                   "https://policies.latrobe.edu.au/document/view.php?id=208&version=4"),
    ("Academic_Staff_Qualifications_Policy",    "https://policies.latrobe.edu.au/document/view.php?id=420&version=1"),
    ("Admissions_Policy",                       "https://policies.latrobe.edu.au/document/view.php?id=169&version=3"),
    ("Admissions_Schedule",                     "https://policies.latrobe.edu.au/document/view.php?id=389&version=2"),
    ("Assessment_Standards",                    "https://policies.latrobe.edu.au/document/view.php?id=363&version=2"),
    ("Asset_Management_Policy",                 "https://policies.latrobe.edu.au/document/view.php?id=229&version=2"),
    ("Campus_Access_Premises_and_Facilities_Policy", "https://policies.latrobe.edu.au/document/view.php?id=434&version=1"),
    ("Code_of_Conduct",                         "https://policies.latrobe.edu.au/document/view.php?id=71&version=1"),
    ("Course_Design_Policy",                    "https://policies.latrobe.edu.au/document/view.php?id=328&version=2"),
    ("Desktop_Equipment_Policy",                "https://policies.latrobe.edu.au/document/view.php?id=366&version=2"),
    ("Graduate_Research_Admissions_Policy",     "https://policies.latrobe.edu.au/document/view.php?id=113&version=4"),
    ("Research_Human_Ethics_Procedure",         "https://policies.latrobe.edu.au/document/view.php?id=112&version=4"),
    ("Student_Charter",                         "https://policies.latrobe.edu.au/document/view.php?id=225&version=3"),
    ("Student_Support_Policy",                  "https://policies.latrobe.edu.au/document/view.php?id=409&version=2"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CampusAwareBot/1.0; research project)"
}

def clean_text(text):
    """Remove excessive whitespace and navigation artifacts."""
    # Remove "Hide Navigation" and similar UI artifacts
    text = re.sub(r'Hide Navigation\s*', '', text)
    text = re.sub(r'Top of Page\s*', '', text)
    text = re.sub(r'Historic Versions\s*Future Versions\s*Print\s*Feedback\s*', '', text)
    text = re.sub(r'Current Version Status and Details Associated Information\s*', '', text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def scrape_policy(name, url):
    print(f"  Fetching: {name}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"    ✗ Failed to fetch: {e}")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove nav sidebar and footer elements
    for tag in soup.select("nav, header, footer, .nav, #nav, .sidebar, .navigation, script, style"):
        tag.decompose()

    # Try to find the main content area
    main = (
        soup.find("div", {"id": "main-content"}) or
        soup.find("div", {"class": "main-content"}) or
        soup.find("div", {"id": "content"}) or
        soup.find("article") or
        soup.find("main") or
        soup.find("body")
    )

    if not main:
        print(f"    ✗ Could not find content area")
        return False

    # Extract text, preserving some structure
    lines = []
    for elem in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th"]):
        text = elem.get_text(separator=" ", strip=True)
        if text and len(text) > 2:
            if elem.name in ["h1", "h2"]:
                lines.append(f"\n{'='*60}\n{text.upper()}\n{'='*60}")
            elif elem.name in ["h3", "h4"]:
                lines.append(f"\n{text}\n{'-'*40}")
            elif elem.name == "li":
                lines.append(f"  • {text}")
            else:
                lines.append(text)

    full_text = f"SOURCE: {url}\nDOCUMENT: {name.replace('_', ' ')}\n\n"
    full_text += clean_text("\n".join(lines))

    # Save as .txt for RAG ingestion
    out_path = os.path.join(OUTPUT_DIR, f"{name}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    word_count = len(full_text.split())
    print(f"    ✓ Saved ({word_count} words) → {out_path}")
    return True

def main():
    print(f"La Trobe Policy Scraper")
    print(f"Output directory: {OUTPUT_DIR}/")
    print(f"Policies to scrape: {len(POLICIES)}\n")

    success, failed = 0, []

    for name, url in POLICIES:
        ok = scrape_policy(name, url)
        if ok:
            success += 1
        else:
            failed.append(name)
        time.sleep(1)  # Be polite to the server

    print(f"\n{'='*50}")
    print(f"Done! {success}/{len(POLICIES)} policies scraped successfully.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"\nNext step: run your ingest_pdfs.py (or ingest_docs.py) pointing at '{OUTPUT_DIR}/'")

if __name__ == "__main__":
    main()
