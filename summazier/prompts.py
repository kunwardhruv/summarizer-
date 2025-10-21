from __future__ import annotations

from typing import Optional


def role_preamble(role: Optional[str]) -> str:
    return role or (
        "You are a research analyst in biomedical AI. Be rigorous, concise, and faithful to the paper."
    )


def stepwise_summary_prompt(role: Optional[str], section_name: str, section_text: str, max_words: int) -> str:
    return (
        f"{role_preamble(role)}\n\n"
        f"Task: Summarize the {section_name} section of an academic paper.\n"
        f"Guidance: Capture all key details (setups, datasets, metrics, limitations). No hard word limit.\n\n"
        f"Section text:\n" + section_text.strip()
    )


def consolidate_prompt(role: Optional[str], abstract: str, methods: str, results: str, discussion: str, max_words: int) -> str:
    return (
        f"{role_preamble(role)}\n\n"
        "Task: Produce a coherent, structured summary across sections (Abstract, Methods, Results, Discussion).\n"
        "Guidance: Use bullet points where helpful; include limitations and future work. No hard word limit.\n\n"
        f"Abstract summary:\n{abstract}\n\n"
        f"Methods summary:\n{methods}\n\n"
        f"Results summary:\n{results}\n\n"
        f"Discussion summary:\n{discussion}"
    )


def refinement_prompt(role: Optional[str], draft_summary: str, max_words: int) -> str:
    return (
        f"{role_preamble(role)}\n\n"
        "Task: Refine the summary for clarity, fidelity, and completeness.\n"
        "Guidance: Improve readability and structure. No hard word limit.\n\n"
        f"Draft:\n{draft_summary}"
    )


def questions_prompt(role: Optional[str], final_summary: str, num_questions: int = 5) -> str:
    return (
        f"{role_preamble(role)}\n\n"
        "Task: Propose follow-up research questions grounded in the summarized findings.\n"
        f"Constraints: {num_questions} questions; each specific, testable, and impactful.\n"
        "Formatting: Return as a numbered list, one question per line.\n\n"
        f"Summary:\n{final_summary}"
    )
