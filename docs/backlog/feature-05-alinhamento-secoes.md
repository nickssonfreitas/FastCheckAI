# Feature 5: Alinhamento de Seções

**Prioridade:** P0 (Essential)
**Sprint:** Semana 2, Dias 6-8
**Estimativa:** 8 story points
**Dependências:** Feature 3 (Extração de Texto)

## Objetivo

Mapear seções correspondentes entre dois PDFs usando abordagem híbrida (heurística + LLM fallback), detectar seções adicionadas/removidas, e gerar mapeamento explícito para viabilizar comparação textual e semântica na etapa seguinte.

## User Stories

### US-014: Alinhamento Heurístico por ID e Título
**Como** desenvolvedor
**Eu quero** alinhar seções automaticamente usando numeração exata e fuzzy matching de títulos
**Para que** ≥80% das seções sejam alinhadas sem intervenção de LLM (otimização de custo)

**Critérios de Aceite:**
- [ ] Função `align_sections_heuristic(sections_a: dict, sections_b: dict) -> dict` implementada
- [ ] Prioridade 1: Exact match por ID de seção (ex: "3.2" em ambos PDFs → match automático)
- [ ] Prioridade 2: Fuzzy match por título usando rapidfuzz (threshold ≥0.8 de similaridade)
- [ ] Retorna dict de alinhamentos: `{"section_a_id": {"section_b_id": "...", "confidence": 0.95, "method": "exact"}}`
- [ ] Confiança média ≥0.8 para considerar alinhamento bem-sucedido

**Definição de Pronto:**
- [ ] Código implementado em `src/section_aligner.py`
- [ ] Testes manuais executados (ASTM 2015 vs 2016)
- [ ] Documentado no notebook (célula "4. Alinhamento de Seções")

**Estimativa:** 3 story points

---

### US-015: Fallback LLM para Alinhamento Complexo
**Como** desenvolvedor
**Eu quero** usar Agno + GPT-4o para sugerir alinhamentos quando heurística falha
**Para que** seções renomeadas ou reorganizadas sejam alinhadas corretamente

**Critérios de Aceite:**
- [ ] Fallback ativado se seção sem match tem confiança <0.8 na heurística
- [ ] Prompt LLM: "Compare estas seções e indique se são correspondentes: Seção A: [título + primeiros 500 chars] vs Seção B: [título + primeiros 500 chars]"
- [ ] LLM retorna JSON: `{"is_match": bool, "confidence": 0.0-1.0, "reasoning": "..."}`
- [ ] Alinhamentos LLM marcados com `"method": "llm_fallback"`
- [ ] Custo por execução <$0.50 (estimado 5-10 chamadas LLM por par de PDFs)

**Definição de Pronto:**
- [ ] Código implementado em `src/section_aligner.py` (função `align_with_llm`)
- [ ] Testes manuais executados (seções renomeadas entre ASTM 2015/2016)
- [ ] Documentado no notebook

**Estimativa:** 4 story points

---

### US-016: Detecção de Seções Adicionadas e Removidas
**Como** engenheiro de produto
**Eu quero** identificar seções que existem apenas em PDF_A ou PDF_B
**Para que** eu saiba exatamente o que foi adicionado ou removido entre versões

**Critérios de Aceite:**
- [ ] Após alinhamento, seções não mapeadas são categorizadas como "added" ou "removed"
- [ ] Seções em PDF_B sem correspondente em PDF_A → marcadas como `"status": "added"`
- [ ] Seções em PDF_A sem correspondente em PDF_B → marcadas como `"status": "removed"`
- [ ] Lista de seções adicionadas/removidas exibida separadamente no output
- [ ] Contadores exibidos: "X seções alinhadas, Y adicionadas, Z removidas"

**Definição de Pronto:**
- [ ] Código implementado em `src/section_aligner.py`
- [ ] Testes manuais executados (validação com PDFs conhecidos)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

## Atividades Técnicas

### Atividade Macro 1: Alinhamento por Exact Match
**Subatividades:**
1. [ ] Criar arquivo `src/section_aligner.py` com imports (rapidfuzz, agno, logging) (arquivo: `src/section_aligner.py`)
2. [ ] Implementar `align_sections_heuristic(sections_a, sections_b) -> dict` (arquivo: `src/section_aligner.py`)
3. [ ] Iterar sobre seções de PDF_A e buscar ID exato em PDF_B (arquivo: `src/section_aligner.py`)
4. [ ] Se match exato, adicionar a alinhamentos com `confidence=1.0, method="exact"` (arquivo: `src/section_aligner.py`)
5. [ ] Marcar seções alinhadas para evitar duplicação (arquivo: `src/section_aligner.py`)
6. [ ] Testar com ASTM 2015/2016 (maioria das seções devem ter exact match) (teste manual)

### Atividade Macro 2: Fuzzy Matching de Títulos
**Subatividades:**
1. [ ] Para seções não alinhadas, aplicar fuzzy matching de títulos (arquivo: `src/section_aligner.py`)
2. [ ] Usar `rapidfuzz.fuzz.ratio(title_a, title_b)` para calcular similaridade (arquivo: `src/section_aligner.py`)
3. [ ] Threshold de aceitação: similaridade ≥0.8 (80%) (arquivo: `src/section_aligner.py`)
4. [ ] Selecionar melhor match (maior similaridade) se múltiplos candidatos (arquivo: `src/section_aligner.py`)
5. [ ] Adicionar a alinhamentos com `confidence=similaridade, method="fuzzy"` (arquivo: `src/section_aligner.py`)
6. [ ] Testar com seções renomeadas (ex: "Scope" → "Application Scope") (teste manual)

