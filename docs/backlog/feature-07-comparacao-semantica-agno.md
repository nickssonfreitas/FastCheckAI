# Feature 7: Comparação Semântica com Agno

**Prioridade:** P0 (Essential - Objetivo Primário do PoC)
**Sprint:** Semana 3, Dias 11-13
**Estimativa:** 10 story points
**Dependências:** Feature 6 (Comparação Textual)

## Objetivo

Integrar framework Agno com GPT-4o para análise semântica de diferenças detectadas, classificando mudanças em três níveis (equivalente semântico, mudança menor, mudança significativa), fornecendo justificativa textual da classificação e validando viabilidade técnica do Agno como objetivo primário do PoC.

## User Stories

### US-020: Integração do Agno Framework
**Como** desenvolvedor aprendendo Agno
**Eu quero** criar agente especializado em análise de documentos técnicos
**Para que** eu valide viabilidade do framework para orchestração de LLM em comparação semântica

**Critérios de Aceite:**
- [ ] Agente Agno criado com `Agent(model="gpt-4o", instructions="You are a technical standards expert...")` em `src/semantic_comparator.py`
- [ ] Temperature configurada em 0.3 (baixa para consistência em análise técnica)
- [ ] Sistema de retry implementado (3 tentativas com backoff exponencial)
- [ ] Fallback para OpenAI SDK direto se Agno falhar em >30% das chamadas
- [ ] Logs detalhados de cada chamada Agno (tempo, tokens, custo estimado)

**Definição de Pronto:**
- [ ] Código implementado em `src/semantic_comparator.py`
- [ ] Testes manuais executados (agente responde a prompt de teste)
- [ ] Documentado no notebook (célula "6. Análise Semântica com Agno")

**Estimativa:** 3 story points

---

### US-021: Classificação Semântica de Diferenças
**Como** engenheiro de produto
**Eu quero** que LLM classifique cada diferença em 3 níveis de significância
**Para que** eu priorize revisão de mudanças realmente importantes vs reformulações sem impacto

**Critérios de Aceite:**
- [ ] Prompt estruturado com contexto de domínio (normas técnicas ASTM)
- [ ] Classificação em 3 níveis: "EQUIVALENT" (semanticamente idêntico), "MINOR" (mudança de clarificação), "SIGNIFICANT" (mudança de requisito técnico)
- [ ] Output estruturado como JSON: `{"classification": "SIGNIFICANT", "confidence": 0.9, "reasoning": "Change from optional to mandatory testing"}`
- [ ] Processamento de seções até 4000 tokens sem erro de contexto
- [ ] Tempo de resposta ≤10 segundos P95 por diferença

**Definição de Pronto:**
- [ ] Código implementado em `src/semantic_comparator.py` (função `classify_semantic_significance`)
- [ ] Testes manuais executados (10 diferenças conhecidas classificadas corretamente)
- [ ] Documentado no notebook

**Estimativa:** 5 story points

---

### US-022: Justificativa Textual da Classificação
**Como** engenheiro de produto
**Eu quero** ler explicação do LLM sobre por que uma mudança foi classificada como significativa
**Para que** eu entenda o raciocínio e confie na análise automatizada

**Critérios de Aceite:**
- [ ] Campo "reasoning" obrigatório no output JSON do LLM
- [ ] Justificativa com 1-3 sentenças explicando decisão
- [ ] Citação de trechos relevantes do texto original e modificado
- [ ] Justificativa exibida junto com classificação no output final
- [ ] Linguagem clara e técnica (sem jargões de IA)

**Definição de Pronto:**
- [ ] Código implementado (parsing de reasoning do LLM)
- [ ] Testes manuais executados (justificativas legíveis e relevantes)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

### US-023: Otimização de Custo e Performance
**Como** desenvolvedor
**Eu quero** minimizar custos de API LLM e tempo de processamento
**Para que** PoC fique dentro do budget de $50 e target de 3 minutos end-to-end

**Critérios de Aceite:**
- [ ] Cache de respostas LLM implementado (mesma diferença não reprocessada)
- [ ] Filtragem prévia: apenas diferenças >10 palavras enviadas para LLM
- [ ] Batching de diferenças triviais: múltiplas mudanças menores em 1 prompt
- [ ] Monitoramento de custo: exibir custo estimado ao final (tokens × pricing)
- [ ] Custo por execução completa (ASTM 2015 vs 2016) ≤$1.50

