from __future__ import annotations

import os
import tempfile
from typing import List
import asyncio
import json

import streamlit as st

from summazier.config import AppConfig, ensure_directories_exist
from summazier.pdf_utils import extract_text_from_pdf, split_into_sections
from summazier.pipeline import run_pipeline_sync, run_pipeline_async


def parse_sections_input(sections_str: str) -> List[str]:
    return [s.strip().lower() for s in sections_str.split(",") if s.strip()]


def main() -> None:
    st.set_page_config(page_title="Summazier - Research Paper Summarizer", layout="wide")
    st.title("🔬 Summazier – Research Paper Summarizer")
    st.markdown(
        "Upload a research paper PDF and get section‑wise summaries, a consolidated + refined summary, "
        "and grounded follow‑up research questions."
    )

    with st.sidebar:
        st.header("Settings")
        provider = st.selectbox("Provider", ["ollama", "openai"], index=0)

        # Reasonable defaults for local vs cloud
        default_model = "llama3.2:1b" if provider == "ollama" else "gpt-4o-mini"
        model = st.text_input("Model name", value=default_model)

        sections_str = st.text_input(
            "Sections to analyze (comma-separated)",
            value="abstract,methods,results,discussion",
            help="Analyze only the sections you care about. Fewer sections → faster.",
        )

        num_questions = st.slider("Number of research questions", min_value=1, max_value=10, value=5)

        role = st.text_area(
            "Research analyst role / instructions",
            value=(
                "You are a research analyst in biomedical AI. Your outputs must be rigorous, concise, "
                "faithful to the paper, and useful for downstream research."
            ),
            height=120,
        )

        run_button = st.button("🚀 Analyze Paper", use_container_width=True)

    st.markdown("### 1️⃣ Upload your paper")
    uploaded_file = st.file_uploader("📄 Upload research paper PDF", type=["pdf"])

    if run_button:
        if uploaded_file is None:
            st.error("Please upload a PDF file first.")
            return

        with st.spinner("Processing paper... this may take a bit depending on model size."):
            # Load configuration & ensure directories
            config = AppConfig.from_env()
            ensure_directories_exist(config)

            # Save uploaded PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            try:
                text = extract_text_from_pdf(tmp_path)
                sections_map = split_into_sections(text)
                only_sections = parse_sections_input(sections_str)

                # Decide base_url for Ollama (local only; for cloud use OpenAI)
                base_url = "http://localhost:11434" if provider == "ollama" else None

                # Use async pipeline for providers that support it to parallelize section summaries
                if provider in ("ollama", "openai"):
                    result = asyncio.run(
                        run_pipeline_async(
                            config=config,
                            sections=sections_map,
                            role=role or config.default_role,
                            model=model or config.openai_model,
                            max_words=0,
                            num_questions=num_questions,
                            provider=provider,
                            base_url=base_url,
                            only_sections=only_sections,
                        )
                    )
                else:
                    result = run_pipeline_sync(
                        config=config,
                        sections=sections_map,
                        role=role or config.default_role,
                        model=model or config.openai_model,
                        max_words=0,
                        num_questions=num_questions,
                        provider=provider,
                        base_url=base_url,
                        only_sections=only_sections,
                    )
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        # Display results
        st.success("Analysis complete!")

        st.markdown("### 2️⃣ Analysis results")

        tab1, tab2, tab3 = st.tabs(["📝 Section summaries", "📋 Summaries", "❓ Research questions"])

        with tab1:
            for key, value in result.section_summaries.items():
                if not value:
                    continue
                with st.expander(key.capitalize(), expanded=(key == "abstract")):
                    st.markdown(value)

        with tab2:
            st.subheader("Consolidated summary")
            st.markdown(result.consolidated or "_No consolidated summary produced._")

            st.subheader("Refined summary")
            st.markdown(result.refined or "_No refined summary produced._")

        with tab3:
            st.subheader("Research questions")
            st.markdown(result.questions or "_No questions produced._")

        # Optional: allow user to download all outputs as JSON
        result_payload = {
            "section_summaries": result.section_summaries,
            "consolidated": result.consolidated,
            "refined": result.refined,
            "questions": result.questions,
        }
        st.markdown("### 3️⃣ Export")
        st.download_button(
            "⬇️ Download results as JSON",
            data=json.dumps(result_payload, ensure_ascii=False, indent=2),
            file_name="summazier_output.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()

