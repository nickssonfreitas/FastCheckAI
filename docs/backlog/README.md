# Backlog de Produto - FastCheckAI PoC

**Versão:** 1.0
**Data:** 30 de Setembro de 2025
**Status:** Pronto para Implementação
**Product Manager:** FastCheckAI Team

---

## Visão Geral

Este backlog contém o detalhamento completo das **11 features priorizadas** para o PoC FastCheckAI, organizado segundo a ordem do **Pipeline ETL** (PDF Input → Validation → Extraction → Alignment → Comparison → Analysis → Output).

**Objetivo do PoC:** Validar viabilidade técnica do framework Agno para comparação automatizada de PDFs técnicos em **3.5 semanas** com **1 desenvolvedor solo**.

---

## Índice de Features

### Semana 1: Setup e Extração (Dias 1-5)

| Feature | Arquivo | Prioridade | Story Points | Dias |
|---------|---------|------------|--------------|------|
| **Feature 1: Setup e Configuração** | [feature-01-setup.md](./feature-01-setup.md) | P0 | 3 | Dia 1 |
| **Feature 2: Ingestão de PDFs** | [feature-02-ingestao-pdfs.md](./feature-02-ingestao-pdfs.md) | P0 | 5 | Dias 1-2 |
| **Feature 3: Extração de Texto** | [feature-03-extracao-texto.md](./feature-03-extracao-texto.md) | P0 | 8 | Dias 2-4 |
| **Feature 4: Extração de Tabelas** | [feature-04-extracao-tabelas.md](./feature-04-extracao-tabelas.md) | P1 | 5 | Dia 4 |

**Total Semana 1:** 21 story points (4 features)

---

### Semana 2: Alinhamento e Comparação (Dias 6-10)

| Feature | Arquivo | Prioridade | Story Points | Dias |
|---------|---------|------------|--------------|------|
| **Feature 5: Alinhamento de Seções** | [feature-05-alinhamento-secoes.md](./feature-05-alinhamento-secoes.md) | P0 | 8 | Dias 6-8 |
| **Feature 6: Comparação Textual** | [feature-06-comparacao-textual.md](./feature-06-comparacao-textual.md) | P0 | 5 | Dias 9-10 |

**Total Semana 2:** 13 story points (2 features)

---

### Semana 3: Análise Semântica e Output (Dias 11-15)

| Feature | Arquivo | Prioridade | Story Points | Dias |
|---------|---------|------------|--------------|------|
| **Feature 7: Comparação Semântica Agno** | [feature-07-comparacao-semantica-agno.md](./feature-07-comparacao-semantica-agno.md) | P0 | 10 | Dias 11-13 |
| **Feature 8: Comparação de Tabelas** | [feature-08-comparacao-tabelas.md](./feature-08-comparacao-tabelas.md) | P1 | 5 | Dia 13 |
| **Feature 9: Classificação de Severidade** | [feature-09-classificacao-severidade.md](./feature-09-classificacao-severidade.md) | P1 | 5 | Dia 14 |
| **Feature 10: Geração de Output** | [feature-10-geracao-output.md](./feature-10-geracao-output.md) | P0 | 5 | Dias 14-15 |

**Total Semana 3:** 25 story points (4 features)

---

### Semana 3.5: Refinamento e Apresentação (Dias 16-17)

| Feature | Arquivo | Prioridade | Story Points | Dias |
|---------|---------|------------|--------------|------|
| **Feature 11: Refinamento e Apresentação** | [feature-11-refinamento.md](./feature-11-refinamento.md) | P0 | 8 | Dias 16-17 |

**Total Semana 3.5:** 8 story points (1 feature)

---

## Resumo Executivo

### Total do Backlog
- **Total de Features:** 11
- **Total de Story Points:** 67
- **Features Essenciais (P0):** 7 (Setup, Ingestão, Extração Texto, Alinhamento, Comparação Textual, Comparação Semântica Agno, Output, Refinamento)
- **Features Desejáveis (P1):** 4 (Extração Tabelas, Comparação Tabelas, Classificação Severidade)
- **Duração:** 3.5 semanas (17.5 dias úteis)

### User Stories
- **Total de User Stories:** 36
- **Média de US por Feature:** 3.3
- **Todas as US seguem formato:** "Como [papel] Eu quero [ação] Para que [benefício]"
- **100% das US têm critérios de aceite testáveis**

### Estrutura de Cada Feature

Cada arquivo de feature contém:

1. **Metadados:** Prioridade, Sprint, Estimativa, Dependências
2. **Objetivo:** Descrição clara do valor entregue
3. **User Stories (2-5 por feature):**
   - Formato BDD: Como/Eu quero/Para que
   - Critérios de Aceite (3-5 por US)
   - Definição de Pronto
   - Estimativa em story points
4. **Atividades Técnicas:**
   - Atividades Macro (2-5 por feature)
   - Subatividades detalhadas com arquivos Python específicos
