# Feature 3: Extração de Texto

**Prioridade:** P0 (Essential)
**Sprint:** Semana 1, Dias 2-4
**Estimativa:** 8 story points
**Dependências:** Feature 2 (Ingestão de PDFs)

## Objetivo

Extrair texto completo de PDFs nativos preservando hierarquia de seções (capítulos, subseções) e estrutura de parágrafos, utilizando PyMuPDF para performance máxima e preparando dados estruturados para alinhamento e comparação.

## User Stories

### US-008: Extração Rápida de Texto com PyMuPDF
**Como** desenvolvedor
**Eu quero** extrair texto de PDFs nativos em até 60 segundos para 25MB
**Para que** o pipeline atenda target de ≤3 minutos end-to-end

**Critérios de Aceite:**
- [ ] Função `extract_text(pdf_doc: fitz.Document) -> str` implementada em `src/text_extractor.py`
- [ ] Usa `page.get_text("text")` do PyMuPDF para extração rápida
- [ ] Processa todas as páginas do PDF sequencialmente
- [ ] Retorna texto completo concatenado com separadores de página
- [ ] Tempo de extração <60 segundos para PDF 25MB (≥2 páginas/segundo)

**Definição de Pronto:**
- [ ] Código implementado em `src/text_extractor.py`
- [ ] Testes manuais executados (PDFs ASTM 2015/2016)
- [ ] Documentado no notebook (célula "2. Extração de Texto")

**Estimativa:** 3 story points

---

### US-009: Preservação de Hierarquia de Seções
**Como** desenvolvedor
**Eu quero** identificar e preservar estrutura de seções numeradas (1, 1.1, 1.1.1)
**Para que** o alinhamento de seções correspondentes seja possível na próxima etapa

**Critérios de Aceite:**
- [ ] Regex implementado para detectar padrões de numeração: `^\d+(\.\d+)*\s+[A-Z]` (ex: "1.2 Scope")
- [ ] Estrutura hierárquica gerada como dict ou JSON: `{"1": {"title": "Scope", "content": "...", "subsections": {"1.1": ...}}}`
- [ ] Níveis de profundidade identificados (nível 1, nível 2, nível 3)
- [ ] Conteúdo de cada seção capturado até início da próxima seção
- [ ] Testado com ASTM 2015/2016 (estrutura típica: 1-3 níveis de profundidade)

**Definição de Pronto:**
- [ ] Código implementado em `src/text_extractor.py` (função `parse_section_hierarchy`)
- [ ] Testes manuais executados (validação manual de 5 seções)
- [ ] Documentado no notebook

**Estimativa:** 5 story points

---

### US-010: Extração de Metadados de PDF
**Como** desenvolvedor
**Eu quero** extrair metadados básicos (número de páginas, título, autor se disponível)
**Para que** eu tenha rastreabilidade dos PDFs processados

**Critérios de Aceite:**
- [ ] Função `extract_metadata(pdf_doc: fitz.Document) -> dict` implementada
- [ ] Retorna dict com: `{"page_count": int, "title": str, "author": str, "creation_date": str}`
- [ ] Campos vazios retornam "N/A" se metadados não disponíveis
- [ ] Metadados exibidos no notebook no início da extração
- [ ] Tempo de extração <1 segundo (metadados são leves)

**Definição de Pronto:**
- [ ] Código implementado em `src/text_extractor.py`
- [ ] Testes manuais executados (PDFs ASTM)
- [ ] Documentado no notebook

**Estimativa:** 1 story point

---

## Atividades Técnicas

### Atividade Macro 1: Extração Básica de Texto
**Subatividades:**
1. [ ] Criar arquivo `src/text_extractor.py` com imports (PyMuPDF, re, logging) (arquivo: `src/text_extractor.py`)
2. [ ] Implementar `extract_text(pdf_doc: fitz.Document) -> str` (arquivo: `src/text_extractor.py`)
3. [ ] Iterar sobre páginas com `for page_num in range(pdf_doc.page_count)` (arquivo: `src/text_extractor.py`)
4. [ ] Extrair texto com `page.get_text("text")` e concatenar (arquivo: `src/text_extractor.py`)
5. [ ] Adicionar separador de página: `\n--- PAGE {page_num} ---\n` (arquivo: `src/text_extractor.py`)
6. [ ] Testar com ASTM 2015 e medir tempo de execução com `%%time` (teste manual)

### Atividade Macro 2: Parsing de Hierarquia de Seções
**Subatividades:**
1. [ ] Implementar `parse_section_hierarchy(text: str) -> dict` (arquivo: `src/text_extractor.py`)
2. [ ] Criar regex para detectar títulos de seções: `r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][^\n]+)"` (arquivo: `src/text_extractor.py`)
3. [ ] Iterar sobre matches e construir estrutura hierárquica recursiva (arquivo: `src/text_extractor.py`)
4. [ ] Capturar conteúdo de cada seção (texto entre título atual e próximo título) (arquivo: `src/text_extractor.py`)
5. [ ] Retornar dict aninhado com níveis de profundidade (arquivo: `src/text_extractor.py`)
6. [ ] Validar estrutura manualmente comparando com PDF visual (teste manual)

