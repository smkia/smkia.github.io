import bibtexparser
from pathlib import Path
import re
from datetime import datetime
import textwrap

# Load BibTeX file
with open("_bibliography/references.bib", "r", encoding="utf-8") as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

# Output directory
output_dir = Path("_publications")
output_dir.mkdir(parents=True, exist_ok=True)

def slugify(text, max_length=80):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    slug = re.sub(r"[\s_]+", "-", text).strip("-")
    return slug[:max_length]

def escape_yaml(s):
    """Escape double quotes and backslashes for YAML safety."""
    return s.replace("\\", "\\\\").replace('"', '\\"')

def parse_date(entry):
    year = entry.get("year", "1900")
    month = entry.get("month", "01")

    try:
        month = str(datetime.strptime(month[:3], "%b").month).zfill(2)
    except:
        month = re.sub(r"\D", "", month).zfill(2) or "01"

    try:
        return datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
    except:
        return datetime.strptime("1900-01-01", "%Y-%m-%d")

# Sort entries by date descending
sorted_entries = sorted(bib_database.entries, key=parse_date, reverse=True)

# Create Markdown files
for entry in sorted_entries:
    try:
        title = entry.get("title", "No title").strip("{}")
        authors = entry.get("author", "Unknown author")
        year = entry.get("year", "2023")
        date_str = parse_date(entry).strftime("%Y-%m-%d")
        venue = entry.get("journal") or entry.get("booktitle") or "Unknown venue"
        doi = entry.get("doi", "")
        url = entry.get("url", "")
        paperurl = f"https://doi.org/{doi}" if doi else url
        citation = f"{authors} ({year}). {title}. {venue}."

        # Get original BibTeX entry as string
        bibtex_lines = [f"@{entry.get('ENTRYTYPE','article')}{{{entry.get('ID','no_id')},"]
        for k, v in entry.items():
            if k.lower() not in ["id", "entrytype"]:
                v = v.replace('\n', ' ').replace('\r', ' ')
                bibtex_lines.append(f"  {k} = {{{v}}},")
        bibtex_lines.append("}")
        bibtex_block = "\n".join(bibtex_lines)

        # Escape fields for YAML
        title_escaped = escape_yaml(title)
        venue_escaped = escape_yaml(venue)
        authors_escaped = escape_yaml(authors)
        paperurl_escaped = escape_yaml(paperurl)
        citation_escaped = escape_yaml(citation)

        filename = slugify(title) + ".md"
        permalink = f"/publication/{slugify(title)}"

        md_content = f"""---
title: "{title_escaped}"
collection: publications
permalink: {permalink}
date: {date_str}
venue: "{venue_escaped}"
authors: "{authors_escaped}"
paperurl: "{paperurl_escaped}"
citation: "{citation_escaped}"
bibtex: |
{textwrap.indent(bibtex_block, "  ")}
---
"""

        (output_dir / filename).write_text(md_content, encoding="utf-8")
        print(f"✔ Generated: {filename}")

    except Exception as e:
        print(f"✖ Failed to process entry: {entry.get('title', 'Unknown')} → {e}")
