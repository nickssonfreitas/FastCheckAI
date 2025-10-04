"""
Report Generation Module for FastCheckAI

This module generates human-readable reports explaining the differences between
technical documents. It converts comparison data into structured Markdown reports
with executive summaries, statistics, and critical change analysis.

This addresses the user requirement: "Eu quero que o agente retorne para mim um
texto explicando as diferenças no documento" (I want the agent to return a text
explaining the differences in the document).

Example:
    >>> from src.report_generator import generate_report
    >>> report = generate_report(comparison_results)
    >>> print(report)  # Display markdown report with all differences explained
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# =============================================================================
# Report Formatting Constants
# =============================================================================

SEVERITY_EMOJIS = {
    "CRITICAL": "🔴",
    "SIGNIFICANT": "🟠",
    "MEDIUM": "🟡",
    "MINOR": "🟢",
    "EQUIVALENT": "⚪",
}

SEVERITY_DESCRIPTIONS = {
    "CRITICAL": "Mudança crítica que impacta requisitos técnicos fundamentais",
    "SIGNIFICANT": "Mudança significativa que altera especificações ou escopo",
    "MEDIUM": "Mudança moderada que pode afetar implementação",
    "MINOR": "Mudança editorial ou clarificação sem impacto técnico",
    "EQUIVALENT": "Mudança cosmética ou reformulação com mesmo significado",
}


# =============================================================================
# Header and Footer Functions
# =============================================================================


def generate_header(doc_a: str, doc_b: str) -> str:
    """
    Generate report header with document information.

    Parameters
    ----------
    doc_a : str
        Name/path of first document (original)
    doc_b : str
        Name/path of second document (modified)

    Returns
    -------
    str
        Markdown formatted header
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"""# 📊 Relatório de Comparação de Documentos Técnicos

**Sistema:** FastCheckAI - Análise Automatizada de Normas Técnicas
**Data/Hora:** {timestamp}
**Tecnologia:** Agno Framework + GPT-4o

---

## 📄 Documentos Analisados

- **Documento Original:** `{doc_a}`
- **Documento Modificado:** `{doc_b}`

---
"""
    return header


def generate_footer() -> str:
    """
    Generate report footer with metadata and disclaimers.

    Returns
    -------
    str
        Markdown formatted footer
    """
    footer = """
---

## 📝 Notas Finais

### Metodologia de Análise
- **Extração de Texto:** PyMuPDF com fallback OCR (Tesseract) para PDFs corrompidos
- **Alinhamento de Seções:** Algoritmo hierárquico com fuzzy matching (threshold: 0.8)
- **Comparação Textual:** difflib com detecção de termos críticos
- **Análise Semântica:** GPT-4o via Agno Framework (temperatura: 0.3)
- **Classificação de Severidade:** Baseada em impacto técnico e palavras-chave

### Limitações
- Análise focada em mudanças textuais (tabelas numéricas podem ter menor precisão)
- Classificação semântica depende do contexto fornecido ao LLM
- OCR pode introduzir erros em documentos escaneados de baixa qualidade

### Sobre o FastCheckAI
Proof of Concept desenvolvido para validar a viabilidade do Agno Framework na
comparação automatizada de normas técnicas ASTM. Sistema projetado para processar
documentos de até 25MB em menos de 3 minutos.

---

*Relatório gerado automaticamente pelo FastCheckAI v0.1.0*
"""
    return footer


# =============================================================================
# Executive Summary Generation
# =============================================================================


