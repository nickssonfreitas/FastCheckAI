# Feature 9: Classificação de Severidade

**Prioridade:** P1 (Desirable)
**Sprint:** Semana 3, Dia 14
**Estimativa:** 5 story points
**Dependências:** Feature 6 (Comparação Textual), Feature 7 (Comparação Semântica)

## Objetivo

Classificar diferenças detectadas em 3 níveis de severidade (CRITICAL, MEDIUM, LOW) usando regras heurísticas baseadas em palavras-chave, contexto e classificação semântica do LLM, para priorizar revisão de mudanças mais importantes pelos engenheiros de produto.

## User Stories

### US-027: Regras de Classificação de Severidade
**Como** engenheiro de produto
**Eu quero** que diferenças sejam automaticamente classificadas por severidade
**Para que** eu priorize revisão de mudanças críticas antes de mudanças editoriais

**Critérios de Aceite:**
- [ ] Função `classify_severity(diff: dict, semantic_result: dict) -> str` implementada em `src/severity_classifier.py`
- [ ] 3 níveis de severidade: "CRITICAL", "MEDIUM", "LOW"
- [ ] Regras implementadas (veja Atividade Macro 1)
- [ ] Severidade adicionada ao dict de diferença: `diff["severity"] = "CRITICAL"`
- [ ] Testado com 20 diferenças conhecidas (validação manual de severidade)

**Definição de Pronto:**
- [ ] Código implementado em `src/severity_classifier.py`
- [ ] Testes manuais executados (classificações corretas)
- [ ] Documentado no notebook (célula "8. Classificação de Severidade")

**Estimativa:** 3 story points

---

### US-028: Priorização de Mudanças Numéricas em Especificações
**Como** engenheiro de produto
**Eu quero** que mudanças em valores numéricos de especificações sejam automaticamente marcadas como CRITICAL
**Para que** eu revise primeiro alterações em requisitos técnicos mensuráveis

**Critérios de Aceite:**
- [ ] Mudanças em valores numéricos + contexto de especificação → CRITICAL
- [ ] Contexto detectado por palavras-chave: "tensile strength", "chemical composition", "tolerance", "limits"
- [ ] Testado com mudança "tensile strength ≥ 500 MPa" → "550 MPa" → CRITICAL
- [ ] Mudanças numéricas sem contexto de especificação → MEDIUM
- [ ] Log exibido: "Mudança numérica em especificação detectada → CRITICAL"

**Definição de Pronto:**
- [ ] Código implementado em `src/severity_classifier.py`
- [ ] Testes manuais executados (mudanças numéricas corretamente priorizadas)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

### US-029: Integração com Classificação Semântica LLM
**Como** desenvolvedor
**Eu quero** usar classificação semântica do LLM como input para severidade
**Para que** mudanças "SIGNIFICANT" do LLM sejam automaticamente CRITICAL ou MEDIUM

**Critérios de Aceite:**
- [ ] Se `semantic_result["classification"] == "SIGNIFICANT"` → considerar CRITICAL (exceto se contradito por outras regras)
- [ ] Se `semantic_result["classification"] == "MINOR"` → considerar LOW ou MEDIUM (dependendo de flags)
- [ ] Se `semantic_result["classification"] == "EQUIVALENT"` → considerar LOW
- [ ] Confiança LLM <0.7 → não usar classificação semântica (usar apenas regras heurísticas)
- [ ] Testado com combinações de classificação semântica e flags

**Definição de Pronto:**
- [ ] Código implementado em `src/severity_classifier.py`
- [ ] Testes manuais executados (integração semântica funcional)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

## Atividades Técnicas

### Atividade Macro 1: Regras Heurísticas de Severidade
**Subatividades:**
1. [ ] Criar arquivo `src/severity_classifier.py` com imports (re, logging) (arquivo: `src/severity_classifier.py`)
2. [ ] Implementar `classify_severity(diff: dict, semantic_result: dict = None) -> str` (arquivo: `src/severity_classifier.py`)
3. [ ] Criar constantes com palavras-chave críticas em `src/config.py`:
   ```python
   CRITICAL_KEYWORDS = ["mandatory", "shall", "must", "required", "prohibited"]
   CRITICAL_CONTEXTS = ["tensile strength", "chemical composition", "tolerance", "limits", "requirements"]
   MEDIUM_KEYWORDS = ["should", "recommended", "typical", "nominal"]
   LOW_KEYWORDS = ["may", "can", "optional", "example", "note"]
   ```
   (arquivo: `src/config.py`)
4. [ ] Implementar lógica de regras (arquivo: `src/severity_classifier.py`):
   - Mudança contém palavra crítica (mandatory, shall) → CRITICAL
   - Mudança em valor numérico + contexto de especificação → CRITICAL
   - Mudança em tabelas numéricas (table_change=True) → CRITICAL
   - Mudança de texto descritivo com palavra MEDIUM → MEDIUM
   - Reformulação editorial sem impacto técnico → LOW
5. [ ] Testar com 10 diferenças conhecidas (teste manual)

### Atividade Macro 2: Detecção de Contexto de Especificação
**Subatividades:**
1. [ ] Implementar `is_specification_context(text: str) -> bool` (arquivo: `src/severity_classifier.py`)
2. [ ] Buscar palavras-chave de contexto no texto original e modificado (arquivo: `src/severity_classifier.py`)
3. [ ] Verificar se mudança ocorre em seção de especificações (ex: "3. Chemical Composition") (arquivo: `src/severity_classifier.py`)
4. [ ] Retornar True se contexto detectado, False caso contrário (arquivo: `src/severity_classifier.py`)
5. [ ] Testar com texto contendo "tensile strength requirements" (deve retornar True) (teste manual)

