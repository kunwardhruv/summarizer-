from __future__ import annotations

from typing import Dict

from pypdf import PdfReader
import regex as re


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages)


def split_into_sections(text: str) -> Dict[str, str]:
    # Heuristic section splitter for academic papers; best-effort.
    content = text
    # Normalize headings to uppercase to improve matching
    normalized = re.sub(r"\n\s*\n", "\n\n", content)

    sections = {
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "discussion": "",
        "conclusion": "",
        "other": "",
    }

    # Try to find an abstract block first
    abs_match = re.search(r"(?is)\babstract\b\s*[:\-]?\s*(.+?)(?=\n\n\s*\b(introduction|background)\b|\Z)", normalized)
    if abs_match:
        sections["abstract"] = abs_match.group(1).strip()

    # Generic splitter by headings
    pattern = re.compile(
        r"(?im)^(abstract|introduction|background|methods?|materials and methods|experiments|results|discussion|conclusion|acknowledgments?|references)\s*$"
    )
    parts = []
    last_idx = 0
    current_label = "other"
    for m in pattern.finditer(normalized):
        if m.start() > last_idx:
            parts.append((current_label, normalized[last_idx:m.start()].strip()))
        current_label = m.group(1).lower()
        last_idx = m.end()
    # tail
    if last_idx < len(normalized):
        parts.append((current_label, normalized[last_idx:].strip()))

    for label, body in parts:
        if not body:
            continue
        label_key = (
            "methods"
            if label in {"method", "methods", "materials and methods", "experiments"}
            else "results" if label == "results" else "discussion" if label == "discussion" else "introduction" if label in {"introduction", "background"} else "conclusion" if label == "conclusion" else "other"
        )
        # Prefer the abstract we already captured
        if label_key == "abstract":
            if not sections["abstract"]:
                sections["abstract"] = body
        else:
            sections[label_key] = (sections[label_key] + "\n\n" + body).strip()

    return sections