def generate_executive_summary(
    total_changes: int,
    critical_changes: int,
    significant_changes: int,
    minor_changes: int,
    sections_added: int,
    sections_removed: int,
) -> str:
    """
    Generate executive summary of comparison results.

    Parameters
    ----------
    total_changes : int
        Total number of changes detected
    critical_changes : int
        Number of critical changes
    significant_changes : int
        Number of significant changes
    minor_changes : int
        Number of minor changes
    sections_added : int
        Number of new sections
    sections_removed : int
        Number of removed sections

    Returns
    -------
    str
        Markdown formatted executive summary
    """
    # Determine overall assessment
    if critical_changes > 0:
        overall = "⚠️ **ATENÇÃO NECESSÁRIA**: Mudanças críticas detectadas que requerem análise detalhada."
    elif significant_changes > 5:
        overall = "📋 **REVISÃO RECOMENDADA**: Múltiplas mudanças significativas identificadas."
    elif total_changes > 20:
        overall = "📝 **ATUALIZAÇÃO SUBSTANCIAL**: Documento passou por revisão extensiva."
    else:
        overall = "✅ **MUDANÇAS MÍNIMAS**: Principalmente atualizações editoriais e clarificações."

    summary = f"""## 🎯 Sumário Executivo

### Visão Geral
{overall}

### Estatísticas Principais
- **Total de Mudanças Detectadas:** {total_changes}
- **Mudanças por Severidade:**
  - {SEVERITY_EMOJIS['CRITICAL']} Críticas: {critical_changes}
  - {SEVERITY_EMOJIS['SIGNIFICANT']} Significativas: {significant_changes}
  - {SEVERITY_EMOJIS['MINOR']} Menores: {minor_changes}
- **Alterações Estruturais:**
  - ➕ Seções Adicionadas: {sections_added}
  - ➖ Seções Removidas: {sections_removed}

### Recomendação
"""

    if critical_changes > 0:
        summary += """
**Ação Imediata Requerida:** As mudanças críticas identificadas podem impactar
conformidade, especificações técnicas ou requisitos mandatórios. Recomenda-se:
1. Revisar detalhadamente cada mudança crítica
2. Avaliar impacto em processos e produtos existentes
3. Atualizar documentação e treinamentos conforme necessário
"""
    elif significant_changes > 0:
        summary += """
**Revisão Cuidadosa Sugerida:** As mudanças significativas podem afetar
interpretação e aplicação da norma. Recomenda-se:
1. Analisar mudanças significativas com equipe técnica
2. Verificar necessidade de ajustes em procedimentos
3. Comunicar alterações relevantes aos stakeholders
"""
    else:
        summary += """
**Atualização de Rotina:** As mudanças são principalmente editoriais.
Recomenda-se:
1. Atualizar referências à versão da norma
2. Revisar mudanças menores para conhecimento
3. Arquivar relatório para auditoria futura
"""

    summary += "\n---\n"
    return summary


# =============================================================================
# Statistics Generation
# =============================================================================


def generate_statistics(comparison_results: List[Dict[str, Any]]) -> str:
    """
    Generate detailed statistics section.

    Parameters
    ----------
    comparison_results : list
        List of comparison result dictionaries

    Returns
    -------
    str
        Markdown formatted statistics
    """
    stats = """## 📈 Análise Estatística Detalhada

### Distribuição de Mudanças por Tipo
"""

    # Count changes by type
    additions = sum(1 for r in comparison_results if r.get("type") == "added")
    deletions = sum(1 for r in comparison_results if r.get("type") == "removed")
    modifications = sum(1 for r in comparison_results if r.get("type") == "modified")

    stats += f"""
| Tipo de Mudança | Quantidade | Percentual |
|-----------------|------------|------------|
| ➕ Adições | {additions} | {additions/max(len(comparison_results), 1)*100:.1f}% |
| ➖ Remoções | {deletions} | {deletions/max(len(comparison_results), 1)*100:.1f}% |
| 🔄 Modificações | {modifications} | {modifications/max(len(comparison_results), 1)*100:.1f}% |

### Distribuição por Seção
"""

    # Count changes by section
    section_counts: Dict[str, int] = {}
    for result in comparison_results:
        section = result.get("section_id", "Unknown")
        # Get top-level section (e.g., "1" from "1.2.3")
        top_section = section.split(".")[0] if section else "Unknown"
        section_counts[top_section] = section_counts.get(top_section, 0) + 1

    if section_counts:
        stats += "\n| Seção | Mudanças | Impacto |\n"
        stats += "|-------|----------|----------|\n"
        for section, count in sorted(section_counts.items()):
            impact = "Alto" if count > 5 else "Médio" if count > 2 else "Baixo"
            stats += f"| {section} | {count} | {impact} |\n"

    # Add confidence metrics if available
    confidences = [r.get("confidence", 0) for r in comparison_results if "confidence" in r]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        stats += f"""
### Métricas de Confiança
- **Confiança Média da Análise:** {avg_confidence:.1%}
- **Análises de Alta Confiança (>90%):** {sum(1 for c in confidences if c > 0.9)}
- **Análises de Baixa Confiança (<70%):** {sum(1 for c in confidences if c < 0.7)}
"""

    stats += "\n---\n"
    return stats


# =============================================================================
# Critical Analysis Generation
# =============================================================================


