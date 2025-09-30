# Feature 4: Extração de Tabelas

**Prioridade:** P1 (Desirable)
**Sprint:** Semana 1, Dia 4
**Estimativa:** 5 story points
**Dependências:** Feature 2 (Ingestão de PDFs)

## Objetivo

Extrair tabelas numéricas de PDFs técnicos usando pdfplumber de forma seletiva (apenas páginas com tabelas detectadas), convertendo-as para DataFrames pandas estruturados para permitir comparação célula por célula na etapa posterior.

## User Stories

### US-011: Detecção de Páginas com Tabelas
**Como** desenvolvedor
**Eu quero** identificar quais páginas contêm tabelas antes de processar
**Para que** eu use pdfplumber seletivamente e evite processamento desnecessário (otimização de performance)

**Critérios de Aceite:**
- [ ] Função `detect_table_pages(pdf_doc: fitz.Document) -> list[int]` implementada
- [ ] Retorna lista de números de páginas contendo tabelas (ex: `[3, 7, 12]`)
- [ ] Heurística: detecta bordas de células via análise de linhas horizontais/verticais no PDF
- [ ] Tempo de detecção <5 segundos para PDF 25MB
- [ ] Testado com ASTM (tabelas de composição química típicas)

**Definição de Pronto:**
- [ ] Código implementado em `src/table_extractor.py`
- [ ] Testes manuais executados (validação com PDFs ASTM)
- [ ] Documentado no notebook (célula "3. Extração de Tabelas")

**Estimativa:** 2 story points

---

### US-012: Extração de Tabelas com pdfplumber
**Como** desenvolvedor
**Eu quero** extrair tabelas de páginas detectadas e convertê-las para DataFrames
**Para que** eu tenha dados tabulares estruturados para comparação numérica

**Critérios de Aceite:**
- [ ] Função `extract_tables(pdf_path: str, table_pages: list[int]) -> dict[int, list[pd.DataFrame]]` implementada
- [ ] Usa `pdfplumber.open(pdf_path)` apenas em páginas com tabelas
- [ ] Converte cada tabela para DataFrame pandas com headers corretos
- [ ] Retorna dict mapeando número de página → lista de DataFrames extraídos
- [ ] Tempo de extração <30 segundos para 10 tabelas (3 segundos/tabela)

**Definição de Pronto:**
- [ ] Código implementado em `src/table_extractor.py`
- [ ] Testes manuais executados (tabelas ASTM extraídas corretamente)
- [ ] Documentado no notebook

**Estimativa:** 3 story points

---

### US-013: Tratamento de Tabelas Malformadas
**Como** desenvolvedor
**Eu quero** registrar tabelas que não puderam ser parseadas sem crashear pipeline
**Para que** eu possa revisar manualmente casos problemáticos posteriormente

**Critérios de Aceite:**
- [ ] Try/except implementado em torno de `page.extract_tables()`
- [ ] Tabelas falhas registradas em log: "WARN: Tabela na página X não pôde ser extraída"
- [ ] Pipeline continua processando páginas restantes
- [ ] Contador de tabelas extraídas vs falhas exibido ao final
- [ ] Testado com PDF contendo tabela complexa (células mescladas)

**Definição de Pronto:**
- [ ] Código implementado em `src/table_extractor.py`
- [ ] Testes manuais executados (tabela problemática simulada)
- [ ] Documentado no notebook

**Estimativa:** 1 story point

---

## Atividades Técnicas

### Atividade Macro 1: Detecção de Tabelas via PyMuPDF
**Subatividades:**
1. [ ] Criar arquivo `src/table_extractor.py` com imports (PyMuPDF, pdfplumber, pandas) (arquivo: `src/table_extractor.py`)
2. [ ] Implementar `detect_table_pages(pdf_doc: fitz.Document) -> list[int]` (arquivo: `src/table_extractor.py`)
3. [ ] Iterar sobre páginas e analisar drawings (linhas) com `page.get_drawings()` (arquivo: `src/table_extractor.py`)
4. [ ] Heurística: se página tem >10 linhas horizontais e >5 verticais, marca como tabela (arquivo: `src/table_extractor.py`)
5. [ ] Retornar lista de page_nums com tabelas detectadas (arquivo: `src/table_extractor.py`)
6. [ ] Testar com ASTM 2015 e validar manualmente páginas detectadas (teste manual)

### Atividade Macro 2: Extração com pdfplumber
**Subatividades:**
1. [ ] Implementar `extract_tables(pdf_path: str, table_pages: list[int]) -> dict` (arquivo: `src/table_extractor.py`)
2. [ ] Abrir PDF com pdfplumber: `pdf = pdfplumber.open(pdf_path)` (arquivo: `src/table_extractor.py`)
3. [ ] Iterar apenas sobre páginas em `table_pages` (arquivo: `src/table_extractor.py`)
4. [ ] Extrair tabelas: `tables = pdf.pages[page_num].extract_tables()` (arquivo: `src/table_extractor.py`)
5. [ ] Converter cada tabela para DataFrame: `pd.DataFrame(table[1:], columns=table[0])` (arquivo: `src/table_extractor.py`)
6. [ ] Testar com tabela ASTM de composição química (teste manual)

