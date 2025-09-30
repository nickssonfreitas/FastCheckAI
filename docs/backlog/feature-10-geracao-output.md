# Feature 10: Geração de Output

**Prioridade:** P0 (Essential)
**Sprint:** Semana 3, Dias 14-15
**Estimativa:** 5 story points
**Dependências:** Feature 9 (Classificação de Severidade)

## Objetivo

Gerar DataFrame pandas estruturado com todas as diferenças detectadas, exibir visualização elaborada no notebook com highlights coloridos, fornecer estatísticas resumidas (total, distribuição por severidade) e permitir fácil navegação e revisão dos resultados da comparação.

## User Stories

### US-030: Geração de DataFrame Estruturado
**Como** engenheiro de produto
**Eu quero** visualizar todas as diferenças em DataFrame pandas com colunas padronizadas
**Para que** eu possa filtrar, ordenar e exportar resultados facilmente

**Critérios de Aceite:**
- [ ] Função `generate_dataframe(diffs: list[dict]) -> pd.DataFrame` implementada em `src/output_generator.py`
- [ ] Colunas obrigatórias: `["ID", "Section", "Type", "Severity", "Original", "Modified", "Semantic_Classification", "Reasoning"]`
- [ ] Cada diferença é uma linha do DataFrame
- [ ] DataFrame ordenado por severidade (CRITICAL primeiro) e depois por seção
- [ ] DataFrame exibido com formatação legível (truncamento de texto longo, cores por severidade)

**Definição de Pronto:**
- [ ] Código implementado em `src/output_generator.py`
- [ ] Testes manuais executados (DataFrame gerado corretamente)
- [ ] Documentado no notebook (célula "9. Geração de Output")

**Estimativa:** 2 story points

---

### US-031: Visualização Elaborada com Highlights
**Como** engenheiro de produto
**Eu quero** visualizar diferenças com formatação rica (cores, negrito, highlights)
**Para que** eu identifique rapidamente mudanças importantes sem ler texto bruto

**Critérios de Aceite:**
- [ ] Função `display_differences(df: pd.DataFrame) -> None` implementada
- [ ] Renderização HTML/Markdown inline no notebook com `IPython.display`
- [ ] Cores por severidade: CRITICAL=vermelho, MEDIUM=amarelo, LOW=cinza
- [ ] Highlights em valores numéricos alterados (negrito)
- [ ] Seções colapsáveis (accordion) para cada diferença (opcional, se tempo permitir)
- [ ] Legível e profissional (sem poluição visual)

**Definição de Pronto:**
- [ ] Código implementado em `src/output_generator.py`
- [ ] Testes manuais executados (visualização clara e legível)
- [ ] Documentado no notebook

**Estimativa:** 3 story points

---

### US-032: Estatísticas Resumidas
**Como** engenheiro de produto
**Eu quero** ver estatísticas resumidas no topo do output
**Para que** eu tenha visão geral rápida dos resultados antes de revisar diferenças individuais

**Critérios de Aceite:**
- [ ] Função `display_summary(df: pd.DataFrame) -> None` implementada
- [ ] Exibição de:
  - Total de diferenças detectadas
  - Distribuição por severidade (contagem + percentual)
  - Distribuição por tipo (adição, remoção, modificação)
  - Seções mais impactadas (top 5 seções com mais mudanças)
- [ ] Formatação clara e concisa (box ou tabela)
- [ ] Tempo de geração <2 segundos

**Definição de Pronto:**
- [ ] Código implementado em `src/output_generator.py`
- [ ] Testes manuais executados (estatísticas corretas)
- [ ] Documentado no notebook

**Estimativa:** 1 story point

---

## Atividades Técnicas