def generate_critical_analysis(
    comparison_results: List[Dict[str, Any]],
    max_items: int = 10
) -> str:
    """
    Generate critical changes analysis section.

    Parameters
    ----------
    comparison_results : list
        List of comparison result dictionaries
    max_items : int, default=10
        Maximum number of critical changes to display

    Returns
    -------
    str
        Markdown formatted critical analysis
    """
    analysis = """## 🔍 Análise de Mudanças Críticas

### Mudanças de Maior Impacto
"""

    # Filter and sort by severity
    critical_results = [
        r for r in comparison_results
        if r.get("severity") in ["CRITICAL", "SIGNIFICANT"]
    ]

    if not critical_results:
        analysis += "\n✅ **Nenhuma mudança crítica ou significativa detectada.**\n\n"
        return analysis + "---\n"

    # Sort by severity (CRITICAL first) and confidence
    critical_results.sort(
        key=lambda x: (
            0 if x.get("severity") == "CRITICAL" else 1,
            -x.get("confidence", 0)
        )
    )

    # Display top critical changes
    for i, result in enumerate(critical_results[:max_items], 1):
        severity = result.get("severity", "UNKNOWN")
        emoji = SEVERITY_EMOJIS.get(severity, "❓")
        section = result.get("section_id", "Unknown")
        title = result.get("section_title", "Sem título")

        analysis += f"\n#### {i}. {emoji} [{severity}] Seção {section}: {title}\n\n"

        # Add change description
        change_type = result.get("type", "modified")
        if change_type == "added":
            analysis += "**Tipo:** ➕ Nova seção adicionada\n\n"
        elif change_type == "removed":
            analysis += "**Tipo:** ➖ Seção removida\n\n"
        else:
            analysis += "**Tipo:** 🔄 Seção modificada\n\n"

        # Add semantic analysis if available
        if "semantic_analysis" in result:
            semantic = result["semantic_analysis"]
            classification = semantic.get("classification", "Unknown")
            reasoning = semantic.get("reasoning", "Análise não disponível")
            confidence = semantic.get("confidence", 0)

            analysis += f"**Classificação Semântica:** {classification}\n"
            analysis += f"**Confiança:** {confidence:.1%}\n"
            analysis += f"**Justificativa:** {reasoning}\n\n"

        # Add diff preview if available
        if "diff_preview" in result:
            analysis += "**Prévia das Mudanças:**\n```diff\n"
            analysis += result["diff_preview"][:500]  # Limit preview length
            if len(result["diff_preview"]) > 500:
                analysis += "\n... (truncado)"
            analysis += "\n```\n\n"

        # Add critical terms detected
        if "critical_terms" in result and result["critical_terms"]:
            terms = ", ".join(result["critical_terms"])
            analysis += f"⚠️ **Termos Críticos Detectados:** {terms}\n\n"

        analysis += "---\n"

    if len(critical_results) > max_items:
        analysis += f"\n*Mostrando {max_items} de {len(critical_results)} mudanças críticas/significativas.*\n\n"

    return analysis


# =============================================================================
# Section Changes Report
# =============================================================================


def generate_section_changes(
    sections_added: List[Dict[str, str]],
    sections_removed: List[Dict[str, str]]
) -> str:
    """
    Generate report section for added/removed sections.

    Parameters
    ----------
    sections_added : list
        List of added sections with id and title
    sections_removed : list
        List of removed sections with id and title

    Returns
    -------
    str
        Markdown formatted section changes
    """
    report = "## 📂 Alterações Estruturais\n\n"

    if sections_added:
        report += "### ➕ Seções Adicionadas\n\n"
        for section in sections_added:
            section_id = section.get("id", "Unknown")
            title = section.get("title", "Sem título")
            report += f"- **{section_id}:** {title}\n"
        report += "\n"

    if sections_removed:
        report += "### ➖ Seções Removidas\n\n"
        for section in sections_removed:
            section_id = section.get("id", "Unknown")
            title = section.get("title", "Sem título")
            report += f"- **{section_id}:** {title}\n"
        report += "\n"

    if not sections_added and not sections_removed:
        report += "*Nenhuma alteração estrutural detectada.*\n\n"

    report += "---\n"
    return report


# =============================================================================
# Main Report Generation Function
# =============================================================================