### Atividade Macro 3: Integração com LLM Semântico
**Subatividades:**
1. [ ] Adicionar parâmetro opcional `semantic_result: dict` a `classify_severity()` (arquivo: `src/severity_classifier.py`)
2. [ ] Verificar se resultado semântico está disponível e tem confiança ≥0.7 (arquivo: `src/severity_classifier.py`)
3. [ ] Mapear classificações LLM para severidade (arquivo: `src/severity_classifier.py`):
   - SIGNIFICANT + confiança alta → CRITICAL (se confirmado por flags)
   - SIGNIFICANT + confiança média → MEDIUM
   - MINOR → MEDIUM ou LOW (dependendo de contexto)
   - EQUIVALENT → LOW
4. [ ] Lógica de desempate: regras heurísticas têm precedência sobre LLM se conflito (arquivo: `src/severity_classifier.py`)
5. [ ] Logar decisão: "Severidade: CRITICAL (LLM=SIGNIFICANT + numeric_change=True)" (arquivo: `src/severity_classifier.py`)
6. [ ] Testar com diferenças tendo classificação semântica (teste manual)

### Atividade Macro 4: Visualização de Distribuição de Severidade
**Subatividades:**
1. [ ] Implementar `summarize_severity(diffs: list[dict]) -> dict` (arquivo: `src/severity_classifier.py`)
2. [ ] Contar diferenças por severidade: `{"CRITICAL": 5, "MEDIUM": 12, "LOW": 8}` (arquivo: `src/severity_classifier.py`)
3. [ ] Calcular percentuais: `{"CRITICAL": "20%", "MEDIUM": "48%", "LOW": "32%"}` (arquivo: `src/severity_classifier.py`)
4. [ ] Exibir resumo no notebook: "25 diferenças: 5 CRITICAL (20%), 12 MEDIUM (48%), 8 LOW (32%)" (arquivo: `src/severity_classifier.py`)
5. [ ] Opcional: gerar gráfico de barras simples com matplotlib (arquivo: `src/severity_classifier.py`)
6. [ ] Testar com conjunto de 30 diferenças (teste manual)

---

## Critérios de Testes

### Teste 1: Classificação de Mudança com Palavra Crítica
**Entrada:** Diferença com mudança "optional testing" → "mandatory testing"
**Ação:** Executar:
```python
from src.severity_classifier import classify_severity
diff = {"original": "optional testing", "content": "mandatory testing"}
severity = classify_severity(diff)
print(severity)
```
**Saída Esperada:** "CRITICAL" (palavra "mandatory" detectada)

### Teste 2: Priorização de Mudança Numérica em Especificação
**Entrada:** Diferença "tensile strength ≥ 500 MPa" → "≥ 550 MPa"
**Ação:** Executar classificação
**Saída Esperada:** "CRITICAL" (mudança numérica + contexto "tensile strength")

### Teste 3: Integração com Classificação Semântica LLM
**Entrada:** Diferença com `semantic_result = {"classification": "SIGNIFICANT", "confidence": 0.92}`
**Ação:** Executar:
```python
severity = classify_severity(diff, semantic_result)
print(severity)
```
**Saída Esperada:** "CRITICAL" (LLM SIGNIFICANT + confiança alta)

### Teste 4: Mudança Editorial Classificada como LOW
**Entrada:** Diferença "automobile" → "vehicle" com `semantic_result = {"classification": "EQUIVALENT"}`
**Ação:** Executar classificação
**Saída Esperada:** "LOW" (equivalente semântico, sem impacto técnico)

### Teste 5: Resumo de Distribuição de Severidade
**Entrada:** 25 diferenças com severidades conhecidas (5 CRITICAL, 12 MEDIUM, 8 LOW)
**Ação:** Executar:
```python
summary = summarize_severity(all_diffs)
print(summary)
```
**Saída Esperada:** `{"CRITICAL": 5, "MEDIUM": 12, "LOW": 8, "percentages": {"CRITICAL": "20%", "MEDIUM": "48%", "LOW": "32%"}}`

---

## Riscos e Mitigações

- **Risco 1:** Regras heurísticas geram muitos falsos positivos (mudanças LOW marcadas como CRITICAL) → **Mitigação:** Validação manual de 50 classificações; ajustar palavras-chave; adicionar regras de exceção
- **Risco 2:** Conflito entre classificação LLM e regras heurísticas (ex: LLM diz MINOR, mas tem "mandatory") → **Mitigação:** Regras heurísticas têm precedência; logar conflitos; revisar manualmente casos divergentes
- **Risco 3:** Contexto de especificação mal detectado (falsos negativos) → **Mitigação:** Expandir lista de palavras-chave; usar análise de seção (ex: seção "3. Requirements" → contexto CRITICAL)
- **Risco 4:** Classificação inconsistente entre execuções (mesma mudança classificada diferente) → **Mitigação:** Classificação baseada apenas em regras determinísticas + LLM (que tem temperature=0.3); validar consistência

---

## Métricas de Sucesso

- Acurácia de classificação: ≥80% de concordância com validação humana (testado em 30 diferenças)
- Precisão de CRITICAL: ≥90% de mudanças marcadas CRITICAL são realmente críticas (validação manual)
- Recall de CRITICAL: ≥85% de mudanças críticas reais são detectadas (não perder mudanças importantes)
- Distribuição esperada: ~20% CRITICAL, ~50% MEDIUM, ~30% LOW (validado com ASTM 2015 vs 2016)
- Performance: <1 segundo para classificar 100 diferenças
