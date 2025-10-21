from __future__ import annotations

import json
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from .config import AppConfig, ensure_directories_exist
from .arxiv_client import search_arxiv, download_pdf
from .pdf_utils import extract_text_from_pdf, split_into_sections
from .pipeline import run_pipeline_sync

console = Console()


@click.command()
@click.option("--id", "arxiv_id", type=str, help="arXiv ID to fetch")
@click.option("--query", type=str, help="Query to search on arXiv")
@click.option("--top_k", type=int, default=1, help="Top K results to consider (for query)")
@click.option("--role", type=str, default=None, help="Role preamble for prompting")
@click.option("--model", type=str, default=None, help="LLM model name")
@click.option("--provider", type=click.Choice(["openai", "ollama"]), default=None, help="LLM provider")
@click.option("--base_url", type=str, default=None, help="Base URL (e.g., http://localhost:11434 for Ollama)")
@click.option("--sections", type=str, default=None, help="Comma-separated sections to summarize (e.g., abstract,methods)")
@click.option("--max_words", type=int, default=300, help="Max words for summaries")
@click.option("--num_questions", type=int, default=5, help="Number of research questions")
@click.option("--save_json", is_flag=True, help="Save outputs to JSON under output/")
def main(
    arxiv_id: Optional[str],
    query: Optional[str],
    top_k: int,
    role: Optional[str],
    model: Optional[str],
    provider: Optional[str],
    base_url: Optional[str],
    sections: Optional[str],
    max_words: int,
    num_questions: int,
    save_json: bool,
) -> None:
    config = AppConfig.from_env()
    ensure_directories_exist(config)

    papers = search_arxiv(query=query, arxiv_id=arxiv_id, max_results=top_k)
    if not papers:
        console.print("[red]No results found.[/red]")
        raise SystemExit(1)

    paper = papers[0]
    console.print(Panel.fit(f"[bold]{paper.title}[/bold]\n{', '.join(paper.authors)}\n{paper.arxiv_id}", title="arXiv Paper"))

    pdf_path = download_pdf(paper, dest_dir=config.tmp_dir)
    text = extract_text_from_pdf(pdf_path)
    sections_map = split_into_sections(text)

    only_sections = None
    if sections:
        only_sections = [s.strip().lower() for s in sections.split(',') if s.strip()]

    result = run_pipeline_sync(
        config=config,
        sections=sections_map,
        role=role or config.default_role,
        model=model,
        max_words=max_words,
        num_questions=num_questions,
        provider=provider,
        base_url=base_url,
        only_sections=only_sections,
    )

    console.rule("Section Summaries")
    for k, v in result.section_summaries.items():
        if v:
            console.print(Panel(v, title=k.capitalize()))

    console.rule("Consolidated Summary")
    console.print(result.consolidated)

    console.rule("Refined Summary")
    console.print(result.refined)

    console.rule("Research Questions")
    console.print(result.questions)

    if save_json:
        out = {
            "paper": {
                "title": paper.title,
                "authors": paper.authors,
                "arxiv_id": paper.arxiv_id,
                "pdf_path": pdf_path,
            },
            "section_summaries": result.section_summaries,
            "consolidated": result.consolidated,
            "refined": result.refined,
            "questions": result.questions,
        }
        out_path = f"{config.output_dir}/{paper.arxiv_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        console.print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