5. **Critérios de Testes:**
   - Entrada, Ação, Saída Esperada
   - Testes executáveis manualmente no notebook
6. **Riscos e Mitigações:**
   - Riscos técnicos priorizados
   - Mitigações concretas
7. **Métricas de Sucesso:**
   - Valores alvo quantificáveis

---

## Mapeamento para Arquivos Python

| Módulo Python | Features Relacionadas | Responsabilidades |
|---------------|----------------------|-------------------|
| `src/config.py` | Feature 1 | Variáveis de ambiente, configurações centralizadas |
| `src/pdf_loader.py` | Feature 2 | Validação e carregamento de PDFs (RF-001 a RF-004) |
| `src/text_extractor.py` | Feature 3 | Extração de texto e parsing de hierarquia (RF-005, RF-006, RF-008) |
| `src/table_extractor.py` | Feature 4 | Extração de tabelas com pdfplumber (RF-007) |
| `src/section_aligner.py` | Feature 5 | Alinhamento heurístico + LLM fallback (RF-010 a RF-014) |
| `src/text_comparator.py` | Feature 6 | Diff textual e detecção de mudanças (RF-015 a RF-018) |
| `src/semantic_comparator.py` | Feature 7 | **AGNO CORE** - Classificação semântica (RF-019 a RF-022) |
| `src/table_comparator.py` | Feature 8 | Comparação numérica de tabelas (RF-023 a RF-026) |
| `src/severity_classifier.py` | Feature 9 | Classificação CRITICAL/MEDIUM/LOW (RF-027 a RF-030) |
| `src/output_generator.py` | Feature 10 | DataFrame + visualização (RF-031 a RF-034) |
| `src/utils.py` | Todas | Funções auxiliares compartilhadas |

---

## Priorização e Dependências

### Ordem de Implementação (CRÍTICA)

**DEVE seguir rigorosamente a ordem do pipeline:**

1. **Feature 1** (Setup) → Sem dependências
2. **Feature 2** (Ingestão) → Depende de Feature 1
3. **Feature 3** (Extração Texto) → Depende de Feature 2
4. **Feature 4** (Extração Tabelas) → Depende de Feature 2 (paralela à Feature 3)
5. **Feature 5** (Alinhamento) → Depende de Feature 3
6. **Feature 6** (Comparação Textual) → Depende de Feature 5
7. **Feature 7** (Comparação Semântica Agno) → **CRÍTICA** - Depende de Feature 6
8. **Feature 8** (Comparação Tabelas) → Depende de Feature 4
9. **Feature 9** (Classificação Severidade) → Depende de Features 6 e 7
10. **Feature 10** (Geração Output) → Depende de Feature 9
11. **Feature 11** (Refinamento) → Depende de Feature 10

### Features Essenciais vs Desejáveis

**Se prazo for pressionado, CORTAR features P1 nesta ordem:**
1. Feature 4 (Extração Tabelas) - P1
2. Feature 8 (Comparação Tabelas) - P1 (dependente de Feature 4)
3. Feature 9 (Classificação Severidade) - P1

**NUNCA cortar Features P0:**
- Feature 1, 2, 3, 5, 6, 7, 10, 11 são **essenciais** para validação do PoC

---

## Checkpoints de Validação

### Checkpoint Semana 1 (Dia 5)
**Critérios de Sucesso:**
- [ ] Agno "Hello World" funcional (Feature 1)
- [ ] PDFs ASTM carregados sem erro (Feature 2)
- [ ] Texto extraído com hierarquia de seções preservada (Feature 3)
- [ ] Tempo de extração <60 segundos (Feature 3)

**Decisão:** Se Agno falhar em >30% das tentativas, migrar para OpenAI SDK direto (plano B)

---

### Checkpoint Semana 2 (Dia 10)
**Critérios de Sucesso:**
- [ ] Alinhamento automático com confiança média ≥0.8 (Feature 5)
- [ ] Diffs textuais categorizados corretamente (Feature 6)
- [ ] Fallback LLM funciona quando heurística falha (Feature 5)

**Decisão:** Se alinhamento <80% acurácia, revisar algoritmo ou usar LLM-only

---

### Checkpoint Semana 3 (Dia 15)
**Critérios de Sucesso:**
- [ ] Pipeline end-to-end executa em ≤3 minutos (Feature 11)
- [ ] Agno classifica diferenças com ≥85% concordância humana (Feature 7)
- [ ] Custo por execução <$1.50 (Feature 7)
- [ ] DataFrame + visualização exibidos corretamente (Feature 10)

**Decisão:** Validar viabilidade do Agno (go/no-go)

---

## Métricas de Aceite do PoC

Baseado em `requirements_complete.md` e ADRs:

### Métricas de Negócio
- [ ] **Taxa de Detecção:** ≥95% de mudanças reais detectadas
- [ ] **Precisão Semântica:** ≥85% de concordância humana com classificação LLM
- [ ] **Custo Total PoC:** ≤$50 (APIs LLM para ~10 execuções completas)
- [ ] **Decisão Go/No-Go:** Entregue em apresentação formal ao final de Semana 3.5

