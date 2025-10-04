#!/usr/bin/env python3
"""
Script de diagnóstico para avaliar qualidade de extração de PDFs

Testa cada componente isoladamente:
1. Carregamento do PDF
2. Extração de texto (PyMuPDF vs OCR)
3. Detecção de tabelas
4. Extração de tabelas
5. Parsing de seções

Usage:
    python scripts/diagnose_extraction.py data/inputs/ASTM_A29_A29M_Rev_2015.pdf
"""

import argparse
import sys
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.pdf_loader import load_pdf
from src.extractors.text_extractor import extract_text, parse_section_hierarchy
from src.extractors.table_extractor import detect_table_pages, extract_tables


def diagnose_pdf(pdf_path: str):
    """Executa diagnóstico completo de extração do PDF."""

    print("=" * 80)
    print("📋 DIAGNÓSTICO DE EXTRAÇÃO DE PDF")
    print("=" * 80)
    print(f"Arquivo: {pdf_path}\n")

    # =========================================================================
    # ETAPA 1: Carregamento do PDF
    # =========================================================================
    print("🔍 [1/5] CARREGAMENTO DO PDF")
    print("-" * 80)

    try:
        pdf_doc = load_pdf(pdf_path)
        print(f"✅ PDF carregado com sucesso")
        print(f"   📄 Páginas: {len(pdf_doc)}")
        print(f"   📦 Tamanho: {Path(pdf_path).stat().st_size / 1024:.1f} KB")

        # Metadata
        metadata = pdf_doc.metadata
        if metadata:
            print(f"   ℹ️  Título: {metadata.get('title', 'N/A')}")
            print(f"   ℹ️  Autor: {metadata.get('author', 'N/A')}")
            print(f"   ℹ️  Criado: {metadata.get('creationDate', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ ERRO: {e}\n")
        return

    # =========================================================================
    # ETAPA 2: Extração de Texto
    # =========================================================================
    print("🔍 [2/5] EXTRAÇÃO DE TEXTO")
    print("-" * 80)

    # Teste 1: PyMuPDF sem OCR
    print("📝 Teste 2.1: PyMuPDF puro (sem OCR)")
    try:
        text_no_ocr = extract_text(pdf_doc, enable_ocr=False)
        print(f"✅ Texto extraído: {len(text_no_ocr)} caracteres")

        # Amostra das primeiras 500 caracteres
        sample = text_no_ocr[:500].replace('\n', ' ')
        print(f"   Amostra: {sample[:200]}...")

        # Detectar corrupção
        special_chars = sum(1 for c in text_no_ocr if ord(c) > 127)
        corruption_rate = special_chars / len(text_no_ocr) if text_no_ocr else 0
        print(f"   Taxa de caracteres especiais: {corruption_rate*100:.1f}%")

        if corruption_rate > 0.3:
            print(f"   ⚠️  TEXTO CORROMPIDO (>{30}% caracteres especiais)")
        print()
    except Exception as e:
        print(f"❌ ERRO: {e}\n")

    # Teste 2: PyMuPDF com OCR fallback
    print("📝 Teste 2.2: Híbrido (PyMuPDF + OCR fallback)")
    try:
        text_with_ocr = extract_text(pdf_doc, enable_ocr=True)
        print(f"✅ Texto extraído: {len(text_with_ocr)} caracteres")

        # Amostra das primeiras 500 caracteres
        sample = text_with_ocr[:500].replace('\n', ' ')
        print(f"   Amostra: {sample[:200]}...")

        # Detectar corrupção
        special_chars = sum(1 for c in text_with_ocr if ord(c) > 127)
        corruption_rate = special_chars / len(text_with_ocr) if text_with_ocr else 0
        print(f"   Taxa de caracteres especiais: {corruption_rate*100:.1f}%")

        if corruption_rate < 0.1:
            print(f"   ✅ TEXTO LIMPO (<10% caracteres especiais)")
        print()
    except Exception as e:
        print(f"❌ ERRO: {e}\n")

    # =========================================================================
    # ETAPA 3: Parsing de Seções
    # =========================================================================
    print("🔍 [3/5] PARSING DE SEÇÕES")
    print("-" * 80)

    try:
        sections = parse_section_hierarchy(text_with_ocr)

        # Listar todas as seções de nível 1
        level_1_sections = [s for s in sections.values() if s['level'] == 1]
        print(f"✅ Seções identificadas: {len(sections)} total")
        print(f"   📑 Seções de nível 1: {len(level_1_sections)}")

        print("\n   Primeiras 10 seções de nível 1:")
        for i, section in enumerate(level_1_sections[:10], 1):
            title = section['title'][:60]
            print(f"   {i:2d}. [{section['section_id']:6s}] {title}")

        if len(level_1_sections) > 10:
            print(f"   ... (+{len(level_1_sections) - 10} seções)")
        print()
    except Exception as e:
        print(f"❌ ERRO: {e}\n")

    # =========================================================================
    # ETAPA 4: Detecção de Tabelas
    # =========================================================================
    print("🔍 [4/5] DETECÇÃO DE TABELAS")
    print("-" * 80)

    try:
        table_pages = detect_table_pages(pdf_doc)
        print(f"✅ Páginas com tabelas detectadas: {len(table_pages)}")
        if table_pages:
            print(f"   📊 Páginas: {table_pages}")
        else:
            print(f"   ℹ️  Nenhuma tabela detectada no documento")
        print()
    except Exception as e:
        print(f"❌ ERRO: {e}\n")
        table_pages = []

    # =========================================================================
    # ETAPA 5: Extração de Tabelas
    # =========================================================================
    print("🔍 [5/5] EXTRAÇÃO DE TABELAS")
    print("-" * 80)

    if not table_pages:
        print("⏭️  Pulado (nenhuma tabela detectada)")
        print()
    else:
        try:
            # Extrair apenas as 3 primeiras tabelas para diagnóstico
            pages_to_extract = table_pages[:min(3, len(table_pages))]
            result = extract_tables(pdf_path, pages_to_extract)

            print(f"✅ Tabelas extraídas: {len(result.tables)}")
            print(f"   ⏱️  Tempo de extração: {result.extraction_time_seconds:.2f}s")

            # Analisar cada tabela
            for i, extracted_table in enumerate(result.tables, 1):
                table = extracted_table.data
                metadata = extracted_table.metadata

                print(f"\n   📊 Tabela {i} (Página {metadata.page_num + 1}):")
                print(f"      Dimensões: {table.shape[0]} linhas x {table.shape[1]} colunas")
                print(f"      Confiança: {metadata.confidence:.0%}")

                # Mostrar nomes das colunas
                print(f"      Colunas:")
                for j, col in enumerate(table.columns[:5], 1):
                    col_display = str(col)[:50]
                    # Verificar corrupção do nome da coluna
                    special_chars = sum(1 for c in str(col) if ord(c) > 127)
                    if special_chars > len(str(col)) * 0.3:
                        print(f"         {j}. ⚠️  CORROMPIDO: {col_display}")
                    else:
                        print(f"         {j}. {col_display}")

                if len(table.columns) > 5:
                    print(f"         ... (+{len(table.columns) - 5} colunas)")

                # Mostrar primeiras 3 linhas
                print(f"\n      Primeiras 3 linhas:")
                for row_idx in range(min(3, len(table))):
                    row_sample = " | ".join(str(table.iloc[row_idx, col_idx])[:20]
                                           for col_idx in range(min(3, len(table.columns))))
                    print(f"         Linha {row_idx + 1}: {row_sample}")

            print()
        except Exception as e:
            print(f"❌ ERRO: {e}\n")
            import traceback
            traceback.print_exc()

    # =========================================================================
    # RESUMO FINAL
    # =========================================================================
    print("=" * 80)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 80)
    print(f"✅ PDF carregado: {len(pdf_doc)} páginas")
    print(f"✅ Texto extraído: {len(text_with_ocr)} caracteres")
    print(f"✅ Seções identificadas: {len(sections)}")
    print(f"✅ Tabelas detectadas: {len(table_pages)} páginas")
    if table_pages:
        print(f"✅ Tabelas extraídas: {len(result.tables) if result else 0}")
    print()
    print("💡 PRÓXIMOS PASSOS:")
    print("   1. Se texto está corrompido → Verificar encoding do PDF")
    print("   2. Se tabelas não detectadas → Ajustar thresholds de detecção")
    print("   3. Se tabelas corrompidas → Usar OCR nas páginas com tabelas")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Diagnóstico de extração de PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "pdf_path",
        help="Caminho para o arquivo PDF a ser diagnosticado"
    )

    args = parser.parse_args()

    # Validar arquivo
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ Erro: Arquivo não encontrado: {pdf_path}")
        return 1

    # Executar diagnóstico
    diagnose_pdf(str(pdf_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