### Atividade Macro 1: Geração de DataFrame Estruturado
**Subatividades:**
1. [ ] Criar arquivo `src/output_generator.py` com imports (pandas, IPython.display, logging) (arquivo: `src/output_generator.py`)
2. [ ] Implementar `generate_dataframe(diffs: list[dict]) -> pd.DataFrame` (arquivo: `src/output_generator.py`)
3. [ ] Criar lista de dicts com colunas padronizadas (arquivo: `src/output_generator.py`):
   ```python
   rows = []
   for idx, diff in enumerate(diffs, 1):
       rows.append({
           "ID": f"DIFF-{idx:03d}",
           "Section": diff.get("section_id", "N/A"),
           "Type": diff.get("type", "modification"),
           "Severity": diff.get("severity", "MEDIUM"),
           "Original": diff.get("original", "")[:200],  # Truncar
           "Modified": diff.get("content", "")[:200],
           "Semantic_Classification": diff.get("semantic_classification", "N/A"),
           "Reasoning": diff.get("reasoning", "")[:300]
       })
   df = pd.DataFrame(rows)
   ```
4. [ ] Ordenar DataFrame: primeiro por severidade (CRITICAL > MEDIUM > LOW), depois por seção (arquivo: `src/output_generator.py`)
5. [ ] Testar com 30 diferenças (teste manual)

### Atividade Macro 2: Visualização com Formatação HTML
**Subatividades:**
1. [ ] Implementar `display_differences(df: pd.DataFrame) -> None` (arquivo: `src/output_generator.py`)
2. [ ] Criar função auxiliar `severity_to_color(severity: str) -> str` retornando códigos HTML (arquivo: `src/output_generator.py`):
   - CRITICAL → `#ff4444` (vermelho)
   - MEDIUM → `#ffcc00` (amarelo)
   - LOW → `#cccccc` (cinza)
3. [ ] Gerar HTML customizado para cada linha do DataFrame (arquivo: `src/output_generator.py`):
   ```python
   html = "<div style='margin-bottom:20px'>"
   html += f"<div style='background-color:{color}; padding:10px; border-radius:5px'>"
   html += f"<b>[{row['Severity']}]</b> {row['Section']} - {row['Type']}"
   html += "</div>"
   html += f"<p><b>Original:</b> {row['Original']}</p>"
   html += f"<p><b>Modified:</b> {row['Modified']}</p>"
   html += f"<p><i>{row['Reasoning']}</i></p>"
   html += "</div>"
   ```
4. [ ] Renderizar com `IPython.display.HTML(html)` (arquivo: `src/output_generator.py`)
5. [ ] Testar visualização no notebook (deve ser legível e colorida) (teste manual)

### Atividade Macro 3: Estatísticas Resumidas
**Subatividades:**
1. [ ] Implementar `display_summary(df: pd.DataFrame) -> None` (arquivo: `src/output_generator.py`)
2. [ ] Calcular estatísticas (arquivo: `src/output_generator.py`):
   - Total: `len(df)`
   - Por severidade: `df['Severity'].value_counts()`
   - Por tipo: `df['Type'].value_counts()`
   - Top seções: `df['Section'].value_counts().head(5)`
3. [ ] Formatar output como texto estruturado (arquivo: `src/output_generator.py`):
   ```
   === RESUMO DE DIFERENÇAS ===
   Total: 25 diferenças detectadas

   Distribuição por Severidade:
   - CRITICAL: 5 (20%)
   - MEDIUM: 12 (48%)
   - LOW: 8 (32%)

   Distribuição por Tipo:
   - Modificação: 18 (72%)
   - Adição: 5 (20%)
   - Remoção: 2 (8%)

   Seções Mais Impactadas:
   1. 3.2 Chemical Composition (7 mudanças)
   2. 5.1 Tensile Requirements (4 mudanças)
   3. 1 Scope (3 mudanças)
   ```
4. [ ] Renderizar com Markdown ou HTML box (arquivo: `src/output_generator.py`)
5. [ ] Testar com 30 diferenças (teste manual)

### Atividade Macro 4: Integração no Notebook Principal
**Subatividades:**
1. [ ] Criar célula notebook "9. Geração de Output" (arquivo: `notebooks/main_pipeline.ipynb`)
2. [ ] Importar e chamar funções de output generator (arquivo: `notebooks/main_pipeline.ipynb`):
   ```python
   from src.output_generator import generate_dataframe, display_summary, display_differences

   df_results = generate_dataframe(all_differences)
   display_summary(df_results)
   display_differences(df_results)
   ```
