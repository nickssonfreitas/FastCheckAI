# Feature 6: Comparação Textual

**Prioridade:** P0 (Essential)
**Sprint:** Semana 2, Dias 9-10
**Estimativa:** 5 story points
**Dependências:** Feature 5 (Alinhamento de Seções)

## Objetivo

Comparar texto corrido de seções alinhadas usando algoritmo diff (difflib), identificar e categorizar adições, remoções e modificações, ignorar diferenças triviais (espaços, quebras de linha) e destacar mudanças em termos técnicos e valores numéricos com maior importância.

## User Stories

### US-017: Diff Textual de Seções Alinhadas
**Como** desenvolvedor
**Eu quero** executar diff linha por linha em seções correspondentes
**Para que** eu identifique exatamente quais trechos foram adicionados, removidos ou modificados

**Critérios de Aceite:**
- [ ] Função `compare_text(text_a: str, text_b: str) -> dict` implementada em `src/text_comparator.py`
- [ ] Usa `difflib.unified_diff()` ou `difflib.SequenceMatcher()` para comparação
- [ ] Retorna dict com listas categorizadas: `{"additions": [...], "removals": [...], "modifications": [...]}`
- [ ] Cada item contém posição (linha), conteúdo original, conteúdo modificado
- [ ] Tempo de comparação <5 segundos para seção de 5000 caracteres

**Definição de Pronto:**
- [ ] Código implementado em `src/text_comparator.py`
- [ ] Testes manuais executados (seções ASTM conhecidas com mudanças)
- [ ] Documentado no notebook (célula "5. Comparação Textual")

**Estimativa:** 3 story points

---

### US-018: Filtragem de Diferenças Triviais
**Como** engenheiro de produto
**Eu quero** ignorar mudanças insignificantes (espaços extras, quebras de linha, pontuação)
**Para que** eu foque apenas em diferenças semanticamente relevantes

**Critérios de Aceite:**
- [ ] Normalização de texto antes de comparação: remover espaços múltiplos, normalizar quebras de linha
- [ ] Diferenças apenas em whitespace ignoradas (não aparecem no output)
- [ ] Contador exibido: "X diferenças encontradas (Y triviais ignoradas)"
- [ ] Função `is_trivial_change(diff_item: dict) -> bool` implementada
- [ ] Testado com texto contendo apenas mudanças de formatação

**Definição de Pronto:**
- [ ] Código implementado em `src/text_comparator.py`
- [ ] Testes manuais executados (diferenças triviais filtradas)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

### US-019: Destacamento de Mudanças em Valores Numéricos
**Como** engenheiro de produto
**Eu quero** identificar mudanças em valores numéricos e termos técnicos com prioridade alta
**Para que** eu revise primeiro as alterações mais críticas em especificações técnicas

**Critérios de Aceite:**
- [ ] Regex implementado para detectar valores numéricos: `\d+(\.\d+)?` com unidades (MPa, %, mm)
- [ ] Mudanças contendo números marcadas com flag: `"contains_numeric_change": True`
- [ ] Lista de termos técnicos críticos (configurable): ["tensile strength", "chemical composition", "mandatory", "shall"]
- [ ] Mudanças em termos críticos marcadas com flag: `"contains_critical_term": True`
- [ ] Diferenças com flags exibidas no topo da lista (prioridade alta)

**Definição de Pronto:**
- [ ] Código implementado em `src/text_comparator.py`
- [ ] Testes manuais executados (mudanças numéricas priorizadas)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

## Atividades Técnicas

### Atividade Macro 1: Implementação de Diff Textual
**Subatividades:**
1. [ ] Criar arquivo `src/text_comparator.py` com imports (difflib, re, logging) (arquivo: `src/text_comparator.py`)
2. [ ] Implementar `compare_text(text_a: str, text_b: str) -> dict` (arquivo: `src/text_comparator.py`)
3. [ ] Usar `difflib.SequenceMatcher(None, text_a, text_b).get_opcodes()` (arquivo: `src/text_comparator.py`)
4. [ ] Categorizar opcodes em additions ("insert"), removals ("delete"), modifications ("replace") (arquivo: `src/text_comparator.py`)
5. [ ] Armazenar posições e conteúdos: `{"type": "addition", "line": 42, "content": "new text", "original": ""}` (arquivo: `src/text_comparator.py`)
6. [ ] Testar com seções ASTM com mudanças conhecidas (teste manual)

### Atividade Macro 2: Normalização e Filtragem de Trivialidades
**Subatividades:**
1. [ ] Implementar `normalize_text(text: str) -> str` (arquivo: `src/text_comparator.py`)
2. [ ] Remover múltiplos espaços: `re.sub(r'\s+', ' ', text)` (arquivo: `src/text_comparator.py`)
3. [ ] Normalizar quebras de linha: converter `\r\n` para `\n` (arquivo: `src/text_comparator.py`)
4. [ ] Aplicar normalização antes de chamar difflib (arquivo: `src/text_comparator.py`)
5. [ ] Implementar `is_trivial_change(diff: dict) -> bool` verificando se mudança é apenas whitespace (arquivo: `src/text_comparator.py`)
6. [ ] Filtrar trivialidades de lista de diferenças e logar contador (arquivo: `src/text_comparator.py`)
7. [ ] Testar com texto "Test  method" vs "Test method" (deve ser ignorado) (teste manual)