**Definição de Pronto:**
- [ ] Código implementado (cache, filtragem, batching)
- [ ] Testes manuais executados (custo validado)
- [ ] Documentado no notebook

**Estimativa:** 3 story points

---

## Atividades Técnicas

### Atividade Macro 1: Setup do Agente Agno
**Subatividades:**
1. [ ] Criar arquivo `src/semantic_comparator.py` com imports (agno, openai, json, logging) (arquivo: `src/semantic_comparator.py`)
2. [ ] Implementar `create_semantic_agent() -> Agent` (arquivo: `src/semantic_comparator.py`)
3. [ ] Configurar agente: `Agent(model="gpt-4o", temperature=0.3, instructions=SEMANTIC_INSTRUCTIONS)` (arquivo: `src/semantic_comparator.py`)
4. [ ] Criar constante `SEMANTIC_INSTRUCTIONS` com contexto de normas técnicas (arquivo: `src/semantic_comparator.py`)
5. [ ] Implementar retry logic com `tenacity` library (3 tentativas, backoff exponencial) (arquivo: `src/semantic_comparator.py`)
6. [ ] Testar criação de agente e prompt simples "Explain semantic equivalence" (teste manual)

### Atividade Macro 2: Prompts de Classificação Semântica
**Subatividades:**
1. [ ] Implementar `classify_semantic_significance(diff: dict, agent: Agent) -> dict` (arquivo: `src/semantic_comparator.py`)
2. [ ] Construir prompt estruturado:
   ```
   You are analyzing changes in technical standard ASTM A29/A29M.
   Original text: "{original}"
   Modified text: "{modified}"

   Classify this change as:
   - EQUIVALENT: Same meaning, just rephrased
   - MINOR: Clarification or editorial change, no technical impact
   - SIGNIFICANT: Change in technical requirement, scope, or specification

   Return JSON: {"classification": "...", "confidence": 0.0-1.0, "reasoning": "..."}
   ```
   (arquivo: `src/semantic_comparator.py`)
3. [ ] Chamar agente: `response = agent.run(prompt)` (arquivo: `src/semantic_comparator.py`)
4. [ ] Parsear JSON do response (com fallback para regex se JSON malformado) (arquivo: `src/semantic_comparator.py`)
5. [ ] Validar campos obrigatórios: classification, confidence, reasoning (arquivo: `src/semantic_comparator.py`)
6. [ ] Testar com 5 diferenças conhecidas (teste manual)

### Atividade Macro 3: Fallback OpenAI SDK
**Subatividades:**
1. [ ] Implementar `classify_with_openai_direct(diff: dict) -> dict` (arquivo: `src/semantic_comparator.py`)
2. [ ] Usar OpenAI SDK: `client.chat.completions.create(model="gpt-4o", messages=[...])` (arquivo: `src/semantic_comparator.py`)
3. [ ] Reusar mesmo prompt da versão Agno (arquivo: `src/semantic_comparator.py`)
4. [ ] Ativar fallback se Agno lançar exceção (logar warning) (arquivo: `src/semantic_comparator.py`)
5. [ ] Contador de fallbacks: exibir "X chamadas Agno, Y fallbacks OpenAI" (arquivo: `src/semantic_comparator.py`)
6. [ ] Testar forçando erro do Agno (API key inválida) (teste manual)

### Atividade Macro 4: Otimização de Custo
**Subatividades:**
1. [ ] Implementar cache simples com dict: `CACHE: dict[str, dict] = {}` (arquivo: `src/semantic_comparator.py`)
2. [ ] Chave de cache: hash do conteúdo original + modificado (arquivo: `src/semantic_comparator.py`)
3. [ ] Verificar cache antes de chamar LLM; retornar resultado cacheado se existir (arquivo: `src/semantic_comparator.py`)
4. [ ] Filtrar diferenças triviais: apenas processar se `len(diff["content"].split()) > 10` (arquivo: `src/semantic_comparator.py`)
5. [ ] Implementar `estimate_cost(total_tokens: int) -> float` usando pricing GPT-4o ($0.0025 input, $0.01 output) (arquivo: `src/semantic_comparator.py`)
6. [ ] Exibir custo total ao final: "Análise semântica: $0.85 (120k tokens)" (arquivo: `src/semantic_comparator.py`)
7. [ ] Testar com 30 diferenças e validar custo <$2 (teste manual)

