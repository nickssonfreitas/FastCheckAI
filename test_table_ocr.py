#!/usr/bin/env python3
"""Teste do OCR híbrido para extração de tabelas."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.extractors.pdf_loader import load_pdf
from src.extractors.table_extractor import detect_table_pages, extract_tables

# Test with corrupted PDF
pdf_path = "data/inputs/ASTM_A29_A29M_Rev_2015.pdf"

print("🧪 Testando OCR Híbrido para Extração de Tabelas")
print("=" * 80)
print(f"PDF: {pdf_path}\n")

# Load PDF
print("📄 Carregando PDF...")
pdf_doc = load_pdf(pdf_path)
print(f"✅ {len(pdf_doc)} páginas carregadas\n")

# Detect tables
print("🔍 Detectando tabelas...")
table_pages = detect_table_pages(pdf_doc)
print(f"✅ Tabelas detectadas em {len(table_pages)} páginas: {table_pages}\n")

# Test 1: Extract WITHOUT OCR (should get corrupted text)
print("=" * 80)
print("TEST 1: Extração SEM OCR (baseline)")
print("=" * 80)
result_no_ocr = extract_tables(pdf_path, table_pages[:1], enable_ocr_fallback=False)
if result_no_ocr.tables:
    table = result_no_ocr.tables[0]
    print(f"Tabela extraída: {table.data.shape[0]} linhas x {table.data.shape[1]} colunas")
    print(f"Método de extração: {table.metadata.extraction_method}")
    print(f"\nPrimeiras colunas:")
    for i, col in enumerate(list(table.data.columns)[:3], 1):
        col_display = str(col)[:60]
        special_chars = sum(1 for c in str(col) if ord(c) > 127)
        corruption_rate = special_chars / len(str(col)) if str(col) else 0
        status = "❌ CORROMPIDO" if corruption_rate > 0.3 else "✅ LIMPO"
        print(f"   {i}. {status} ({corruption_rate*100:.0f}%): {col_display}")
print()

# Test 2: Extract WITH OCR (should get clean text)
print("=" * 80)
print("TEST 2: Extração COM OCR (solução)")
print("=" * 80)
result_with_ocr = extract_tables(pdf_path, table_pages[:1], enable_ocr_fallback=True, corruption_threshold=0.3)
if result_with_ocr.tables:
    table = result_with_ocr.tables[0]
    print(f"Tabela extraída: {table.data.shape[0]} linhas x {table.data.shape[1]} colunas")
    print(f"Método de extração: {table.metadata.extraction_method}")
    print(f"\nPrimeiras colunas:")
    for i, col in enumerate(list(table.data.columns)[:5], 1):
        col_display = str(col)[:60]
        special_chars = sum(1 for c in str(col) if ord(c) > 127)
        corruption_rate = special_chars / len(str(col)) if str(col) else 0
        status = "✅ LIMPO" if corruption_rate < 0.1 else "⚠️  PARCIAL" if corruption_rate < 0.3 else "❌ CORROMPIDO"
        print(f"   {i}. {status} ({corruption_rate*100:.0f}%): {col_display}")

    print(f"\nPrimeiras 3 linhas da tabela:")
    for row_idx in range(min(3, len(table.data))):
        row_sample = " | ".join(str(table.data.iloc[row_idx, col_idx])[:30]
                               for col_idx in range(min(3, len(table.data.columns))))
        print(f"   Linha {row_idx + 1}: {row_sample}")
print()

# Summary
print("=" * 80)
print("📊 RESUMO")
print("=" * 80)
print(f"Método sem OCR: {result_no_ocr.tables[0].metadata.extraction_method if result_no_ocr.tables else 'N/A'}")
print(f"Método com OCR: {result_with_ocr.tables[0].metadata.extraction_method if result_with_ocr.tables else 'N/A'}")

if result_with_ocr.tables and result_with_ocr.tables[0].metadata.extraction_method == "ocr_tesseract":
    print("\n✅ SUCESSO: OCR foi aplicado automaticamente!")
elif result_with_ocr.tables:
    print(f"\n⚠️  ATENÇÃO: OCR não foi ativado. Método usado: {result_with_ocr.tables[0].metadata.extraction_method}")
    print("   Possíveis causas:")
    print("   1. Threshold de corrupção muito alto")
    print("   2. Tabela não foi detectada como corrompida")
    print("   3. OCR fallback falhou")
else:
    print("\n❌ ERRO: Nenhuma tabela extraída")

pdf_doc.close()
