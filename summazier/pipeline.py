from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Iterable

from .config import AppConfig
from .llm import LLMClient
from .prompts import (
    stepwise_summary_prompt,
    consolidate_prompt,
    refinement_prompt,
    questions_prompt,
)


@dataclass
class PipelineResult:
    section_summaries: Dict[str, str]
    consolidated: str
    refined: str
    questions: str


def run_pipeline_sync(
    config: AppConfig,
    sections: Dict[str, str],
    role: Optional[str] = None,
    model: Optional[str] = None,
    max_words: int = 300,
    num_questions: int = 5,
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    only_sections: Optional[Iterable[str]] = None,
) -> PipelineResult:
    client = LLMClient(
        api_key=config.openai_api_key,
        model=model or config.openai_model,
        provider=(provider or config.provider),
        base_url=(base_url or config.base_url),
    )

    # Stepwise summaries
    wanted = list(only_sections) if only_sections else ["abstract", "methods", "results", "discussion"]
    summary_sections = {}
    for key in wanted:
        text = sections.get(key, "").strip()
        if not text:
            summary_sections[key] = ""
            continue
        prompt = stepwise_summary_prompt(role, key, text, max_words)
        out = client.complete(system="You summarize scientific text.", prompt=prompt)
        summary_sections[key] = out.strip()

    # Consolidation uses whatever sections we produced
    consolidated = client.complete(
        system="You write structured scientific summaries.",
        prompt=consolidate_prompt(
            role,
            summary_sections.get("abstract", ""),
            summary_sections.get("methods", ""),
            summary_sections.get("results", ""),
            summary_sections.get("discussion", ""),
            max_words=max_words,
        ),
    ).strip()

    # Refinement
    refined = client.complete(
        system="You refine text with strict word limits.",
        prompt=refinement_prompt(role, consolidated, max_words),
    ).strip()

    # Questions
    questions = client.complete(
        system="You generate research questions.",
        prompt=questions_prompt(role, refined, num_questions=num_questions),
    ).strip()

    return PipelineResult(
        section_summaries=summary_sections,
        consolidated=consolidated,
        refined=refined,
        questions=questions,
    )
