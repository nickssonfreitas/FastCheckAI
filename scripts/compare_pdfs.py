#!/usr/bin/env python3
"""
Script de linha de comando para comparação rápida de PDFs

Usage:
    python scripts/compare_pdfs.py pdf1.pdf pdf2.pdf
    python scripts/compare_pdfs.py pdf1.pdf pdf2.pdf --output meu_relatorio.md
    python scripts/compare_pdfs.py pdf1.pdf pdf2.pdf --format html
"""

import argparse
import sys
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipelines.semantic_comparison import PDFComparisonPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Compara dois PDFs e gera relatório de diferenças",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Comparação básica
  python scripts/compare_pdfs.py data/inputs/doc_v1.pdf data/inputs/doc_v2.pdf

  # Com nome de arquivo customizado
  python scripts/compare_pdfs.py doc1.pdf doc2.pdf --output meu_relatorio.md

  # Formato HTML
  python scripts/compare_pdfs.py doc1.pdf doc2.pdf --format html

  # Sem OCR (mais rápido)
  python scripts/compare_pdfs.py doc1.pdf doc2.pdf --no-ocr

  # Modo rápido (sem análise semântica LLM)
  python scripts/compare_pdfs.py doc1.pdf doc2.pdf --fast
        """
    )

    # Argumentos obrigatórios
    parser.add_argument(
        "pdf1",
        help="Caminho para o primeiro PDF (versão antiga)"
    )
    parser.add_argument(
        "pdf2",
        help="Caminho para o segundo PDF (versão nova)"
    )

    # Argumentos opcionais
    parser.add_argument(
        "-o", "--output",
        help="Nome do arquivo de saída (default: auto-gerado com timestamp)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Formato do relatório (default: markdown)"
    )
    parser.add_argument(
        "--output-dir",
        default="data/outputs",
        help="Diretório para salvar o relatório (default: data/outputs)"
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Desabilita OCR (mais rápido, mas pode falhar em PDFs escaneados)"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Modo rápido: desabilita análise semântica LLM (apenas diff textual)"
    )
    parser.add_argument(
        "--model",
        choices=["gpt-4o", "gpt-4o-mini"],
        default="gpt-4o",
        help="Modelo LLM para análise semântica (default: gpt-4o)"
    )

    args = parser.parse_args()

    # Validar arquivos de entrada
    pdf1_path = Path(args.pdf1)
    pdf2_path = Path(args.pdf2)

    if not pdf1_path.exists():
        print(f"❌ Erro: Arquivo não encontrado: {pdf1_path}")
        return 1

    if not pdf2_path.exists():
        print(f"❌ Erro: Arquivo não encontrado: {pdf2_path}")
        return 1

    # Criar diretório de saída se não existir
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configurar pipeline
    print("🚀 Iniciando comparação de PDFs...")
    print(f"   PDF 1: {pdf1_path.name}")
    print(f"   PDF 2: {pdf2_path.name}")
    print(f"   Formato: {args.format}")
    print(f"   OCR: {'Desabilitado' if args.no_ocr else 'Habilitado'}")
    print(f"   Análise Semântica: {'Desabilitada (modo rápido)' if args.fast else 'Habilitada'}")
    print()

    try:
        pipeline = PDFComparisonPipeline(
            enable_ocr=not args.no_ocr,
            llm_model=args.model,
            output_dir=str(output_dir),
            log_level="INFO",
        )

        # Executar comparação
        result = pipeline.run(
            pdf1_path=str(pdf1_path),
            pdf2_path=str(pdf2_path),
            report_format=args.format,
            report_filename=args.output,
        )

        # Exibir resultados
        print("=" * 60)
        print("✅ COMPARAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print(f"📊 Estatísticas:")
        print(f"   Total de mudanças: {result.statistics['total_changes']}")
        print(f"   Adições: {result.statistics.get('additions', 0)}")
        print(f"   Remoções: {result.statistics.get('deletions', 0)}")
        print(f"   Modificações: {result.statistics.get('modifications', 0)}")
        print()
        print(f"⚠️  Severidade:")
        for severity, count in result.statistics.get('severity_breakdown', {}).items():
            emoji = "🔴" if severity == "CRITICAL" else "🟡" if severity == "MEDIUM" else "🟢"
            print(f"   {emoji} {severity}: {count}")
        print()
        print(f"⏱️  Tempo de processamento: {result.processing_time_seconds:.2f}s")
        print(f"📄 Relatório salvo em: {result.report_path}")
        print()
        print(f"Para visualizar o relatório:")
        if args.format == "markdown":
            print(f"   cat {result.report_path}")
        elif args.format == "html":
            print(f"   open {result.report_path}")
        else:
            print(f"   cat {result.report_path} | jq .")

        return 0

    except Exception as e:
        print("=" * 60)
        print("❌ ERRO DURANTE A COMPARAÇÃO")
        print("=" * 60)
        print(f"Erro: {type(e).__name__}: {e}")
        print()
        print("Dicas:")
        print("  - Verifique se os PDFs estão corrompidos")
        print("  - Tente usar --no-ocr se os PDFs forem nativos")
        print("  - Use --fast para pular análise semântica")
        return 1


if __name__ == "__main__":
    sys.exit(main())
