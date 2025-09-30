# Feature 8: Comparação de Tabelas

**Prioridade:** P1 (Desirable)
**Sprint:** Semana 3, Dia 13
**Estimativa:** 5 story points
**Dependências:** Feature 4 (Extração de Tabelas)

## Objetivo

Comparar tabelas numéricas extraídas célula por célula, detectar mudanças em valores com tolerância configurável, identificar linhas/colunas adicionadas ou removidas, e destacar mudanças em headers de tabelas (nomes de colunas) para análise de especificações técnicas.

## User Stories

### US-024: Comparação Célula por Célula
**Como** engenheiro de produto
**Eu quero** comparar tabelas numéricas célula por célula entre duas versões
**Para que** eu identifique exatamente quais valores foram alterados em especificações técnicas

**Critérios de Aceite:**
- [ ] Função `compare_tables(table_a: pd.DataFrame, table_b: pd.DataFrame) -> dict` implementada em `src/table_comparator.py`
- [ ] Alinhamento de tabelas por headers (match de colunas por nome)
- [ ] Comparação célula por célula: identificar valores alterados, adicionados, removidos
- [ ] Retorna dict com diferenças: `{"cell_changes": [...], "row_changes": {...}, "column_changes": {...}}`
- [ ] Tempo de comparação <5 segundos para tabela 20x10 (200 células)

**Definição de Pronto:**
- [ ] Código implementado em `src/table_comparator.py`
- [ ] Testes manuais executados (tabelas ASTM de composição química)
- [ ] Documentado no notebook (célula "7. Comparação de Tabelas")

**Estimativa:** 3 story points

---

### US-025: Tolerância Numérica Configurável
**Como** engenheiro de produto
**Eu quero** configurar tolerância aceitável para variações numéricas (ex: ±0.01)
**Para que** mudanças insignificantes dentro da margem de erro não sejam reportadas como diferenças

**Critérios de Aceite:**
- [ ] Parâmetro `tolerance: float` adicionado a `compare_tables()` (default: 0.01)
- [ ] Valores numéricos comparados com tolerância: `abs(val_a - val_b) <= tolerance` → considerado igual
- [ ] Diferenças dentro da tolerância não incluídas no output
- [ ] Log exibido: "5 mudanças detectadas, 2 dentro da tolerância (ignoradas)"
- [ ] Testado com mudança 5.00 → 5.01 (tolerância 0.05) → deve ser ignorada

**Definição de Pronto:**
- [ ] Código implementado em `src/table_comparator.py`
- [ ] Testes manuais executados (mudanças dentro e fora da tolerância)
- [ ] Documentado no notebook

**Estimativa:** 1 story point

---

### US-026: Detecção de Linhas/Colunas Adicionadas ou Removidas
**Como** engenheiro de produto
**Eu quero** identificar quando linhas ou colunas inteiras foram adicionadas ou removidas
**Para que** eu entenda mudanças estruturais na tabela (novos grades, novos elementos)

**Critérios de Aceite:**
- [ ] Comparação de headers: colunas em table_b não presentes em table_a → marcadas como "added"
- [ ] Colunas em table_a não presentes em table_b → marcadas como "removed"
- [ ] Comparação de índices: linhas adicionadas/removidas identificadas
- [ ] Output inclui: `{"added_columns": ["Silicon"], "removed_columns": [], "added_rows": [5, 7]}`
- [ ] Testado com tabela ASTM com coluna "Silicon" adicionada

**Definição de Pronto:**
- [ ] Código implementado em `src/table_comparator.py`
- [ ] Testes manuais executados (colunas e linhas adicionadas/removidas)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

## Atividades Técnicas

### Atividade Macro 1: Alinhamento de Tabelas por Headers
**Subatividades:**
1. [ ] Criar arquivo `src/table_comparator.py` com imports (pandas, numpy, logging) (arquivo: `src/table_comparator.py`)
2. [ ] Implementar `compare_tables(table_a: pd.DataFrame, table_b: pd.DataFrame, tolerance: float = 0.01) -> dict` (arquivo: `src/table_comparator.py`)
3. [ ] Normalizar headers: `.str.strip().str.lower()` para matching robusto (arquivo: `src/table_comparator.py`)
4. [ ] Identificar colunas comuns: `common_cols = set(table_a.columns) & set(table_b.columns)` (arquivo: `src/table_comparator.py`)
5. [ ] Alinhar DataFrames: `table_a_aligned = table_a[common_cols]` (arquivo: `src/table_comparator.py`)
6. [ ] Testar com tabelas ASTM com headers idênticos (teste manual)

### Atividade Macro 2: Comparação Célula por Célula
**Subatividades:**
1. [ ] Implementar `detect_cell_changes(table_a, table_b, tolerance) -> list` (arquivo: `src/table_comparator.py`)
2. [ ] Iterar sobre células comuns: `for row in range(min(len(table_a), len(table_b))): for col in common_cols:` (arquivo: `src/table_comparator.py`)
3. [ ] Extrair valores: `val_a = table_a.iloc[row][col]`, `val_b = table_b.iloc[row][col]` (arquivo: `src/table_comparator.py`)
4. [ ] Comparar numéricos com tolerância: `if abs(val_a - val_b) > tolerance: # diferença detectada` (arquivo: `src/table_comparator.py`)
5. [ ] Armazenar diferenças: `{"row": row, "column": col, "old_value": val_a, "new_value": val_b, "delta": val_b - val_a}` (arquivo: `src/table_comparator.py`)
6. [ ] Testar com tabela de composição química (teste manual)