### Atividade Macro 3: Tratamento de Erros
**Subatividades:**
1. [ ] Envolver `extract_tables()` em try/except capturando `IndexError` e `ValueError` (arquivo: `src/table_extractor.py`)
2. [ ] Logar erro com `logging.warning(f"Tabela na página {page_num} falhou: {str(e)}")` (arquivo: `src/table_extractor.py`)
3. [ ] Continuar processamento (não interromper pipeline) (arquivo: `src/table_extractor.py`)
4. [ ] Retornar lista vazia para página com falha (arquivo: `src/table_extractor.py`)
5. [ ] Testar com PDF contendo tabela com células mescladas (caso problemático) (teste manual)

### Atividade Macro 4: Visualização de Tabelas Extraídas
**Subatividades:**
1. [ ] Implementar `display_extracted_tables(tables: dict) -> None` (arquivo: `src/table_extractor.py`)
2. [ ] Iterar sobre tabelas extraídas e exibir com `IPython.display.display(df)` (arquivo: `src/table_extractor.py`)
3. [ ] Adicionar headers: "Página X - Tabela Y" (arquivo: `src/table_extractor.py`)
4. [ ] Exibir resumo: "Total: N tabelas extraídas, M falhas" (arquivo: `src/table_extractor.py`)
5. [ ] Testar visualização no notebook (teste manual)

---

## Critérios de Testes

### Teste 1: Detecção de Páginas com Tabelas
**Entrada:** PDF ASTM 2015 com 3 tabelas em páginas 5, 8, 12
**Ação:** Executar:
```python
from src.pdf_loader import load_pdf
from src.table_extractor import detect_table_pages
pdf_doc = load_pdf("data/inputs/astm_2015.pdf")
table_pages = detect_table_pages(pdf_doc)
print(f"Páginas com tabelas: {table_pages}")
```
**Saída Esperada:** Lista `[5, 8, 12]` (ou próximo, validar manualmente se correto)

### Teste 2: Extração de Tabelas para DataFrames
**Entrada:** Path para ASTM 2015, lista de páginas `[5, 8, 12]`
**Ação:** Executar:
```python
from src.table_extractor import extract_tables
tables = extract_tables("data/inputs/astm_2015.pdf", [5, 8, 12])
for page, dfs in tables.items():
    print(f"Página {page}: {len(dfs)} tabelas extraídas")
    print(dfs[0].head())  # Primeira tabela da página
```
**Saída Esperada:**
- Página 5: 1 tabela extraída, DataFrame com headers (Grade, Carbon, Manganese, ...) e valores numéricos
- DataFrame displayado com formatação legível no notebook

### Teste 3: Tratamento de Tabela Malformada
**Entrada:** PDF com tabela complexa (células mescladas, bordas ausentes)
**Ação:** Executar extração em página problemática
**Saída Esperada:** Log warning "WARN: Tabela na página X não pôde ser extraída", pipeline continua sem crash, contador exibe "2 tabelas extraídas, 1 falha"

### Teste 4: Performance de Extração
**Entrada:** PDF com 10 tabelas simples
**Ação:** Executar com `%%time`:
```python
%%time
tables = extract_tables(pdf_path, table_pages)
```
**Saída Esperada:** Tempo de execução ≤30 segundos (target: 2-3 segundos/tabela)

---

## Riscos e Mitigações

- **Risco 1:** pdfplumber falha em tabelas sem bordas (implicit grids) → **Mitigação:** Usar strategy "text" em vez de "lines"; ajustar tolerância de detecção; documentar limitação
- **Risco 2:** Detecção de tabelas tem falsos positivos (gráficos confundidos com tabelas) → **Mitigação:** Refinar heurística (ratio linhas H/V, densidade); validar manualmente 10 páginas
- **Risco 3:** Headers de tabelas extraídos incorretamente (valores como headers) → **Mitigação:** Implementar heurística: se primeira linha tem >50% valores numéricos, não é header
- **Risco 4:** Performance pdfplumber <3 segundos/tabela (risco de exceder 30 segundos) → **Mitigação:** Processar tabelas em paralelo (multiprocessing); usar detecção seletiva mais rigorosa

---

## Métricas de Sucesso

- Taxa de detecção de tabelas: ≥90% (validado em 20 páginas conhecidas com tabelas)
- Taxa de extração bem-sucedida: ≥80% para tabelas grid simples (bordas claras)
- Performance: ≤3 segundos por tabela (target: 2 segundos)
- Qualidade de DataFrames: Headers corretos em ≥90% dos casos
- Robustez: 100% de tabelas falhas logadas sem crash de pipeline