### Atividade Macro 5: Logging e Observabilidade
**Subatividades:**
1. [ ] Logar cada chamada LLM: "Classificando diferença X/Y... (tokens: Z)" (arquivo: `src/semantic_comparator.py`)
2. [ ] Logar tempo de resposta: "LLM respondeu em 3.2s" (arquivo: `src/semantic_comparator.py`)
3. [ ] Logar uso de cache: "Cache hit: diferença já processada" (arquivo: `src/semantic_comparator.py`)
4. [ ] Logar classificações: "SIGNIFICANT (conf=0.92): mandatory → optional" (arquivo: `src/semantic_comparator.py`)
5. [ ] Resumo ao final: "30 diferenças processadas, 5 cached, 2 fallbacks, custo: $0.85" (arquivo: `src/semantic_comparator.py`)

---

## Critérios de Testes

### Teste 1: Criação e Validação do Agente Agno
**Entrada:** Ambiente configurado com OPENAI_API_KEY
**Ação:** Executar célula notebook:
```python
from src.semantic_comparator import create_semantic_agent
agent = create_semantic_agent()
response = agent.run("What is semantic equivalence in one sentence?")
print(response)
```
**Saída Esperada:** Resposta legível do GPT-4o via Agno (ex: "Semantic equivalence means two texts convey the same meaning despite different wording") em <10 segundos

### Teste 2: Classificação de Mudança Equivalente
**Entrada:** Diferença com reformulação: "automobile" → "vehicle"
**Ação:** Executar:
```python
diff = {"original": "automobile", "content": "vehicle"}
result = classify_semantic_significance(diff, agent)
print(result)
```
**Saída Esperada:** `{"classification": "EQUIVALENT", "confidence": 0.95, "reasoning": "Both terms refer to the same concept with no technical distinction"}`

### Teste 3: Classificação de Mudança Significativa
**Entrada:** Diferença crítica: "mandatory testing" → "optional testing"
**Ação:** Executar classificação
**Saída Esperada:** `{"classification": "SIGNIFICANT", "confidence": 0.98, "reasoning": "Change from mandatory to optional fundamentally alters the requirement"}`

### Teste 4: Fallback OpenAI em Caso de Falha Agno
**Entrada:** Agno configurado com API key inválida (simular falha)
**Ação:** Executar classificação e verificar log
**Saída Esperada:** Warning "Agno falhou, usando fallback OpenAI SDK", classificação bem-sucedida via OpenAI direto

### Teste 5: Custo e Performance de 30 Diferenças
**Entrada:** 30 diferenças do ASTM 2015 vs 2016 (mix de EQUIVALENT, MINOR, SIGNIFICANT)
**Ação:** Executar com `%%time`:
```python
%%time
results = [classify_semantic_significance(d, agent) for d in diffs]
print(f"Custo estimado: ${estimate_cost(total_tokens)}")
```
**Saída Esperada:** Tempo <90 segundos (3s/diferença), custo <$1.50, cache utilizado em re-execução (custo $0)

---

## Riscos e Mitigações

- **Risco 1:** Agno Framework instável (bugs em >30% das chamadas) → **Mitigação:** Checkpoint Dia 11: se taxa de falha >30%, migrar para OpenAI SDK direto (estimado 2-3h); documentar bugs reportados
- **Risco 2:** Classificações inconsistentes (mesma mudança classificada diferente em re-execução) → **Mitigação:** Usar temperature=0.3 (baixa variabilidade); validar consistência em 10 re-execuções; implementar cache obrigatório
- **Risco 3:** Custo excede $1.50/execução (30 diferenças × $0.05/chamada = $1.50) → **Mitigação:** Batching de diferenças menores; filtro agressivo (>15 palavras); usar GPT-4o-mini para MINOR candidates
- **Risco 4:** LLM retorna JSON malformado (quebra parsing) → **Mitigação:** Implementar fallback regex para extrair classification; validar schema com pydantic; retry com prompt ajustado
- **Risco 5:** Contexto excede 4000 tokens (seções muito longas) → **Mitigação:** Truncar contexto mantendo primeiros e últimos 2000 chars; logar warning; marcar como "context_truncated"

---

## Métricas de Sucesso

- Taxa de sucesso do Agno: ≥70% (30% podem usar fallback OpenAI)
- Acurácia de classificação: ≥85% de concordância com validação humana (testado em 20 diferenças)
- Consistência: ≥90% de classificações idênticas em re-execução (temperature=0.3)
- Performance: P95 ≤10 segundos por diferença
- Custo por execução completa: ≤$1.50 (30 diferenças)
- Validação de Agno: Framework considerado viável se taxa de falha <30%