### Atividade Macro 3: Aplicação de Tolerância Numérica
**Subatividades:**
1. [ ] Validar se valores são numéricos: `isinstance(val, (int, float))` (arquivo: `src/table_comparator.py`)
2. [ ] Aplicar tolerância apenas em valores numéricos (arquivo: `src/table_comparator.py`)
3. [ ] Strings comparadas com exact match (tolerância não aplicável) (arquivo: `src/table_comparator.py`)
4. [ ] Logar diferenças ignoradas: "2 mudanças dentro da tolerância (±0.01)" (arquivo: `src/table_comparator.py`)
5. [ ] Testar com mudança 0.40 → 0.41 (tolerância 0.05) → deve ser ignorada (teste manual)

### Atividade Macro 4: Detecção de Mudanças Estruturais
**Subatividades:**
1. [ ] Implementar `detect_structural_changes(table_a, table_b) -> dict` (arquivo: `src/table_comparator.py`)
2. [ ] Colunas adicionadas: `added_cols = set(table_b.columns) - set(table_a.columns)` (arquivo: `src/table_comparator.py`)
3. [ ] Colunas removidas: `removed_cols = set(table_a.columns) - set(table_b.columns)` (arquivo: `src/table_comparator.py`)
4. [ ] Linhas adicionadas: `added_rows = list(range(len(table_a), len(table_b)))` se table_b maior (arquivo: `src/table_comparator.py`)
5. [ ] Linhas removidas: `removed_rows = list(range(len(table_b), len(table_a)))` se table_a maior (arquivo: `src/table_comparator.py`)
6. [ ] Retornar dict: `{"added_columns": [...], "removed_columns": [...], "added_rows": [...], "removed_rows": [...]}` (arquivo: `src/table_comparator.py`)
7. [ ] Testar com tabela com coluna "Silicon" adicionada (teste manual)

---

## Critérios de Testes

### Teste 1: Comparação de Tabela com Mudança Numérica
**Entrada:** Tabela A (Grade 1020: Carbon=0.40%) vs Tabela B (Grade 1020: Carbon=0.42%)
**Ação:** Executar:
```python
from src.table_comparator import compare_tables
import pandas as pd

table_a = pd.DataFrame({"Grade": ["1020"], "Carbon": [0.40], "Manganese": [0.60]})
table_b = pd.DataFrame({"Grade": ["1020"], "Carbon": [0.42], "Manganese": [0.60]})

diffs = compare_tables(table_a, table_b, tolerance=0.01)
print(diffs["cell_changes"])
```
**Saída Esperada:** 1 mudança detectada: `{"row": 0, "column": "Carbon", "old_value": 0.40, "new_value": 0.42, "delta": 0.02}`

### Teste 2: Tolerância Numérica Ignora Mudança Pequena
**Entrada:** Tabela A (Carbon=5.00) vs Tabela B (Carbon=5.01), tolerância=0.05
**Ação:** Executar comparação com tolerância
**Saída Esperada:** 0 mudanças detectadas, log: "1 mudança dentro da tolerância (±0.05)"

### Teste 3: Detecção de Coluna Adicionada
**Entrada:** Tabela A (colunas: Grade, Carbon, Manganese) vs Tabela B (colunas: Grade, Carbon, Manganese, Silicon)
**Ação:** Executar:
```python
structural_changes = detect_structural_changes(table_a, table_b)
print(structural_changes["added_columns"])
```
**Saída Esperada:** `["Silicon"]`

### Teste 4: Performance de Comparação de Tabela Grande
**Entrada:** Tabela 20x10 (200 células) com 5 mudanças
**Ação:** Executar com `%%time`:
```python
%%time
diffs = compare_tables(large_table_a, large_table_b)
```
**Saída Esperada:** Tempo de execução <5 segundos

---

## Riscos e Mitigações

- **Risco 1:** Headers com nomes ligeiramente diferentes (ex: "Carbon %" vs "Carbon") não alinham → **Mitigação:** Normalizar headers (remover espaços, símbolos, lowercase); usar fuzzy matching de headers com threshold 0.9
- **Risco 2:** Tabelas com estruturas completamente diferentes (não há colunas comuns) → **Mitigação:** Logar warning "Tabelas incomparáveis (0 colunas comuns)"; retornar resultado vazio; documentar limitação
- **Risco 3:** Valores numéricos em formato string (ex: "0.40%" em vez de 0.40) → **Mitigação:** Implementar parsing: remover símbolos (%, mm), converter para float; logar conversões
- **Risco 4:** Tolerância inapropriada para diferentes grandezas (0.01 OK para %, ruim para temperaturas em °C) → **Mitigação:** Documentar necessidade de ajuste manual de tolerância; permitir tolerância por coluna (avançado)

---

## Métricas de Sucesso

- Taxa de detecção de mudanças: 100% de mudanças numéricas >tolerância detectadas
- Precisão de alinhamento de headers: ≥95% (validado em 10 tabelas)
- Performance: <5 segundos para tabela 20x10 (200 células)
- Robustez a formatos: ≥80% de valores string parseáveis para float
- Detecção estrutural: 100% de colunas/linhas adicionadas/removidas identificadas
