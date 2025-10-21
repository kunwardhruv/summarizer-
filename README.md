# 🔬 Summazier - AI Research Paper Summarizer

> **Transform any research paper into structured insights, stepwise summaries, and follow-up research questions with AI-powered analysis.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-purple.svg)](https://ollama.com/)

## ✨ Features

- 🎯 **Stepwise Analysis**: Abstract → Methods → Results → Discussion
- 🧠 **Role-Based Prompting**: Customize AI analyst persona (e.g., "biomedical AI researcher")
- 🔍 **Key Insights Extraction**: Consolidated and refined summaries
- ❓ **Research Questions**: AI-generated follow-up questions for future work
- 🌐 **Web Interface**: Beautiful dark-themed UI with PDF upload
- 🖥️ **CLI Support**: Command-line interface for batch processing
- 🔄 **Multiple Providers**: OpenAI GPT or local Ollama models
- 📊 **No Word Limits**: Comprehensive analysis without artificial constraints

## 🚀 Quick Start

### Option 1: Web UI (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/summazier.git
cd summazier
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Install Ollama (free local AI)
# Download from: https://ollama.com/download
ollama pull llama3.1:8b

# 3. Start web interface
python run_web.py

# 4. Open browser: http://localhost:8000
# Upload any PDF and get instant analysis! 🎉
```

### Option 2: OpenAI (Faster)

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# Run CLI
python -m summazier.cli --id 1706.03762 --model gpt-4o-mini --save_json
```

## 📖 Usage Examples

### Web Interface
1. **Upload PDF** → Select your research paper
2. **Configure** → Choose AI provider, model, sections
3. **Analyze** → Get stepwise summaries and research questions
4. **Export** → Copy results or save as JSON

### CLI Examples

```bash
# Analyze by arXiv ID
python -m summazier.cli --id 1706.03762 --provider ollama --model llama3.1:8b

# Search and analyze
python -m summazier.cli --query "protein structure prediction" --top_k 1

# Custom sections only
python -m summazier.cli --id 1706.03762 --sections abstract,methods --num_questions 3

# OpenAI (requires API key)
python -m summazier.cli --id 1706.03762 --provider openai --model gpt-4o-mini
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
# OpenAI (optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Ollama (default)
PROVIDER=ollama
BASE_URL=http://localhost:11434

# Customization
DEFAULT_ROLE="You are a research analyst in biomedical AI..."
MAX_WORDS=300
```

### Supported Models

| Provider | Models | Speed | Cost |
|----------|--------|-------|------|
| **Ollama** | `llama3.1:8b`, `llama3.1:7b`, `llama3.1:3b` | Medium | Free |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` | Fast | Paid |

## 🏗️ Architecture

```
summazier/
├── 📄 web.py              # FastAPI web interface
├── 🔧 cli.py              # Command-line interface  
├── 🧠 pipeline.py         # Core analysis pipeline
├── 📝 prompts.py          # AI prompt templates
├── 📊 pdf_utils.py        # PDF text extraction
├── 🔍 arxiv_client.py     # arXiv paper fetching
├── ⚙️ config.py          # Configuration management
└── 🤖 llm.py              # LLM client wrapper
```

## 🎨 Web Interface Preview

![Summazier Web Interface](https://via.placeholder.com/800x400/0b0f17/5ab0f3?text=Summazier+Web+Interface)

- **Dark Theme**: Easy on the eyes for long research sessions
- **PDF Upload**: Drag & drop any research paper
- **Real-time Analysis**: Watch as AI processes your paper
- **Structured Output**: Clean, readable summaries and questions

## 🔧 Advanced Usage

### Custom Prompts

Edit `summazier/prompts.py` to customize AI behavior:

```python
def role_preamble(role: Optional[str]) -> str:
    return role or (
        "You are a research analyst in [YOUR DOMAIN]. "
        "Focus on [SPECIFIC ASPECTS] and provide [OUTPUT STYLE]."
    )
```

### Batch Processing

```bash
# Process multiple papers
for id in 1706.03762 2012.00123 2103.00001; do
    python -m summazier.cli --id $id --save_json
done
```

### API Integration

```python
from summazier.pipeline import run_pipeline_sync
from summazier.config import AppConfig

config = AppConfig.from_env()
result = run_pipeline_sync(
    config=config,
    sections=your_pdf_sections,
    role="Your custom role",
    provider="ollama",
    model="llama3.1:8b"
)
```

## 🐛 Troubleshooting

### Common Issues

**Ollama not found:**
```bash
# Add to PATH
export PATH="$PATH:/path/to/ollama"
# Or use full path
/path/to/ollama pull llama3.1:8b
```

**Slow processing:**
- Use smaller model: `llama3.1:7b` or `llama3.1:3b`
- Limit sections: `--sections abstract`
- Reduce questions: `--num_questions 3`

**PDF parsing issues:**
- Try different PDF (some have complex formatting)
- Use CLI for debugging: `python -m summazier.cli --id 1706.03762`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup

```bash
git clone https://github.com/yourusername/summazier.git
cd summazier
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .  # Install in development mode
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for LLM integration
- [FastAPI](https://fastapi.tiangolo.com/) for web framework
- [Ollama](https://ollama.com/) for local AI models
- [arXiv](https://arxiv.org/) for research paper access

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/summazier/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/summazier/discussions)
- 📧 **Email**: kunwarrdhruv@gmail.com.com

---

**Made with ❤️ for the research community**
