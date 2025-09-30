# ADR-0001 — Arquitetura Macro do Sistema FastCheckAI

**Status:** Accepted | **Data:** 2025-09-30 | **Dono:** FastCheckAI Team

## 📋 Índice

1. [Contexto](#contexto)
2. [Decisão](#decisão)
3. [Alternativas Consideradas](#alternativas-consideradas)
4. [Consequências](#consequências)
5. [Plano de Implementação](#plano-de-implementação)
6. [Critérios de Revisão](#critérios-de-revisão)
7. [Métricas de Aceite](#métricas-de-aceite)
8. [ADRs Relacionados](#adrs-relacionados)

---

**Resumo da Decisão (TL;DR):**

Adotar **Pipeline Linear ETL em Jupyter Notebook** com **Arquitetura Híbrida** (PyMuPDF + pdfplumber + Agno Framework) para validar viabilidade técnica de comparação automatizada de PDFs em 3.5 semanas, priorizando simplicidade de implementação, aprendizado do framework Agno e baixo custo operacional.

---

## 1. Contexto

### 1.1 Problema ou Objetivo

FastCheckAI é um Proof of Concept (PoC) destinado a **validar a viabilidade técnica de comparação automatizada de documentos PDF técnicos** (normas ASTM A29/A29M versões 2015 vs 2016). O objetivo principal é avaliar a capacidade do framework Agno para orchestração de LLMs em tarefas de análise semântica, entregando resultados em formato estruturado e visualização elaborada em Jupyter Notebook.

**Desafios principais:**
- Prazo apertado de 3.5 semanas com desenvolvedor solo
- Necessidade de aprender novo framework (Agno) durante desenvolvimento
- Processar PDFs técnicos de até 25MB com extração de texto, tabelas e análise semântica
- Manter custo operacional baixo (uso de APIs LLM)
- Entregar solução funcional end-to-end sem infraestrutura de deploy

### 1.2 Fatores Relevantes (Requisitos e Restrições)

**Requisitos de Negócio:**

* Validar framework Agno para futuras aplicações em comparação de documentos técnicos
* Demonstrar capacidade de detecção automatizada de mudanças com ≥95% de acurácia
* Entregar apresentação técnica para decisão go/no-go sobre MVP
* Custo total do PoC ≤ $50 (APIs LLM para ~10 execuções completas)

**Restrições Técnicas:**

* Ambiente de execução: Jupyter Notebook local (sem deploy, Docker ou cloud)
* Prazo fixo: 3.5 semanas (17.5 dias úteis)
* Equipe: 1 desenvolvedor solo aprendendo Agno durante o PoC
* Hardware: Máquina local com ≥8GB RAM, sem GPU dedicada garantida
* Input: 2 PDFs de até 25MB cada (normas técnicas ASTM)
* Performance: Processamento end-to-end ≤3 minutos aceitável

**Requisitos de Usuário:**

* Carregar 2 PDFs via caminho local no filesystem
* Visualizar diferenças em formato tabular estruturado (DataFrame)
* Entender classificação semântica de mudanças (equivalente/menor/significativa)
* Identificar severidade das mudanças (CRÍTICA/MÉDIA/BAIXA)
* Visualização "elaborada" com highlights e estatísticas resumidas

### 1.3 Relação com Outros ADRs

* **Depende de:** N/A (primeiro ADR do projeto)
* **Afeta:** ADRs futuros sobre integração LLM, estratégia de testes, modularização
* **Substitui:** N/A

---

## 2. Decisão

**Adotar arquitetura baseada em Pipeline Linear ETL executado em Jupyter Notebook, utilizando arquitetura híbrida de processamento que combina PyMuPDF (extração de texto), pdfplumber (extração de tabelas), Agno Framework (orchestração LLM) e GPT-3.5-turbo (análise semântica).**

### 2.1 Princípios da Decisão

1. **Simplicidade sobre Otimização:** Priorizar implementação rápida e debugging fácil sobre performance extrema, apropriado para PoC de 3.5 semanas
2. **Aprendizado Guiado:** Framework Agno como componente central para atender objetivo de aprendizado técnico
3. **Modularidade Pragmática:** Separação em camadas (Extração → Alinhamento → Comparação → Análise) sem over-engineering
4. **Cost-Effective:** Minimizar custos com GPT-3.5-turbo e processamento local

### 2.2 Escopo Incluído

**Componentes/Funcionalidades:**

* Pipeline ETL linear com 11 células em Jupyter Notebook (Setup → Visualização)
* Camada de Extração: PyMuPDF para texto + pdfplumber para tabelas + pytesseract para OCR
* Camada de Alinhamento: Heurística (exact match + fuzzy match) com fallback LLM via Agno
* Camada de Comparação: difflib para diff textual + Agno + GPT-3.5 para análise semântica
* Camada de Apresentação: DataFrame pandas + visualização HTML com highlights
* Modularização em 10 módulos Python (`src/*.py`) orquestrados pelo notebook

### 2.3 Escopo Excluído (Se aplicável)

**Fora de Escopo:**

* Deploy em produção (containerização, API REST, frontend standalone)
* Processamento assíncrono ou paralelizado (não essencial para PoC)
* Suporte a formatos além de PDF (DOCX, HTML, etc.)
* Sistema de cache persistente ou banco de dados
* Testes automatizados extensivos (apenas validação manual)
* CI/CD pipeline e infraestrutura como código

---

## 3. Alternativas Consideradas

### 3.1 Comparativo de Alternativas

**⚠️ OBRIGATÓRIO: Mínimo de 3 alternativas, máximo de 5 alternativas**

| Critério | Alt 1: Pipeline Linear ETL (Escolhida) | Alt 2: Microserviços | Alt 3: Serverless Functions | Alt 4: Monolito CLI | Alt 5: Processamento Manual |
|----------|--------------|--------------|--------------|--------------|--------------|
| **Time-to-Market (3.5 semanas)** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Facilidade de Debug** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Custo de Desenvolvimento** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Escalabilidade Futura** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Aprendizado Agno** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **Custo Operacional** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Sistema de Avaliação:** ⭐ (péssimo) | ⭐⭐ (ruim) | ⭐⭐⭐ (médio) | ⭐⭐⭐⭐ (bom) | ⭐⭐⭐⭐⭐ (excelente)

### 3.2 Detalhamento das Alternativas

**Alternativa 1: Pipeline Linear ETL em Notebook (Escolhida)**

* **Descrição:** Notebook Jupyter com 11 células executando pipeline sequencial: PDF Input → Validation → Extraction → Alignment → Comparison → Analysis → Output. Modularização em arquivos Python (`src/`) orquestrados pelas células.
* **Vantagens:**
  - Desenvolvimento rápido com feedback visual imediato
  - Debug trivial (executar célula por célula)
  - Zero overhead de infraestrutura (sem Docker, APIs, servidores)
  - Ideal para PoC: código limpo, documentado inline, fácil apresentação
  - Salvar estados intermediários entre células facilita experimentação
* **Desvantagens:**
  - Escalabilidade limitada (não processa múltiplos PDFs em batch)
  - Não adequado para produção (requer conversão para aplicação standalone)
  - Processamento síncrono (pode ser lento para PDFs muito grandes)
* **Adequação:** **Escolhida porque atende perfeitamente o contexto de PoC com prazo apertado, desenvolvedor solo, entrega em notebook e foco em aprendizado.**

**Alternativa 2: Arquitetura de Microserviços**

* **Descrição:** Separar processamento em serviços independentes: (1) PDF Ingestion Service, (2) Text Extraction Service, (3) LLM Analysis Service, (4) Storage Service. Comunicação via REST APIs ou message broker (RabbitMQ/Kafka).
* **Vantagens:**
  - Alta escalabilidade horizontal (processar múltiplos PDFs simultaneamente)
  - Isolamento de falhas (serviço de OCR falha sem derrubar extração de texto)
  - Tecnologias heterogêneas (Python para LLM, Go para parsing rápido)
  - Preparado para produção desde o início
* **Desvantagens:**
  - Overhead massivo para PoC: Docker Compose, API contracts, service discovery
  - Tempo de desenvolvimento 3-4x maior (estimado 8-10 semanas vs 3.5)
  - Complexidade de debug (logs distribuídos, tracing)
  - Infraestrutura local complexa (múltiplos containers, networking)
* **Adequação:** **Rejeitada devido ao prazo de 3.5 semanas. Over-engineering para PoC.**

**Alternativa 3: Serverless Functions (AWS Lambda / Google Cloud Functions)**

* **Descrição:** Funções serverless para cada etapa do pipeline: (1) Lambda PDF Upload → (2) Lambda Text Extraction → (3) Lambda LLM Analysis → (4) Lambda Result Storage. Orquestração via Step Functions ou Pub/Sub.
* **Vantagens:**
  - Escalabilidade automática (processar 1 ou 1000 PDFs sem mudança de código)
  - Custo pay-per-use (sem servidores idle)
  - Alta disponibilidade out-of-box
  - Infraestrutura gerenciada (sem manutenção de servidores)
* **Desvantagens:**
  - Requer conta cloud ativa (AWS/GCP) com billing configurado
  - Cold start latency (primeira execução pode levar 5-10 segundos)
  - Limitações: timeout (15min AWS Lambda), memória (10GB), tamanho payload (6MB)
  - Debugging complexo (CloudWatch logs, remote debugging)
  - Tempo de setup: 2-3 dias para IAM, networking, CI/CD
* **Adequação:** **Rejeitada porque PoC deve rodar 100% local. Não há requisito de deploy.**

**Alternativa 4: Monolito CLI (Command-Line Application)**

* **Descrição:** Aplicação Python standalone executável via terminal: `python fastcheckai.py --pdf-a astm_2015.pdf --pdf-b astm_2016.pdf --output report.html`. Estrutura modular interna (classes PDFLoader, TextExtractor, SemanticComparator) com CLI via argparse ou Click.
* **Vantagens:**
  - Executável simples (sem Jupyter Server)
  - Facilita automação (bash scripts, cron jobs)
  - Mais próximo de aplicação "real" que notebook
  - Empacotamento via PyInstaller para distribuição
* **Desvantagens:**
  - Perde visualização interativa do notebook (menos impacto na apresentação)
  - Debugging menos intuitivo que células de notebook
  - Requer desenvolvimento de logging estruturado desde início
  - Output report estático (HTML file) vs células interativas
* **Adequação:** **Rejeitada porque requisito explícito é "entrega em Jupyter Notebook" e visualização elaborada inline.**

**Alternativa 5: Processamento Manual (Status Quo)**

* **Descrição:** Não desenvolver ferramenta automatizada. Engenheiro compara PDFs manualmente usando ferramentas existentes: Adobe Acrobat Compare, diff textual, leitura lado a lado.
* **Vantagens:**
  - Zero tempo de desenvolvimento
  - Zero custo de APIs LLM
  - Controle humano 100% sobre julgamento de significância
* **Desvantagens:**
  - Tempo de análise manual: 8-12 horas por par de PDFs (inviável para escala)
  - Erros humanos (fadiga, viés, inconsistência)
  - Não atende objetivo de "validar viabilidade técnica do Agno"
  - Análise semântica limitada (humano pode perder nuances técnicas)
* **Adequação:** **Rejeitada porque elimina o objetivo principal do PoC: validar automação via LLM.**

### 3.3 Justificativa da Escolha

A **Alternativa 1 (Pipeline Linear ETL em Notebook)** foi escolhida porque:

1. **Atende prazo de 3.5 semanas:** Desenvolvimento incremental, testável célula por célula, sem overhead de infraestrutura.
2. **Maximiza aprendizado Agno:** Desenvolvedor pode experimentar framework em ambiente controlado (notebook) com feedback visual imediato.
3. **Debugging trivial:** Executar célula → inspecionar variáveis → ajustar código → re-executar. Ciclo de feedback <30 segundos.
4. **Custo zero de infraestrutura:** Sem Docker, cloud, APIs próprias, CI/CD. Apenas APIs LLM (~$5-15 para 10 execuções).
5. **Apresentação impactante:** Notebook com visualizações inline, markdown explicativo, resultados interativos é mais efetivo que relatório estático.
6. **Modularização suficiente:** Separação em `src/*.py` permite reuso de código em futura aplicação standalone sem reescrita total.

**Comparação com runners-up:**
- **Alternativa 4 (Monolito CLI)** é tecnicamente viável mas perde visualização interativa crítica para apresentação.
- **Alternativa 2 (Microserviços)** e **Alternativa 3 (Serverless)** são over-engineering para PoC: adicionariam 4-6 semanas de desenvolvimento.

---

## 4. Consequências

### 4.1 Positivas

**Desenvolvimento:**

* Ciclo de desenvolvimento rápido (implementar feature → testar → validar em <1 hora)
* Fácil onboarding de stakeholders (qualquer pessoa com Jupyter pode executar)
* Documentação inline via markdown cells (código auto-documentado)
* Reutilização de bibliotecas maduras (PyMuPDF, pandas, Agno)

**Negócio:**

* Validação rápida de viabilidade técnica (decisão go/no-go em 3.5 semanas)
* Custo total do PoC ≤ $50 (APIs LLM + tempo de desenvolvimento)
* Demonstração impactante para stakeholders (visualizações interativas)
* Aprendizado técnico reutilizável em futuros projetos (expertise em Agno)

**Técnico:**

* Baixo acoplamento entre módulos (`src/*.py` independentes)
* Fácil substituição de componentes (trocar PyMuPDF por pdfplumber é mudança de 10 linhas)
* Observabilidade trivial (print statements + células de inspeção)
* Testes manuais eficientes (executar célula específica)

### 4.2 Negativas ou Riscos + Mitigações

**Risco: Agno Framework instável ou com bugs críticos**

* **Probabilidade:** Média (framework lançado em Set/2025, comunidade pequena)
* **Impacto:** Alto (bloqueia objetivo principal do PoC)
* **Mitigação:**
  - **Checkpoint Semana 1 (Dia 5):** Validar setup Agno com exemplo "Hello World" de LLM orchestration
  - **Plano B:** Se Agno falhar, migrar para OpenAI SDK direto (estimado 2-3 horas de refactoring em `semantic_comparator.py`)
  - **Fallback híbrido:** Usar Agno onde funciona, OpenAI API direta onde Agno falha

**Risco: Performance insuficiente (>3 minutos para processar PDFs 25MB)**

* **Probabilidade:** Baixa (PyMuPDF processa 25MB em ~30-60 segundos)
* **Impacto:** Médio (degradação de experiência, mas não bloqueia validação técnica)
* **Mitigação:**
  - Usar PyMuPDF para texto (60x mais rápido que pdfplumber)
  - pdfplumber apenas em páginas com tabelas detectadas (uso seletivo)
  - Limitar chamadas LLM a mudanças significativas (ignorar triviais)
  - Se necessário, processar em chunks e salvar estados intermediários

**Risco: Escalabilidade limitada para MVP futuro**

* **Probabilidade:** Alta (notebook não é arquitetura de produção)
* **Impacto:** Baixo (PoC não precisa escalar; MVP será re-arquitetado)
* **Mitigação:**
  - Modularização em `src/*.py` facilita migração para CLI ou API REST
  - Documentar decisões arquiteturais neste ADR para guiar MVP
  - Considerar Alternativa 4 (Monolito CLI) como próximo passo se go

**Risco: Alinhamento de seções falha em PDFs complexos**

* **Probabilidade:** Média (PDFs técnicos podem ter numeração inconsistente)
* **Impacto:** Alto (comparação incorreta invalida resultados)
* **Mitigação:**
  - Abordagem híbrida: heurística (exact + fuzzy match) + fallback LLM via Agno
  - Threshold de confiança 0.8: se média <0.8, usar LLM para sugestões
  - Validação manual dos resultados durante Semana 2 checkpoint
  - Logging detalhado de alinhamentos para debugging

---

## 5. Plano de Implementação

### 5.1 Fase 1: Setup e Extração (Semana 1 — Dias 1-5)

* **Dia 1:** Setup ambiente (Python 3.12, uv, Jupyter, dependências, .env com API keys)
* **Dia 1-2:** Implementar ingestão PDFs (RF-001 a RF-004): validação tamanho, detecção tipo (nativo/escaneado)
* **Dia 2-3:** Implementar extração texto (RF-005, RF-008): PyMuPDF + parsing hierárquico de seções
* **Dia 3-4:** Implementar extração tabelas (RF-007): pdfplumber seletivo + detecção de páginas com tabelas
* **Dia 4-5:** Implementar OCR básico (RF-006): pytesseract para PDFs escaneados + checkpoint Agno setup

**Critérios de Sucesso Fase 1:**
- [ ] PDFs ASTM 2015/2016 carregados com sucesso
- [ ] Texto extraído com hierarquia de seções preservada
- [ ] Tabelas extraídas em páginas detectadas
- [ ] Agno "Hello World" funcionando (criar agente + executar prompt simples)

### 5.2 Fase 2: Alinhamento e Comparação Textual (Semana 2 — Dias 6-10)

* **Dia 6:** Implementar alinhamento heurístico (RF-010 a RF-012): exact match por ID + fuzzy match por título
* **Dia 7:** Implementar fallback LLM para alinhamento (RF-013 a RF-014): Agno sugere correspondências se confiança <0.8
* **Dia 8:** Detectar seções adicionadas/removidas (RF-015 a RF-016)
* **Dia 9:** Implementar comparação textual (RF-017 a RF-018): difflib para diff + categorização (ADD/REMOVE/MODIFY)
* **Dia 10:** Checkpoint Semana 2: validar alinhamento em ≥90% dos casos reais

**Critérios de Sucesso Fase 2:**
- [ ] Alinhamento automático com confiança média ≥0.8
- [ ] Seções não alinhadas detectadas corretamente
- [ ] Diffs textuais categorizados (ADD/REMOVE/MODIFY)
- [ ] Fallback LLM funciona quando heurística falha

### 5.3 Fase 3: Análise Semântica e Output (Semana 3 — Dias 11-15)

* **Dia 11-12:** Implementar comparação semântica (RF-019 a RF-022): Agno + GPT-3.5 para análise de significância
* **Dia 13:** Implementar comparação tabelas (RF-023 a RF-026): diff numérico com tolerância
* **Dia 14:** Implementar classificação severidade (RF-027 a RF-030): regras CRÍTICA/MÉDIA/BAIXA
* **Dia 15:** Implementar output generator (RF-031 a RF-034): DataFrame + estatísticas + visualização HTML

**Critérios de Sucesso Fase 3:**
- [ ] Análise semântica classifica mudanças como equivalent/minor/significant
- [ ] Tabelas comparadas com diff célula a célula
- [ ] Severidades atribuídas corretamente
- [ ] Pipeline end-to-end executa em ≤3 minutos

### 5.4 Fase 4: Refinamento e Apresentação (Semana 3.5 — Dias 16-17)

* **Dia 16:** Features desejáveis (melhorar visualização, adicionar estatísticas, refinar prompts LLM)
* **Dia 17 (manhã):** Documentação notebook (markdown cells explicativos, README atualizado)
* **Dia 17 (tarde):** Preparação apresentação (slides, demo ao vivo, decisão go/no-go)

**Critérios de Sucesso Fase 4:**
- [ ] Notebook executável do início ao fim sem erros
- [ ] Visualização final aprovada por stakeholders
- [ ] Apresentação técnica preparada (30-45 minutos)
- [ ] Decisão go/no-go documentada

---

## 6. Critérios de Revisão

Revisitar esta decisão se:

**Mudanças de Contexto:**

* PoC validado com sucesso e decisão é GO para MVP (migrar para Alternativa 4: Monolito CLI)
* Prazo estendido para >6 semanas (considerar Alternativa 2: Microserviços)
* Requisito de processar múltiplos PDFs em batch adicionado (notebook não escala)
* Stakeholders exigem aplicação web standalone (migrar para FastAPI + React)

**Gatilhos Técnicos:**

* Performance consistentemente >3 minutos (investigar Alternativa 3: Serverless para paralelização)
* Agno Framework provoca bugs críticos em >30% das execuções (migrar para OpenAI SDK direto)
* Custos de API LLM excedem $50 no PoC (otimizar prompts ou reduzir chamadas)
* Alinhamento de seções falha em >20% dos casos (revisar algoritmo ou usar LLM-only)

---

## 7. Métricas de Aceite

**Métricas de Negócio:**

* **Taxa de Detecção:** ≥95% de mudanças reais detectadas (vs validação manual)
* **Precisão Semântica:** ≥85% de concordância humana com classificação LLM (equivalent/minor/significant)
* **Custo Total PoC:** ≤$50 (APIs LLM para ~10 execuções completas ASTM 2015 vs 2016)
* **Decisão Go/No-Go:** Entregue em apresentação formal ao final de Semana 3.5

**Métricas Técnicas:**

* **Taxa de Sucesso Pipeline:** ≥95% de execuções completas sem erros críticos
* **Cobertura de Requisitos:** 100% dos requisitos essenciais (RF-001 a RF-040) implementados
* **Confiança Alinhamento:** Média ≥0.8 em alinhamento automático de seções
* **Fallback Rate:** ≤20% de seções requerem fallback LLM para alinhamento

**Métricas de Performance:**

* **Tempo End-to-End:** ≤3 minutos para processar 2 PDFs ASTM (~25MB cada)
* **Tempo Extração:** ≤60 segundos para extração de texto (PyMuPDF)
* **Tempo LLM:** ≤90 segundos para todas as chamadas Agno + GPT-3.5 (estimado 20-30 mudanças)
* **Uso de Memória:** ≤4GB RAM pico durante processamento

---

## 8. ADRs Relacionados

### **Arquitetura e Design**

* **ADR-0002** — Estratégia de Integração Agno Framework (futuro)
* **ADR-0003** — Algoritmo de Alinhamento de Seções (futuro)

### **Tecnologia e Stack**

* **ADR-0004** — Escolha de Modelo LLM (GPT-3.5-turbo vs Claude Haiku vs GPT-4) (futuro)
* **ADR-0005** — Estratégia de Parsing de PDFs (PyMuPDF vs pdfplumber tradeoffs) (futuro)

### **Qualidade e Observabilidade**

* **ADR-0006** — Estratégia de Testes para PoC (manual vs automatizado) (futuro)
* **ADR-0007** — Logging e Observabilidade em Notebooks (futuro)

---

**Notas de Implementação:**

Este ADR documenta a decisão arquitetural macro do sistema. Decisões detalhadas sobre componentes específicos (ex: estratégia exata de alinhamento de seções, prompts LLM, formato de output) serão documentadas em ADRs subsequentes conforme necessário durante a implementação.

**Histórico de Revisões:**

* **2025-09-30:** Versão inicial (Status: Accepted)
