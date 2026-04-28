"""
Convert all .txt policy files in docs/ to .pdf
Run this on your Mac after scrape_policies.py
"""
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

DOCS_DIR = "docs"

def convert(txt_path, pdf_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
        rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, spaceAfter=6)
    body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=14, spaceAfter=4)

    story = []
    name = os.path.basename(txt_path).replace('.txt', '').replace('_', ' ')
    story.append(Paragraph(name, styles['Title']))
    story.append(Spacer(1, 0.2 * inch))

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.05 * inch))
            continue
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if line.startswith('SECTION') or line.startswith('PART') or line.isupper():
            story.append(Paragraph(line, heading_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)

def main():
    txt_files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.txt')]
    if not txt_files:
        print("No .txt files found in docs/")
        return
    print(f"Converting {len(txt_files)} .txt files to PDF...\n")
    for txt_file in txt_files:
        txt_path = os.path.join(DOCS_DIR, txt_file)
        pdf_path = os.path.join(DOCS_DIR, txt_file.replace('.txt', '.pdf'))
        try:
            convert(txt_path, pdf_path)
            print(f"  ✓ {txt_file} → {pdf_path}")
        except Exception as e:
            print(f"  ✗ {txt_file}: {e}")
    print(f"\nDone! Now run: git add docs/*.pdf && git commit -m 'Sprint 5: Add La Trobe policy PDFs' && git push")

if __name__ == "__main__":
    main()