# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastCheckAI is a Proof of Concept (PoC) for automated comparison of technical PDF documents, specifically designed for comparing technical standards like ASTM A29/A29M (2015 vs 2016 versions). The project is intended to validate the technical feasibility of using the Agno framework for semantic document comparison.

## Development Commands

### Environment Setup

**Quick Setup (Recommended)**:
```bash
# Run the setup script (creates venv with Python 3.12, installs dependencies, creates .env)
bash scripts/setup.sh

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Manual Setup**:
```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from pyproject.toml
uv pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env to add OPENAI_API_KEY
```

**Note:** All dependencies are managed via `pyproject.toml` (PEP 621 compliant). No `requirements.txt` needed.

### Running the Notebook
```bash
# Start Jupyter notebook server
jupyter notebook

# Open main_pipeline.ipynb in browser
# Execute cells sequentially (Shift+Enter) or Run All
```

### Testing Individual Components
```python
# Test PDF loading
from src.pdf_loader import load_pdf
pdf_doc = load_pdf("data/inputs/astm_2015.pdf")

# Test text extraction
from src.text_extractor import extract_text
text_content = extract_text(pdf_doc)

# Test semantic comparison with Agno
from src.semantic_comparator import analyze_semantic_significance
result = analyze_semantic_significance(change_object)
```

### Common Development Tasks
```bash
# Check for large files before processing
ls -lh data/inputs/*.pdf

# Monitor memory usage during execution
htop  # or use Activity Monitor on Mac

# Clear Jupyter output for cleaner commits
jupyter nbconvert --clear-output --inplace notebooks/main_pipeline.ipynb

# Profile slow cells in Jupyter
%%time  # Add to beginning of cell to measure execution time
```

## Architecture & Structure

### High-Level Architecture
The project follows a **Linear ETL Pipeline** pattern optimized for Jupyter Notebook execution:

```
PDF Input → Validation → Extraction → Alignment → Comparison → Analysis → Output
```

### Key Architectural Decisions

1. **Hybrid PDF Processing Stack**:
   - PyMuPDF for fast text extraction (60x faster than alternatives)
   - pdfplumber selectively for table extraction (superior accuracy)
   - pytesseract for OCR when dealing with scanned PDFs

2. **Agno Framework Integration**:
   - Used specifically for LLM orchestration in semantic comparison
   - Fallback to direct OpenAI API calls if Agno encounters issues
   - Framework chosen for its minimal overhead (~3.75 KiB memory per agent)

3. **Section Alignment Strategy**:
   - Hierarchical approach: exact ID match → fuzzy title match → LLM suggestion
   - Confidence threshold of 0.8 for automatic acceptance
   - Agno-powered LLM fallback for complex alignments

4. **Performance Targets**:
   - End-to-end processing: ≤3 minutes for 25MB PDFs
   - Memory usage: ≤4GB RAM
   - Extraction rate: ≥2 pages/second for native PDFs

### Module Organization
```
fastcheckai_poc/
├── notebooks/
│   └── main_pipeline.ipynb      # Main execution notebook (11 cells)
├── src/
│   ├── config.py                # Centralized configuration
│   ├── pdf_loader.py            # PDF validation and loading
│   ├── text_extractor.py        # PyMuPDF/OCR text extraction
│   ├── table_extractor.py       # pdfplumber table extraction
│   ├── section_aligner.py       # Section alignment logic
│   ├── text_comparator.py       # Diff-based text comparison
│   ├── semantic_comparator.py   # AGNO + LLM semantic analysis
│   ├── table_comparator.py      # Numerical table comparison
│   ├── severity_classifier.py   # Change severity classification
│   ├── output_generator.py      # DataFrame and visualization
│   └── utils.py                 # Helper functions
└── data/
    ├── inputs/                  # Source PDFs (ASTM 2015/2016)
    └── outputs/                 # Generated results
```

### Critical Implementation Details

#### Agno Integration Pattern
```python
# Primary usage for semantic comparison
from agno import Agent

agent = Agent(
    model="gpt-4o",
    instructions="You are a technical document expert...",
    temperature=0.3  # Low for consistency
)

# Fallback pattern if Agno fails
if agno_error:
    from openai import OpenAI
    client = OpenAI()
    result = client.chat.completions.create(...)
```

#### Section Alignment Flow
1. Exact match by section ID (confidence=1.0)
2. Fuzzy match by title using rapidfuzz (threshold≥0.8)
3. If average confidence <0.8, use Agno LLM for suggestions
4. Track unmatched sections as added/removed

#### Performance Optimizations
- Process PyMuPDF pages in parallel when possible
- Limit LLM context to 4000 tokens per call
- Cache section alignments to avoid recomputation
- Use selective pdfplumber only for detected table pages

## Important Context from Documentation

### Project Constraints (from requirements_complete.md)
- **Timeline**: 3.5 weeks fixed deadline
- **Team**: Single developer learning Agno framework during PoC
- **Environment**: Local Jupyter Notebook only (no deployment)
- **Input**: 2 PDFs up to 25MB each (ASTM technical standards)
- **Output**: Structured DataFrame + elaborate visualization in notebook

### Key Requirements
- **Essential Features** (Must work for PoC success):
  - Load 2 PDFs via local file path
  - Extract text preserving section structure
  - Align corresponding sections between PDFs
  - Detect additions, removals, modifications
  - Use LLM (via Agno) for semantic significance analysis
  - Display results in readable notebook format

- **Desirable Features** (Nice to have):
  - OCR for scanned PDFs (≥70% accuracy acceptable)
  - Table comparison with numerical tolerance
  - Severity classification (CRITICAL/MEDIUM/LOW)
  - Modular pipeline execution for debugging

### Technology Stack Rationale (from architecture_decision.md)
The hybrid approach was chosen (Option C) because it:
- Meets the Agno learning objective without compromising deadline
- Combines PyMuPDF speed with pdfplumber table accuracy
- Provides easy fallback from Agno to direct OpenAI API
- Balances cost and quality with GPT-4o (~$12-25 for 10 full runs, superior semantic analysis)

### Risk Mitigation
- **Week 1 Checkpoint**: If Agno setup fails, switch to direct OpenAI API (2-3 hour migration)
- **Alignment Fallback**: If heuristic alignment <90% accurate, use LLM-only approach
- **Performance Issues**: If >3 minutes, parallelize PyMuPDF or reduce LLM calls

### Agent Workflow Integration (from fluxo_agentes.md)
While the project has a comprehensive agent system defined, for this PoC the focus is on:
1. **requirements-analyst**: Requirements already captured in requirements_complete.md
2. **architect-specialist**: Architecture decided in architecture_decision.md
3. **python-expert-reviewer**: Code review during implementation
4. **qa-automation-specialist**: Basic test coverage validation
5. **project-analyzer**: Health check at milestone completion

The full agent workflow is designed for production projects and is overkill for this PoC.

## Development Tips

### When Working with Agno
- Start with simple test cases to validate Agno installation
- Keep prompts under 4000 tokens to avoid context limits
- Use temperature=0.3 for consistent semantic analysis
- Always implement try/except blocks with OpenAI fallback

### PDF Processing Best Practices
- Validate PDF size before processing (≤25MB limit)
- Check if PDF is native (text-selectable) before attempting OCR
- For tables, scan pages first to identify which contain tables
- Use pdfplumber only on table-containing pages to optimize speed

### OCR Implementation (Feature 3 - Completed)

FastCheckAI implements a **hybrid extraction strategy** to handle PDFs with corrupted text encoding:

#### Problem: Corrupted Text Extraction
Some technical PDFs (especially ASTM standards) use custom embedded fonts with broken Unicode mappings:
- **Symptom**: PyMuPDF extracts gibberish like "Ü»­·¹²¿¬·±²æ ßîçñßîçÓ"
- **Expected**: "Designation: A29/A29M"
- **Root cause**: Custom fonts (e.g., Z@RFDA6.tmp) with Identity-H encoding but missing ToUnicode CMap

#### Solution: Automatic OCR Fallback

The `extract_text()` function now uses a 3-step process:

1. **Try PyMuPDF fast extraction** (0.5 sec/page)
2. **Detect corruption** using `is_text_corrupted()` (checks if >30% special characters)
3. **Fallback to OCR** if corrupted (5-10 sec/page)

```python
from src.text_extractor import extract_text

# Automatic OCR fallback (default)
text = extract_text(pdf_doc, enable_ocr=True)

# Disable OCR for speed (may have corrupted text)
text = extract_text(pdf_doc, enable_ocr=False)

# Custom OCR settings
text = extract_text(
    pdf_doc,
    corruption_threshold=0.40,  # Higher = less sensitive
    ocr_dpi=600,                # Higher = better quality, slower
)
```

#### Tesseract OCR Installation

**Required for OCR functionality**. Install before running extraction:

```bash
# Ubuntu/Debian/WSL2
sudo apt-get update && sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS
brew install tesseract

# Verify installation
tesseract --version
```

**Note**: The setup script (`scripts/setup.sh`) checks for Tesseract and offers to install it interactively.

#### OCR Performance Characteristics

- **Speed**: 10-20x slower than PyMuPDF (5-10 sec/page vs 0.5 sec/page)
- **Accuracy**: 95-98% for clean printed text (ASTM documents)
- **Use case**: Only triggered for corrupted pages (typically pages 2+ in ASTM PDFs)
- **Total time**: ~90 seconds for 17-page ASTM PDF (within 3-minute target)

#### Testing OCR Implementation

```bash
# Quick validation script
python scripts/test_extraction_fix.py

# Expected output:
# ✓ PASS: Metadata Fix
# ✓ PASS: Corruption Detection
# ✓ PASS: Hybrid Extraction
```

#### OCR Debugging

Enable debug logging to see OCR decisions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

text = extract_text(pdf_doc)
# Logs will show:
# DEBUG: Corruption check: 2450/3000 special chars (81.67%), threshold: 30%
# INFO: Page 2: Corrupted text detected, using OCR fallback
```

### Jupyter Notebook Organization
- Keep configuration in Cell 1 for easy modification
- Save intermediate results after each major step
- Use markdown cells to document what each code cell does
- Include progress logging for long-running operations

### Performance Monitoring
```python
# Add to cells for performance tracking
import time
start_time = time.time()
# ... your code ...
print(f"Execution time: {time.time() - start_time:.2f} seconds")

# Memory usage monitoring
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

## Success Criteria

The PoC is considered successful when:
- [ ] End-to-end pipeline executes without critical errors
- [ ] 2 ASTM PDFs processed successfully
- [ ] Differences displayed in structured, readable format
- [ ] Execution time ≤3 minutes
- [ ] Agno framework integrated and functioning for semantic comparison
- [ ] Presentation delivered to Engineering team with go/no-go decision

## Common Issues and Solutions

### Issue: Agno installation fails
**Solution**: Use uv to install directly from GitHub if PyPI version is problematic:
```bash
uv pip install git+https://github.com/agno-agi/agno.git

# Or add to pyproject.toml:
# agno @ git+https://github.com/agno-agi/agno.git
```

### Issue: OCR accuracy too low
**Solution**: Focus on native PDFs for PoC validation; mark OCR as "desirable" not "essential"

### Issue: Section alignment confidence low
**Solution**: Manually review alignment results; adjust fuzzy matching threshold; rely more on LLM suggestions

### Issue: Memory usage exceeds 4GB
**Solution**: Process PDFs in chunks; clear variables after each stage; use del to explicitly free memory