3. [ ] Adicionar opção de exportação (desejável, não essencial) (arquivo: `notebooks/main_pipeline.ipynb`):
   ```python
   # df_results.to_csv("outputs/astm_comparison_results.csv", index=False)
   # df_results.to_excel("outputs/astm_comparison_results.xlsx", index=False)
   ```
4. [ ] Testar execução completa do pipeline (teste manual)

---

## Critérios de Testes

### Teste 1: Geração de DataFrame com Colunas Corretas
**Entrada:** 25 diferenças com severidades variadas
**Ação:** Executar:
```python
from src.output_generator import generate_dataframe
df = generate_dataframe(all_diffs)
print(df.columns.tolist())
print(df.head(3))
```
**Saída Esperada:**
- Colunas: `["ID", "Section", "Type", "Severity", "Original", "Modified", "Semantic_Classification", "Reasoning"]`
- DataFrame com 25 linhas, IDs sequenciais (DIFF-001, DIFF-002, ...)

### Teste 2: Ordenação por Severidade
**Entrada:** DataFrame com mix de severidades
**Ação:** Verificar primeiras 5 linhas do DataFrame
**Saída Esperada:** Todas as linhas CRITICAL aparecem antes de MEDIUM, MEDIUM antes de LOW

### Teste 3: Visualização com Cores Corretas
**Entrada:** DataFrame com 3 diferenças (1 CRITICAL, 1 MEDIUM, 1 LOW)
**Ação:** Executar `display_differences(df)` no notebook
**Saída Esperada:** Visualização HTML com:
- Diferença CRITICAL em fundo vermelho (#ff4444)
- Diferença MEDIUM em fundo amarelo (#ffcc00)
- Diferença LOW em fundo cinza (#cccccc)

### Teste 4: Estatísticas Resumidas Corretas
**Entrada:** DataFrame com 25 diferenças (5 CRITICAL, 12 MEDIUM, 8 LOW)
**Ação:** Executar `display_summary(df)`
**Saída Esperada:** Resumo exibido:
```
Total: 25 diferenças
CRITICAL: 5 (20%)
MEDIUM: 12 (48%)
LOW: 8 (32%)
```

### Teste 5: Performance de Geração
**Entrada:** 100 diferenças
**Ação:** Executar com `%%time`:
```python
%%time
df = generate_dataframe(large_diffs)
display_summary(df)
display_differences(df)
```
**Saída Esperada:** Tempo total <5 segundos

---

## Riscos e Mitigações

- **Risco 1:** DataFrame muito grande (>1000 linhas) torna visualização lenta ou ilegível → **Mitigação:** Implementar paginação (exibir primeiras 50, botão "carregar mais"); otimizar renderização HTML; considerar exportação para arquivo
- **Risco 2:** Texto longo em colunas Original/Modified quebra formatação → **Mitigação:** Truncar texto em 200 caracteres com "..." (já implementado); adicionar tooltip hover para ver texto completo (avançado)
- **Risco 3:** Renderização HTML não funciona em todos os ambientes Jupyter → **Mitigação:** Fallback para display simples com `print(df.to_string())`; testar em JupyterLab e Jupyter Notebook classic
- **Risco 4:** Exportação para CSV/Excel com caracteres especiais (encoding) → **Mitigação:** Usar `encoding='utf-8-sig'` no to_csv; validar abertura no Excel

---

## Métricas de Sucesso

- Completude de DataFrame: 100% das diferenças incluídas com todas as colunas
- Legibilidade de visualização: Aprovada por stakeholder (sem ajustes necessários)
- Performance: <5 segundos para gerar e exibir 100 diferenças
- Acurácia de estatísticas: 100% (validado manualmente)
- Ordenação correta: 100% das diferenças CRITICAL no topo