def generate_report(
    comparison_results: List[Dict[str, Any]],
    doc_a: str = "Documento Original",
    doc_b: str = "Documento Modificado",
    include_statistics: bool = True,
    include_critical_analysis: bool = True,
    max_critical_items: int = 10
) -> str:
    """
    Generate complete comparison report in Markdown format.

    This is the main entry point that creates a human-readable report
    explaining all differences between documents, as requested by the user:
    "Eu quero que o agente retorne para mim um texto explicando as diferenças"

    Parameters
    ----------
    comparison_results : list
        List of dictionaries containing comparison results with keys:
        - section_id: Section identifier
        - section_title: Section title
        - type: "added" | "removed" | "modified"
        - severity: "CRITICAL" | "SIGNIFICANT" | "MINOR"
        - semantic_analysis: Dict with classification, confidence, reasoning
        - diff_preview: String with diff preview
        - critical_terms: List of critical terms found
    doc_a : str, default="Documento Original"
        Name/path of first document
    doc_b : str, default="Documento Modificado"
        Name/path of second document
    include_statistics : bool, default=True
        Whether to include detailed statistics section
    include_critical_analysis : bool, default=True
        Whether to include critical changes analysis
    max_critical_items : int, default=10
        Maximum number of critical changes to show

    Returns
    -------
    str
        Complete Markdown formatted report

    Examples
    --------
    >>> from src.report_generator import generate_report
    >>> results = [
    ...     {
    ...         "section_id": "1.1",
    ...         "section_title": "Scope",
    ...         "type": "modified",
    ...         "severity": "CRITICAL",
    ...         "semantic_analysis": {
    ...             "classification": "SIGNIFICANT",
    ...             "confidence": 0.95,
    ...             "reasoning": "Change from mandatory to optional requirement"
    ...         }
    ...     }
    ... ]
    >>> report = generate_report(results, "astm_2015.pdf", "astm_2016.pdf")
    >>> print(report)  # Displays formatted Markdown report
    """
    logger.info(f"Generating report for {len(comparison_results)} comparison results")

    # Calculate summary statistics
    total_changes = len(comparison_results)
    critical_changes = sum(1 for r in comparison_results if r.get("severity") == "CRITICAL")
    significant_changes = sum(1 for r in comparison_results if r.get("severity") == "SIGNIFICANT")
    minor_changes = sum(1 for r in comparison_results if r.get("severity") == "MINOR")

    # Separate added/removed sections
    sections_added = [r for r in comparison_results if r.get("type") == "added"]
    sections_removed = [r for r in comparison_results if r.get("type") == "removed"]

    # Build report sections
    report_parts = []

    # Header
    report_parts.append(generate_header(doc_a, doc_b))

    # Executive Summary
    report_parts.append(generate_executive_summary(
        total_changes,
        critical_changes,
        significant_changes,
        minor_changes,
        len(sections_added),
        len(sections_removed)
    ))

    # Statistics
    if include_statistics and comparison_results:
        report_parts.append(generate_statistics(comparison_results))

    # Critical Analysis
    if include_critical_analysis and comparison_results:
        report_parts.append(generate_critical_analysis(
            comparison_results,
            max_critical_items
        ))

    # Section Changes
    if sections_added or sections_removed:
        report_parts.append(generate_section_changes(
            sections_added,
            sections_removed
        ))

    # Footer
    report_parts.append(generate_footer())

    # Combine all parts
    full_report = "\n".join(report_parts)

    logger.info(f"Report generated successfully ({len(full_report)} characters)")

    return full_report


# =============================================================================
# Utility Functions
# =============================================================================


def format_for_display(report: str) -> str:
    """
    Format report for display in Jupyter Notebook using IPython.display.

    Parameters
    ----------
    report : str
        Markdown report content

    Returns
    -------
    str
        Report ready for IPython.display.Markdown()

    Examples
    --------
    >>> from IPython.display import Markdown, display
    >>> from src.report_generator import generate_report, format_for_display
    >>> report = generate_report(results)
    >>> display(Markdown(format_for_display(report)))
    """
    # Ensure proper line breaks for Jupyter rendering
    formatted = report.replace("\n\n\n", "\n\n")
    formatted = formatted.replace("```\n\n", "```\n")

    return formatted


def save_report(report: str, output_path: str) -> None:
    """
    Save report to a Markdown file.

    Parameters
    ----------
    report : str
        Markdown report content
    output_path : str
        Path where to save the report

    Examples
    --------
    >>> from src.report_generator import generate_report, save_report
    >>> report = generate_report(results)
    >>> save_report(report, "data/outputs/comparison_report.md")
    """
    from pathlib import Path

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Report saved to {output_path}")


def get_severity_from_semantic(semantic_classification: str) -> str:
    """
    Map semantic classification to severity level.

    Parameters
    ----------
    semantic_classification : str
        "EQUIVALENT" | "MINOR" | "SIGNIFICANT"

    Returns
    -------
    str
        "MINOR" | "MEDIUM" | "CRITICAL"
    """
    mapping = {
        "EQUIVALENT": "MINOR",
        "MINOR": "MEDIUM",
        "SIGNIFICANT": "CRITICAL"
    }
    return mapping.get(semantic_classification, "MEDIUM")