### Atividade Macro 3: Extração de Metadados
**Subatividades:**
1. [ ] Implementar `extract_metadata(pdf_doc: fitz.Document) -> dict` (arquivo: `src/text_extractor.py`)
2. [ ] Acessar `pdf_doc.metadata` para obter campos padrão (arquivo: `src/text_extractor.py`)
3. [ ] Extrair `page_count` com `pdf_doc.page_count` (arquivo: `src/text_extractor.py`)
4. [ ] Tratar campos ausentes com `.get("title", "N/A")` (arquivo: `src/text_extractor.py`)
5. [ ] Formatar data de criação se disponível (ISO 8601) (arquivo: `src/text_extractor.py`)
6. [ ] Testar com PDFs ASTM e PDFs sem metadados (arquivo vazio) (teste manual)

### Atividade Macro 4: Logging de Progresso
**Subatividades:**
1. [ ] Adicionar logs informativos: "Extraindo página X/Y..." (arquivo: `src/text_extractor.py`)
2. [ ] Usar `logging.info()` com formato legível (arquivo: `src/text_extractor.py`)
3. [ ] Exibir resumo ao final: "Texto extraído: Z caracteres, N seções identificadas" (arquivo: `src/text_extractor.py`)
4. [ ] Configurar logging level em `src/config.py` (arquivo: `src/config.py`)
5. [ ] Testar logs no notebook (deve exibir progresso em tempo real) (teste manual)

---

## Critérios de Testes

### Teste 1: Extração Completa de Texto
**Entrada:** PDF ASTM 2015 (~20 páginas, 25MB)
**Ação:** Executar célula notebook:
```python
from src.pdf_loader import load_pdf
from src.text_extractor import extract_text
pdf_doc = load_pdf("data/inputs/astm_2015.pdf")
text = extract_text(pdf_doc)
print(f"Caracteres extraídos: {len(text)}")
print(f"Primeiras 500 chars: {text[:500]}")
```
**Saída Esperada:** Número de caracteres >50000, primeiros 500 chars contêm texto legível do documento, tempo de execução <60 segundos

### Teste 2: Identificação de Hierarquia de Seções
**Entrada:** Texto extraído de PDF ASTM com estrutura típica (1 Scope, 2 Referenced Documents, 2.1 ASTM Standards...)
**Ação:** Executar:
```python
from src.text_extractor import parse_section_hierarchy
sections = parse_section_hierarchy(text)
print(f"Seções de nível 1: {list(sections.keys())}")
print(f"Subseções de seção 2: {list(sections['2']['subsections'].keys())}")
```
**Saída Esperada:**
- Seções nível 1: `['1', '2', '3', '4', ...]`
- Subseções de 2: `['2.1', '2.2', ...]`
- Estrutura aninhada correta (visual inspection)

### Teste 3: Extração de Metadados
**Entrada:** PDF ASTM 2015 com metadados
**Ação:** Executar:
```python
from src.text_extractor import extract_metadata
metadata = extract_metadata(pdf_doc)
print(metadata)
```
**Saída Esperada:** Dict como `{"page_count": 20, "title": "ASTM A29/A29M-15", "author": "ASTM International", "creation_date": "2015-07-01"}`

### Teste 4: Performance de Extração
**Entrada:** PDF 25MB (ASTM completo)
**Ação:** Executar com `%%time`:
```python
%%time
text = extract_text(pdf_doc)
```
**Saída Esperada:** Tempo de execução ≤60 segundos (target: 30-45 segundos para 20 páginas = 2-2.5 páginas/segundo)

---

## Riscos e Mitigações

- **Risco 1:** PyMuPDF extrai texto em ordem errada (multi-coluna, layouts complexos) → **Mitigação:** Testar com layout="blocks" ou "dict" mode; validar manualmente 3-5 seções críticas
- **Risco 2:** Regex de seções falha em numerações não-padrão (A.1, Annex B) → **Mitigação:** Expandir regex para capturar padrões alternativos; documentar limitações conhecidas
- **Risco 3:** Performance <2 páginas/segundo (excede 60 segundos) → **Mitigação:** Processar páginas em paralelo com multiprocessing; usar `get_text("blocks")` seletivamente
- **Risco 4:** Hierarquia de seções gera estrutura incorreta (seções órfãs) → **Mitigação:** Implementar validação de estrutura; logar warnings para seções sem parent; permitir correção manual

---

## Métricas de Sucesso

- Taxa de extração bem-sucedida: ≥95% para PDFs nativos ASTM
- Performance: ≥2 páginas/segundo (target: 30-60 segundos para 20 páginas)
- Acurácia de detecção de seções: ≥90% (validado manualmente em 20 seções)
- Preservação de estrutura: Hierarquia de 3 níveis corretamente aninhada
- Completude de metadados: 100% dos campos disponíveis extraídos
