from __future__ import annotations

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import AppConfig, ensure_directories_exist
from .pdf_utils import extract_text_from_pdf, split_into_sections
from .pipeline import run_pipeline_sync, run_pipeline_async

app = FastAPI(title="Summazier - Research Paper Summarizer")

# Create templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Summazier - Research Paper Summarizer</title>
        <style>
            :root { --bg: #0b0f17; --panel: #121826; --text: #e6edf3; --muted: #a0aec0; --accent: #5ab0f3; --accent2: #9b59b6; }
            * { box-sizing: border-box; }
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: var(--bg); color: var(--text); }
            .container { background: linear-gradient(180deg, #121826, #0f1624); padding: 30px; border-radius: 14px; box-shadow: 0 8px 30px rgba(0,0,0,0.35); border: 1px solid #1f2a40; }
            h1 { color: #f0f6fc; text-align: center; margin-bottom: 18px; }
            .subtitle { text-align: center; color: var(--muted); margin-bottom: 28px; }
            .upload-area { border: 2px dashed var(--accent); padding: 28px; text-align: center; border-radius: 10px; margin: 16px 0; background: rgba(90,176,243,0.06); }
            input[type="file"] { margin: 10px 0; color: var(--text); }
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
            .form-group { margin: 10px 0; }
            label { display: block; margin-bottom: 6px; font-weight: bold; color: #c9d1d9; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #24324a; border-radius: 8px; background: #0e1523; color: var(--text); }
            textarea { resize: vertical; }
            button { background: linear-gradient(90deg, var(--accent), var(--accent2)); color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
            button:hover { filter: brightness(1.05); }
            .results { margin-top: 24px; padding: 20px; background: #0e1523; border-radius: 10px; border: 1px solid #22304a; }
            .section { margin: 18px 0; padding: 15px; background: #0b1220; border-left: 4px solid var(--accent); border-radius: 6px; }
            .section h3 { margin-top: 0; color: #e6edf3; }
            .mono { white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; line-height: 1.4; }
            .loading { text-align: center; padding: 20px; color: var(--muted); }
            .error { background: #7f1d1d; color: #fee2e2; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container"> 
            <h1>🔬 Summazier</h1>
            <p class="subtitle">Upload a research paper PDF and get stepwise summaries, key insights, and research questions.</p>
            
            <form id="uploadForm" enctype="multipart/form-data"> 
                <div class="upload-area"> 
                    <h3>📄 Upload Research Paper PDF</h3>
                    <input type="file" id="pdfFile" name="pdf_file" accept=".pdf" required>
                </div>
                
                <div class="form-group">
                    <label for="role">Research Analyst Role:</label>
                    <textarea id="role" name="role" rows="3">You are a research analyst in biomedical AI. Your outputs must be rigorous, concise, faithful to the paper, and useful for downstream research.</textarea>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label for="provider">AI Provider:</label>
                        <select id="provider" name="provider"> 
                            <option value="ollama" selected>Ollama (Local)</option>
                            <option value="openai">OpenAI</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="model">Model:</label>
                        <input type="text" id="model" name="model" value="llama3.2:1b" placeholder="llama3.2:1b">
                    </div>
                    <div class="form-group">
                        <label for="sections">Sections to Analyze:</label>
                        <input type="text" id="sections" name="sections" value="abstract,methods,results,discussion">
                    </div>
                    <div class="form-group">
                        <label for="num_questions">Number of Research Questions:</label>
                        <input type="number" id="num_questions" name="num_questions" value="5" min="1" max="10"> 
                    </div>
                </div>

                <button type="submit">🚀 Analyze Paper</button>
            </form>
            
            <div id="loading" class="loading" style="display: none;">⏳ Processing your paper...</div>
            
            <div id="results" class="results" style="display: none;"></div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const loading = document.getElementById('loading');
                const results = document.getElementById('results');
                
                loading.style.display = 'block';
                results.style.display = 'none';
                
                try {
                    const response = await fetch('/analyze', { method: 'POST', body: formData });
                    if (!response.ok) throw new Error('Analysis failed');
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    results.style.display = 'block';
                    
                    const summaries = Object.entries(data.section_summaries).map(([key, value]) => 
                        value ? `<h4>${key.charAt(0).toUpperCase() + key.slice(1)}</h4><div class="mono">${value.replace(/</g, '&lt;')}</div>` : ''
                    ).join('');
                    
                    const questionsHtml = `<div class="mono">${(data.questions || '').replace(/</g, '&lt;')}</div>`;
                    
                    results.innerHTML = `
                        <h2>📊 Analysis Results</h2>
                        <div class="section"> <h3>📝 Section Summaries</h3> ${summaries} </div>
                        <div class="section"> <h3>📋 Consolidated Summary</h3> <div class="mono">${(data.consolidated || '').replace(/</g, '&lt;')}</div> </div>
                        <div class="section"> <h3>✨ Refined Summary</h3> <div class="mono">${(data.refined || '').replace(/</g, '&lt;')}</div> </div>
                        <div class="section"> <h3>❓ Research Questions</h3> ${questionsHtml} </div>
                    `;
                } catch (error) {
                    loading.style.display = 'none';
                    results.style.display = 'block';
                    results.innerHTML = `<div class="error">Error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/analyze")
async def analyze_paper(
    pdf_file: UploadFile = File(...),
    role: str = Form("You are a research analyst in biomedical AI. Your outputs must be rigorous, concise, faithful to the paper, and useful for downstream research."),
    provider: str = Form("ollama"),
    model: str = Form("llama3.2:1b"),
    sections: str = Form("abstract,methods,results,discussion"),
    max_words: int = Form(0),
    num_questions: int = Form(5),
):
    import traceback
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Load config
        config = AppConfig.from_env()
        ensure_directories_exist(config)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await pdf_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Extract text and split sections
            text = extract_text_from_pdf(tmp_path)
            sections_map = split_into_sections(text)
            
            # Parse sections filter
            only_sections = [s.strip().lower() for s in sections.split(',') if s.strip()]
            
            # Run pipeline (no word limit enforced)
            # Prefer async (concurrent) flow for providers that support async calls.
            # We now use async for both OpenAI and Ollama to parallelize section summaries.
            if provider in ("openai", "ollama"):
                result = await run_pipeline_async(
                    config=config,
                    sections=sections_map,
                    role=role,
                    model=model,
                    max_words=0,
                    num_questions=num_questions,
                    provider=provider,
                    base_url="http://localhost:11434" if provider == "ollama" else None,
                    only_sections=only_sections,
                )
            else:
                result = run_pipeline_sync(
                    config=config,
                    sections=sections_map,
                    role=role,
                    model=model,
                    max_words=0,
                    num_questions=num_questions,
                    provider=provider,
                    base_url="http://localhost:11434" if provider == "ollama" else None,
                    only_sections=only_sections,
                )
            
            return {
                "success": True,
                "section_summaries": result.section_summaries,
                "consolidated": result.consolidated,
                "refined": result.refined,
                "questions": result.questions,
            }
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