### Atividade Macro 3: Detecção de Mudanças Numéricas
**Subatividades:**
1. [ ] Implementar `contains_numeric_change(diff: dict) -> bool` (arquivo: `src/text_comparator.py`)
2. [ ] Regex para valores numéricos: `r'\d+(\.\d+)?\s*(MPa|%|mm|kg|°C)?'` (arquivo: `src/text_comparator.py`)
3. [ ] Buscar padrão em `diff["content"]` e `diff["original"]` (arquivo: `src/text_comparator.py`)
4. [ ] Adicionar flag `"contains_numeric_change": True` se detectado (arquivo: `src/text_comparator.py`)
5. [ ] Testar com mudança "500 MPa" → "550 MPa" (deve ser flagged) (teste manual)

### Atividade Macro 4: Detecção de Termos Críticos
**Subatividades:**
1. [ ] Criar lista de termos críticos em `src/config.py`: `CRITICAL_TERMS = ["tensile strength", "mandatory", "shall", "chemical composition"]` (arquivo: `src/config.py`)
2. [ ] Implementar `contains_critical_term(diff: dict) -> bool` (arquivo: `src/text_comparator.py`)
3. [ ] Buscar termos críticos (case-insensitive) em conteúdo (arquivo: `src/text_comparator.py`)
4. [ ] Adicionar flag `"contains_critical_term": True` se detectado (arquivo: `src/text_comparator.py`)
5. [ ] Ordenar lista de diferenças: flags no topo, resto depois (arquivo: `src/text_comparator.py`)
6. [ ] Testar com mudança contendo "mandatory" (deve aparecer no topo) (teste manual)

---

## Critérios de Testes

### Teste 1: Diff de Seção com Adição e Remoção
**Entrada:** Seção "2.1 Scope" de ASTM 2015: "This standard covers carbon steel bars" vs ASTM 2016: "This standard covers carbon and alloy steel bars"
**Ação:** Executar:
```python
from src.text_comparator import compare_text
diffs = compare_text(text_2015, text_2016)
print(f"Adições: {len(diffs['additions'])}")
print(f"Modificações: {len(diffs['modifications'])}")
print(diffs["additions"][0])
```
**Saída Esperada:**
- Modificações: 1
- Conteúdo: `{"type": "modification", "original": "carbon steel", "content": "carbon and alloy steel"}`

### Teste 2: Filtragem de Diferenças Triviais
**Entrada:** Texto com diferença apenas em espaçamento: "Test  method" vs "Test method"
**Ação:** Executar comparação com normalização
**Saída Esperada:** 0 diferenças encontradas (trivial ignorada), log: "5 diferenças encontradas (1 trivial ignorada)"

### Teste 3: Priorização de Mudança Numérica
**Entrada:** Seção com mudança "tensile strength ≥ 500 MPa" → "tensile strength ≥ 550 MPa"
**Ação:** Executar:
```python
diffs = compare_text(text_a, text_b)
flagged = [d for d in diffs["modifications"] if d.get("contains_numeric_change")]
print(flagged[0])
```
**Saída Esperada:** Mudança detectada com `"contains_numeric_change": True` e `"contains_critical_term": True` (tensile strength)

### Teste 4: Performance de Comparação
**Entrada:** Seção de 5000 caracteres com 20 mudanças
**Ação:** Executar com `%%time`:
```python
%%time
diffs = compare_text(long_text_a, long_text_b)
```
**Saída Esperada:** Tempo de execução <5 segundos

---

## Riscos e Mitigações

- **Risco 1:** difflib gera diff muito granular (cada palavra como linha separada) → **Mitigação:** Usar `autojunk=False` no SequenceMatcher; ajustar granularidade para sentenças em vez de palavras
- **Risco 2:** Normalização muito agressiva remove diferenças legítimas → **Mitigação:** Validação manual de 20 diferenças; refinar regex de normalização; documentar transformações aplicadas
- **Risco 3:** Regex de valores numéricos com falsos positivos (IDs de seção "3.2" detectados como valores) → **Mitigação:** Contextualizar regex (valores com unidades: MPa, %, mm); filtrar IDs de seção explicitamente
- **Risco 4:** Performance ruim em seções muito longas (>10k caracteres) → **Mitigação:** Processar seções em chunks de 5k chars; otimizar difflib com threshold de similaridade

---

## Métricas de Sucesso

- Taxa de detecção de diferenças: 100% de mudanças reais detectadas (validado em 10 seções conhecidas)
- Taxa de filtragem de trivialidades: ≥90% de whitespace-only changes ignoradas
- Precisão de detecção numérica: ≥95% (valores numéricos corretamente flagged)
- Performance: <5 segundos para seção de 5000 caracteres
- Ordenação correta: 100% de mudanças críticas no topo da lista
