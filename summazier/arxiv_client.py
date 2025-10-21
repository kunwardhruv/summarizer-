from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

import arxiv  # type: ignore


@dataclass(frozen=True)
class ArxivPaper:
    title: str
    authors: List[str]
    summary: str
    published: str
    updated: str
    arxiv_id: str
    pdf_url: str


def search_arxiv(query: Optional[str] = None, arxiv_id: Optional[str] = None, max_results: int = 3) -> List[ArxivPaper]:
    if not query and not arxiv_id:
        raise ValueError("Provide either query or arxiv_id")

    if arxiv_id:
        search = arxiv.Search(id_list=[arxiv_id])
    else:
        search = arxiv.Search(
            query=query or "",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

    results: List[ArxivPaper] = []
    for result in search.results():  # type: ignore[attr-defined]
        paper_id = result.get_short_id()
        results.append(
            ArxivPaper(
                title=result.title,
                authors=[a.name for a in result.authors],
                summary=result.summary,
                published=str(result.published),
                updated=str(result.updated),
                arxiv_id=paper_id,
                pdf_url=result.pdf_url,
            )
        )
    return results


def download_pdf(paper: ArxivPaper, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    filename = f"{paper.arxiv_id}.pdf"
    dest_path = os.path.join(dest_dir, filename)

    client = arxiv.Client()
    # Re-fetch to get a result object compatible with download
    search = arxiv.Search(id_list=[paper.arxiv_id])
    for result in client.results(search):
        result.download_pdf(filename=dest_path)
        break
    if not os.path.exists(dest_path):
        raise RuntimeError("Failed to download PDF from arXiv")
    return dest_path
