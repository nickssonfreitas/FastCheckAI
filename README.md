# FastCheckAI

**Automated comparison of technical PDF documents using Agno framework**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## 📋 Overview

FastCheckAI is a Proof of Concept (PoC) for automated semantic comparison of technical PDF documents, specifically designed for comparing technical standards like ASTM specifications. The project validates the feasibility of using the Agno framework for intelligent document comparison with LLM-powered semantic analysis.

### Key Features

- **PDF Text Extraction** with hybrid OCR fallback for corrupted PDFs
- **Section Hierarchy Parsing** with nested structure detection
- **Semantic Comparison** using Agno framework + OpenAI GPT-4o
- **Change Classification** (additions, removals, modifications)
- **Severity Analysis** (CRITICAL, MEDIUM, LOW)
- **Interactive Jupyter Notebook** interface

### Use Case

Compare two versions of technical standards (e.g., ASTM A29/A29M 2015 vs 2016) to identify:
- New requirements added
- Deprecated clauses removed
- Modified specifications
- Semantic significance of changes

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (required)
- **uv** package manager ([install](https://astral.sh/uv/install))
- **Tesseract OCR** (recommended for corrupted PDFs)
- **OpenAI API Key** (required)

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/FastCheckAI.git
cd FastCheckAI
```

#### 2. Run the setup script
```bash
bash scripts/setup.sh
```

This will:
- Create a Python 3.12 virtual environment
- Install all dependencies from `pyproject.toml`
- Create `.env` file from template
- Set up project directories
- Optionally install Tesseract OCR (interactive prompt)

#### 3. Configure API key
Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 4. Activate the environment
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 5. Start Jupyter Lab
```bash
bash scripts/start_jupyter.sh
```

Open `notebooks/pipeline.ipynb` and run cells sequentially.

---

## 🔧 System Requirements

### Required Dependencies (Auto-installed)

- **agno** ≥2.0.11 - LLM orchestration framework
- **pymupdf** ≥1.23.0 - Fast PDF text extraction
- **pytesseract** ≥0.3.13 - Python wrapper for Tesseract OCR
- **pillow** ≥10.0.0 - Image processing for OCR
- **openai** ≥1.0.0 - OpenAI API client
- **pandas** ≥2.3.3 - Data manipulation
- **jupyter** ≥1.0.0 - Interactive notebook interface

### Optional: Tesseract OCR Engine

Tesseract is **required** for OCR fallback when PDFs have corrupted text encoding (common in ASTM documents).

#### Installation by Platform

**Ubuntu/Debian/WSL2:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

**Verify installation:**
```bash
tesseract --version
# Expected: tesseract 4.x.x or 5.x.x
```

#### Why Tesseract?

Some technical PDFs (like ASTM standards) use custom fonts with broken Unicode mappings, causing PyMuPDF to extract gibberish characters:
- ❌ Without OCR: "Ü»­·¹²¿¬·±²æ ßîçñßîçÓ"
- ✅ With OCR: "Designation: A29/A29M"

FastCheckAI automatically detects corrupted text and falls back to OCR extraction.

---

## 📚 Project Structure

```
FastCheckAI/
├── src/                        # Source code modules
│   ├── config.py               # Centralized configuration
│   ├── pdf_loader.py           # PDF validation and loading
│   ├── text_extractor.py       # Text extraction + OCR fallback
│   ├── table_extractor.py      # Table extraction (pdfplumber)
│   ├── section_aligner.py      # Section matching between PDFs
│   ├── text_comparator.py      # Diff-based text comparison
│   ├── semantic_comparator.py  # Agno + LLM semantic analysis
│   ├── severity_classifier.py  # Change severity classification
│   └── output_generator.py     # Results visualization
│
├── notebooks/
│   └── pipeline.ipynb          # Main interactive pipeline
│
├── tests/
│   └── unit/                   # Unit tests (80+ tests, 88% coverage)
│       ├── test_pdf_loader.py
│       ├── test_text_extractor.py
│       └── ...
│
├── data/
│   ├── inputs/                 # Input PDFs (up to 25MB each)
│   └── outputs/                # Generated results
│
├── scripts/
│   ├── setup.sh                # Automated setup script
│   ├── start_jupyter.sh        # Jupyter Lab launcher
│   └── test_extraction_fix.py  # OCR validation script
│
├── docs/                       # Project documentation
│   ├── requirements_complete.md
│   ├── architecture_decision.md
│   └── backlog/
│
├── pyproject.toml              # Python dependencies (PEP 621)
├── CLAUDE.md                   # Claude Code instructions
├── IMPLEMENTATION_SUMMARY.md   # Feature 3 implementation notes
└── README.md                   # This file
```

---

## 💻 Usage

### Basic Usage: Compare Two PDFs

```python
from src.pdf_loader import load_pdf
from src.text_extractor import extract_text, parse_section_hierarchy

# Load PDFs
pdf_2015 = load_pdf("data/inputs/astm_2015.pdf")
pdf_2016 = load_pdf("data/inputs/astm_2016.pdf")

# Extract text (automatic OCR fallback)
text_2015 = extract_text(pdf_2015)
text_2016 = extract_text(pdf_2016)

# Parse section structure
sections_2015 = parse_section_hierarchy(text_2015)
sections_2016 = parse_section_hierarchy(text_2016)

print(f"PDF 2015: {len(sections_2015)} top-level sections")
print(f"PDF 2016: {len(sections_2016)} top-level sections")
```

### Advanced: Custom OCR Settings

```python
# High-quality OCR for scanned documents
text = extract_text(
    pdf_doc,
    enable_ocr=True,           # Enable OCR fallback
    corruption_threshold=0.40,  # Trigger OCR if >40% special chars
    ocr_dpi=600,               # High resolution (slower but better)
)
```

### Disable OCR (Fast Mode)

```python
# Skip OCR for native PDFs (20x faster)
text = extract_text(pdf_doc, enable_ocr=False)
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/unit/ -v
```

### Run Specific Module Tests
```bash
pytest tests/unit/test_text_extractor.py -v
```

### Run with Coverage Report
```bash
pytest tests/unit/ -v --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Test OCR Functionality
```bash
python scripts/test_extraction_fix.py
```

Expected output:
```
✓ PASS: Metadata Fix
✓ PASS: Corruption Detection
✓ PASS: Hybrid Extraction
```

---

## 📊 Current Development Status

### Completed Features ✅

- ✅ **Feature 1: Environment Setup** (100%)
  - Python 3.12 venv with uv
  - Dependencies configured via pyproject.toml
  - Git repository initialized

- ✅ **Feature 2: PDF Loader** (100%)
  - Size validation (≤25MB)
  - PyMuPDF integration
  - Error handling with custom exceptions
  - 100% test coverage (34 tests)

- ✅ **Feature 3: Text Extraction** (100%)
  - Fast text extraction with PyMuPDF
  - Hybrid OCR fallback for corrupted PDFs
  - Section hierarchy parsing
  - Metadata extraction
  - 88% test coverage (80 tests)

### In Progress 🚧

- ⏳ **Feature 4: Section Alignment**
- ⏳ **Feature 5: Text Comparison**
- ⏳ **Feature 6: Semantic Analysis (Agno + LLM)**
- ⏳ **Feature 7: Severity Classification**
- ⏳ **Feature 8: Output Generation**

**Overall Progress**: 27% (3/11 features complete)

---

## 🔍 Known Limitations

1. **PDF Size**: Maximum 25MB per PDF (PoC constraint)
2. **OCR Performance**: 10-20x slower than native text extraction
3. **OCR Accuracy**: ~95-98% for printed text (may vary with scan quality)
4. **Language Support**: English only (extensible)
5. **Deployment**: Local Jupyter Notebook only (no web interface)

---

## 🐛 Troubleshooting

### Issue: "Tesseract not found"
**Solution**: Install Tesseract OCR engine (see [System Requirements](#system-requirements))

### Issue: Corrupted text extraction
**Symptom**: Text shows "Ü»­·¹²¿¬·±²æ" instead of "Designation"

**Solution**: Enable OCR fallback (default behavior):
```python
text = extract_text(pdf_doc, enable_ocr=True)  # Default
```

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution**: Set PYTHONPATH:
```bash
export PYTHONPATH=/path/to/FastCheckAI:$PYTHONPATH
```

### Issue: Slow extraction (>3 minutes)
**Solution**: Disable OCR for native PDFs:
```python
text = extract_text(pdf_doc, enable_ocr=False)
```

---

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Instructions for Claude Code
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Feature 3 implementation details
- **[docs/requirements_complete.md](docs/requirements_complete.md)** - Complete requirements
- **[docs/architecture_decision.md](docs/architecture_decision.md)** - Technology stack rationale
- **[TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)** - Test suite overview
- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - Test results and coverage

---

## 🤝 Contributing

This is a Proof of Concept project with fixed scope. For questions or feedback:
1. Review existing documentation in `docs/`
2. Check [CLAUDE.md](CLAUDE.md) for development guidelines
3. Run test suite before submitting changes: `pytest tests/unit/ -v`

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🎯 Roadmap

### Phase 1: PoC Completion (Current)
- [x] Environment setup
- [x] PDF loading
- [x] Text extraction with OCR
- [ ] Section alignment
- [ ] Semantic comparison (Agno)
- [ ] Results visualization

### Phase 2: Production Readiness (Future)
- [ ] Web interface
- [ ] Batch processing
- [ ] Multi-language support
- [ ] Cloud deployment
- [ ] API endpoints
- [ ] Advanced caching

---

## 📧 Contact

For technical questions about this PoC, consult:
- Project documentation in `docs/`
- CLAUDE.md for Claude Code guidance
- Test suite in `tests/unit/` for usage examples

---

**Last Updated**: October 1, 2025
**Version**: 0.1.0 (PoC)
