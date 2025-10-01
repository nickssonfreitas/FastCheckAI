#!/usr/bin/env python3
"""Test to confirm the fix for format field."""
import pymupdf as fitz

pdf_path = "data/ASTM_A29_A29M_Rev.00'2015.pdf"
pdf_doc = fitz.open(pdf_path)

print('Verificação final:')
print(f'1. pdf_doc.pdf_version existe? {hasattr(pdf_doc, "pdf_version")}')
print(f'2. pdf_doc.metadata["format"] existe? {"format" in pdf_doc.metadata}')
print(f'3. Valor de metadata["format"]: {pdf_doc.metadata.get("format")}')
print()
print('Comparação do código atual vs correto:')
print(f'  Código ATUAL (ERRADO):')
print(f'    pdf_doc.pdf_version -> AttributeError (não existe)')
print(f'    Resultado: "PDF N/A"')
print()
print(f'  Código CORRETO:')
print(f'    pdf_doc.metadata["format"] -> {repr(pdf_doc.metadata["format"])}')
print(f'    Resultado esperado: "{pdf_doc.metadata["format"]}"')

pdf_doc.close()