### Atividade Macro 3: Fallback LLM com Agno
**Subatividades:**
1. [ ] Implementar `align_with_llm(section_a, section_b) -> dict` (arquivo: `src/section_aligner.py`)
2. [ ] Criar agente Agno: `Agent(model="gpt-4o", instructions="You are an expert in technical document comparison...")` (arquivo: `src/section_aligner.py`)
3. [ ] Construir prompt: "Seção A: [id + title + primeiros 500 chars] | Seção B: [id + title + primeiros 500 chars] | São correspondentes?" (arquivo: `src/section_aligner.py`)
4. [ ] Parsear resposta JSON do LLM: `{"is_match": bool, "confidence": float, "reasoning": str}` (arquivo: `src/section_aligner.py`)
5. [ ] Aplicar fallback apenas para seções com confiança heurística <0.8 (arquivo: `src/section_aligner.py`)
6. [ ] Logar uso de LLM: "LLM fallback usado para seção X: match={is_match}, confidence={conf}" (arquivo: `src/section_aligner.py`)
7. [ ] Testar com seções reorganizadas (teste manual)

### Atividade Macro 4: Detecção de Added/Removed
**Subatividades:**
1. [ ] Implementar `detect_unmatched_sections(alignments, sections_a, sections_b) -> dict` (arquivo: `src/section_aligner.py`)
2. [ ] Identificar IDs em sections_a não presentes em alignments → marcar como "removed" (arquivo: `src/section_aligner.py`)
3. [ ] Identificar IDs em sections_b não presentes em alignments → marcar como "added" (arquivo: `src/section_aligner.py`)
4. [ ] Retornar dict: `{"added": [list of sections], "removed": [list of sections]}` (arquivo: `src/section_aligner.py`)
5. [ ] Exibir resumo: "10 seções alinhadas, 2 adicionadas, 1 removida" (arquivo: `src/section_aligner.py`)
6. [ ] Testar com PDFs com seções novas/removidas conhecidas (teste manual)

---

## Critérios de Testes

### Teste 1: Alinhamento por Exact Match
**Entrada:** Seções extraídas de ASTM 2015 e 2016 com IDs idênticos (ex: "1 Scope", "2 Referenced Documents")
**Ação:** Executar:
```python
from src.section_aligner import align_sections_heuristic
alignments = align_sections_heuristic(sections_2015, sections_2016)
exact_matches = [a for a in alignments.values() if a["method"] == "exact"]
print(f"Exact matches: {len(exact_matches)}")
```
**Saída Esperada:** Maioria das seções (≥80%) com exact match, confidence=1.0

### Teste 2: Fuzzy Matching de Títulos Renomeados
**Entrada:** Seções com títulos similares mas não idênticos (ex: "Chemical Composition" vs "Chemical Composition Requirements")
**Ação:** Executar alinhamento heurístico
**Saída Esperada:** Match com confidence ≥0.8, method="fuzzy", seções corretamente alinhadas

### Teste 3: Fallback LLM para Seções Reorganizadas
**Entrada:** Seção "3.2 Tensile Requirements" em PDF_A, renumerada para "5.1 Tensile Requirements" em PDF_B (heurística falha)
**Ação:** Executar:
```python
from src.section_aligner import align_with_llm
llm_alignment = align_with_llm(section_3_2_pdf_a, section_5_1_pdf_b)
print(llm_alignment)
```
**Saída Esperada:** `{"is_match": True, "confidence": 0.9, "reasoning": "Both sections describe tensile requirements with similar content"}`, tempo <10 segundos

### Teste 4: Detecção de Seções Adicionadas/Removidas
**Entrada:** PDF_A com seção "7 Obsolete Process", ausente em PDF_B; PDF_B com nova seção "8 Sustainability Requirements"
**Ação:** Executar:
```python
from src.section_aligner import detect_unmatched_sections
unmatched = detect_unmatched_sections(alignments, sections_a, sections_b)
print(f"Adicionadas: {unmatched['added']}")
print(f"Removidas: {unmatched['removed']}")
```
**Saída Esperada:**
- Removidas: `[{"id": "7", "title": "Obsolete Process"}]`
- Adicionadas: `[{"id": "8", "title": "Sustainability Requirements"}]`

---

## Riscos e Mitigações

- **Risco 1:** Fuzzy matching gera falsos positivos (seções não relacionadas com títulos similares) → **Mitigação:** Validação manual de top 10 matches; ajustar threshold para 0.85; adicionar validação de conteúdo
- **Risco 2:** LLM fallback muito caro (>$0.50/execução se muitas seções sem match) → **Mitigação:** Limitar fallback a seções com confiança 0.5-0.8; usar GPT-4o-mini se custo exceder budget
- **Risco 3:** Alinhamento heurístico <80% de confiança média → **Mitigação:** Refinar fuzzy matching; usar embedding similarity em vez de string matching; documentar limitações
- **Risco 4:** Seções com conteúdo idêntico mas títulos completamente diferentes não alinham → **Mitigação:** Implementar fallback por similaridade de conteúdo (TF-IDF ou embeddings)

---

## Métricas de Sucesso

- Taxa de alinhamento automático (heurística): ≥80% das seções
- Confiança média de alinhamentos: ≥0.8
- Taxa de uso de LLM fallback: ≤20% das seções
- Acurácia de alinhamento: ≥90% (validado manualmente em 30 seções)
- Custo de LLM por execução: ≤$0.50 (5-10 chamadas)
- Detecção de added/removed: 100% de precisão (validado manualmente)