### Métricas Técnicas
- [ ] **Taxa de Sucesso Pipeline:** ≥95% de execuções completas sem erros críticos
- [ ] **Cobertura de Requisitos:** 100% dos requisitos essenciais (RF-001 a RF-040 P0) implementados
- [ ] **Confiança Alinhamento:** Média ≥0.8 em alinhamento automático de seções
- [ ] **Fallback Rate:** ≤20% de seções requerem fallback LLM para alinhamento

### Métricas de Performance
- [ ] **Tempo End-to-End:** ≤3 minutos para processar 2 PDFs ASTM (~25MB cada)
- [ ] **Tempo Extração:** ≤60 segundos para extração de texto (PyMuPDF)
- [ ] **Tempo LLM:** ≤90 segundos para todas as chamadas Agno + GPT-4o
- [ ] **Uso de Memória:** ≤4GB RAM pico durante processamento

### Validação do Agno Framework
- [ ] **Taxa de Sucesso Agno:** ≥70% (30% podem usar fallback OpenAI SDK)
- [ ] **Consistência:** ≥90% de classificações idênticas em re-execução (temperature=0.3)
- [ ] **Performance LLM:** P95 ≤10 segundos por diferença

---

## Definition of Done (DoD) do PoC

**PoC considerado COMPLETO quando:**
- [ ] Pipeline end-to-end executa sem erros críticos
- [ ] Notebook está documentado (markdown + comentários)
- [ ] 2 PDFs ASTM processados com sucesso
- [ ] Output exibe diferenças de forma estruturada e legível
- [ ] Tempo de execução ≤3 minutos
- [ ] Framework Agno integrado e funcionando para comparação semântica
- [ ] Apresentação final realizada com Eng. Produto
- [ ] Decisão go/no-go documentada

**PoC considerado EXCELENTE quando (além do DoD acima):**
- [ ] OCR funciona com ≥70% acurácia
- [ ] Comparação de tabelas detecta mudanças numéricas
- [ ] Classificação de severidade implementada
- [ ] Pipeline modular (execução célula por célula)
- [ ] ≥90% das diferenças conhecidas detectadas corretamente

---

## Riscos Principais e Mitigações

### Risco Crítico 1: Agno Framework Instável
**Probabilidade:** Alta | **Impacto:** Crítico
**Mitigação:**
- Checkpoint Dia 5: validar Agno com "Hello World"
- Plano B: migrar para OpenAI SDK direto se taxa de falha >30% (estimado 2-3h)
- Documentar bugs para contribuir com comunidade Agno

### Risco Crítico 2: Performance >3 Minutos
**Probabilidade:** Média | **Impacto:** Alto
**Mitigação:**
- Usar PyMuPDF para texto (60x mais rápido que pdfplumber)
- Limitar chamadas LLM a mudanças significativas (filtro >10 palavras)
- Implementar cache de respostas LLM
- Processar páginas em paralelo se necessário

### Risco Crítico 3: Alinhamento de Seções Falha
**Probabilidade:** Média | **Impacto:** Alto
**Mitigação:**
- Abordagem híbrida: heurística (exact + fuzzy) + fallback LLM
- Checkpoint Semana 2: validar alinhamento em ≥90% dos casos
- Threshold de confiança 0.8: se <0.8, usar LLM para sugestões

---

## Próximos Passos

### Após Conclusão do Backlog

1. **Semana 1 - Dia 1:**
   - Executar `bash scripts/setup.sh` (Feature 1)
   - Validar instalação de todas as dependências
   - Testar Agno "Hello World"

2. **Durante Desenvolvimento:**
   - Marcar user stories como concluídas após validação
   - Atualizar riscos conforme descobertas
   - Documentar bugs do Agno encontrados

3. **Semana 3.5 - Dia 17:**
   - Apresentar PoC para Engenharia de Produto
   - Documentar decisão go/no-go em `docs/decisao_go_no_go.md`
   - Se GO: criar roadmap de MVP (6-8 semanas)

---

## Contato e Suporte

**Dúvidas sobre o backlog:** Consultar documentação de referência:
- `docs/requirements_complete.md` - Requisitos completos (RF-001 a RF-040)
- `docs/adr/ADR-0001-arquitetura-macro-do-sistema.md` - Arquitetura macro
- `docs/adr/ADR-0002-stack-tecnologica.md` - Stack tecnológica
- `CLAUDE.md` - Overview do projeto

**Ferramentas de Tracking:**
- Backlog: Arquivos markdown em `docs/backlog/`
- Progresso: Checklist em cada feature-*.md
- Métricas: Validar ao final de cada checkpoint

---

**Última Atualização:** 30 de Setembro de 2025
**Versão do Backlog:** 1.0
**Status:** Aprovado e Pronto para Implementação
