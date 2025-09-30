# ADR-0002 — Stack Tecnológica do FastCheckAI

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

Adotar stack tecnológica híbrida com **Python 3.12 + uv + PyMuPDF/pdfplumber + Agno Framework + GPT-4o** para maximizar facilidade de instalação, compatibilidade e qualidade de análise semântica em PoC de 3.5 semanas, priorizando bibliotecas maduras instaláveis via pip e framework Agno para aprendizado técnico.

---

## 1. Contexto

### 1.1 Problema ou Objetivo

FastCheckAI requer escolhas tecnológicas específicas para cada camada do sistema (runtime, PDF processing, LLM orchestration, comparação, visualização) que atendam os requisitos críticos de:

* **Prazo apertado:** 3.5 semanas de desenvolvimento solo
* **Aprendizado:** Desenvolvedor precisa aprender Agno Framework durante implementação
* **Facilidade de setup:** Instalação via pip/uv sem compilação manual
* **Performance:** Processar 2 PDFs de 25MB em ≤3 minutos
* **Custo:** ≤$50 para ~10 execuções completas (APIs LLM)
* **Compatibilidade:** Python 3.12 em ambiente local (Linux/Windows/Mac)

### 1.2 Fatores Relevantes (Requisitos e Restrições)

**Requisitos de Negócio:**

* Validar viabilidade do Agno Framework (objetivo primário do PoC)
* Processar PDFs técnicos com texto nativo, tabelas e potencialmente OCR
* Comparação semântica via LLM (classificação de significância de mudanças)
* Visualização estruturada em Jupyter Notebook

**Restrições Técnicas:**

* Python 3.12+ como linguagem base (requisito de compatibilidade)
* 100% das dependências instaláveis via pip (RNF-017)
* Execução local sem Docker/cloud (ambiente de desenvolvimento único)
* Sem GPU dedicada garantida (CPU-only processing)
* RAM disponível: ~8GB (target ≤4GB durante execução)

**Requisitos de Usuário:**

* Setup inicial ≤10 minutos (cold start com instalação de dependências)
* Todas as configurações em célula única (API keys, paths, thresholds)
* Mensagens de erro legíveis em caso de falha de qualquer biblioteca
* Logs de progresso durante processamento longo (OCR, LLM)

### 1.3 Relação com Outros ADRs

* **Depende de:** ADR-0001 (Arquitetura Macro do Sistema — define pipeline linear em notebook)
* **Afeta:** ADR-0003 (Estratégia de Alinhamento de Seções — depende de bibliotecas de similaridade)
* **Afeta:** ADR-0004 (Escolha de Modelo LLM — integração via Agno/OpenAI SDK)

---

## 2. Decisão

**Adotar stack tecnológica híbrida combinando bibliotecas Python maduras para processamento de dados com framework Agno para orchestração de LLM:**

**Camada de Runtime:**
* Python 3.12 (versão estável mais recente com performance melhorada)
* uv (gerenciador de dependências rápido e moderno)
* Jupyter Notebook 7.0+ (ambiente de execução principal)

**Camada de Processamento PDF:**
* PyMuPDF 1.23+ (extração de texto rápida de PDFs nativos)
* pdfplumber 0.10+ (extração de tabelas complexas)
* pytesseract 0.3.10+ (OCR para PDFs escaneados — desejável)
* Pillow 10.0+ (manipulação de imagens para OCR)

**Camada de LLM Orchestration:**
* Agno 0.x (framework de aprendizado — versão estável a confirmar)
* openai 1.0+ (fallback direto se Agno bloquear)

**Camada de Comparação e Análise:**
* difflib (built-in Python — diff textual)
* rapidfuzz 3.0+ (fuzzy matching rápido para alinhamento)
* pandas 2.0+ (manipulação de dados tabulares)
* numpy 1.24+ (operações numéricas)

**Camada de Visualização:**
* matplotlib 3.7+ (gráficos básicos — opcional)
* tabulate 0.9+ (formatação de tabelas ASCII)
* IPython display (renderização HTML inline)

### 2.1 Princípios da Decisão

1. **Maturidade sobre Novidade:** Priorizar bibliotecas com ≥3 anos de releases estáveis (PyMuPDF, pandas) sobre alternativas experimentais
2. **Instalação Zero-Friction:** Todas as dependências via pip wheel pré-compilado (sem gcc, cmake, rust toolchain)
3. **Agno como Objetivo de Aprendizado:** Aceitar risco de imaturidade do Agno porque validação técnica do framework é objetivo primário do PoC
4. **Balanceamento Custo-Qualidade:** GPT-4o ($0.0025/$0.01 por 1K tokens) oferece análise semântica superior mantendo custo dentro do budget ($12-25 para 10 execuções vs $50 limite)
5. **Modularidade de Substituição:** Design permite trocar biblioteca X por Y mudando 1 arquivo Python

### 2.2 Escopo Incluído

**Componentes Cobertos:**

* Gerenciamento de dependências: uv com `pyproject.toml` (PEP 621 compliant)
* Parsing de PDFs: texto (PyMuPDF), tabelas (pdfplumber), OCR (pytesseract)
* Orquestração LLM: Agno Framework com fallback OpenAI SDK
* Comparação: diff textual (difflib), fuzzy match (rapidfuzz), numérico (numpy)
* Visualização: DataFrames pandas + HTML/Markdown inline

**Versões Mínimas Especificadas:**

```python
# Core
python = ">=3.12,<4.0"
jupyter = "^7.0.0"
pandas = "^2.0.0"
numpy = "^1.24.0"

# PDF Processing
pymupdf = "^1.23.0"
pdfplumber = "^0.10.0"
pytesseract = "^0.3.10"
pillow = "^10.0.0"

# LLM Orchestration
agno = "^0.x.x"  # Versão a confirmar Semana 1
openai = "^1.0.0"

# Text Processing
rapidfuzz = "^3.0.0"
python-Levenshtein = "^0.20.0"

# Visualization
matplotlib = "^3.7.0"
tabulate = "^0.9.0"

# Utilities
python-dotenv = "^1.0.0"
tqdm = "^4.65.0"
```

### 2.3 Escopo Excluído

**Fora de Escopo:**

* Frameworks web (FastAPI, Flask, Streamlit — aplicável apenas para MVP futuro)
* Banco de dados (PostgreSQL, SQLite — persistência não necessária em PoC)
* Processamento paralelo/async (multiprocessing, asyncio — complexidade desnecessária para PoC)
* Vector databases (Weaviate, Pinecone — RAG não é caso de uso deste PoC)
* Ferramentas de build/deploy (Docker, Kubernetes, CI/CD)

---

## 3. Alternativas Consideradas

### 3.1 Categoria 1: Bibliotecas de Processamento PDF

| Critério | PyMuPDF + pdfplumber (Escolhida) | pdfplumber puro | PyPDF2 + camelot | Adobe PDF Services API | Apache PDFBox (py4j) |
|----------|--------------|--------------|--------------|--------------|--------------|
| **Facilidade de Instalação** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Velocidade Extração Texto** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Qualidade Extração Tabelas** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Custo Operacional** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **Maturidade/Estabilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Compatibilidade Python 3.12** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Justificativa:** PyMuPDF 60x mais rápido para texto, pdfplumber superior para tabelas. Abordagem híbrida maximiza velocidade + qualidade.

### 3.2 Categoria 2: Framework LLM

| Critério | Agno Framework (Escolhida) | LangChain | OpenAI SDK direto | LlamaIndex | Anthropic SDK (Claude) |
|----------|--------------|--------------|--------------|--------------|--------------|
| **Facilidade de Instalação** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maturidade/Estabilidade** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Documentação** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Adequação ao Objetivo PoC** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Curva de Aprendizado** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Suporte a Workflows** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Justificativa:** Agno é objetivo primário de aprendizado do PoC (requisito de negócio). Risco de imaturidade mitigado com fallback OpenAI SDK.

### 3.3 Categoria 3: Modelo LLM

| Critério | GPT-4o (Escolhida) | GPT-3.5-turbo | GPT-4 | Claude 3 Haiku | GPT-4o-mini |
|----------|--------------|--------------|--------------|--------------|--------------|
| **Custo por 1K tokens (input)** | ⭐⭐⭐ ($0.0025) | ⭐⭐⭐⭐ ($0.0005) | ⭐ ($0.03) | ⭐⭐⭐⭐⭐ ($0.00025) | ⭐⭐⭐⭐⭐ ($0.00015) |
| **Qualidade de Análise Semântica** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Latência (P95)** | ⭐⭐⭐⭐⭐ (2-4s) | ⭐⭐⭐⭐ (3-6s) | ⭐⭐⭐ (5-15s) | ⭐⭐⭐⭐ (2-5s) | ⭐⭐⭐⭐⭐ (1-2s) |
| **Contexto Suportado** | ⭐⭐⭐⭐⭐ (128k) | ⭐⭐⭐⭐ (16k) | ⭐⭐⭐⭐⭐ (128k) | ⭐⭐⭐⭐⭐ (200k) | ⭐⭐⭐⭐⭐ (128k) |
| **Facilidade de Integração** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maturidade/Disponibilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Justificativa:** GPT-4o oferece excelente balanceamento entre qualidade de análise semântica (superior ao GPT-3.5-turbo) e custo controlado ($12-25 para 10 execuções vs $50 budget). Contexto de 128k tokens elimina risco de truncamento em seções longas.

### 3.4 Categoria 4: Gerenciador de Dependências

| Critério | uv (Escolhida) | pip + venv | poetry | conda | pipenv |
|----------|--------------|--------------|--------------|--------------|--------------|
| **Velocidade de Instalação** | ⭐⭐⭐⭐⭐ (10-100x) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Facilidade de Uso** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Compatibilidade Python 3.12** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Lock Files** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maturidade** | ⭐⭐⭐ (2024) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Adoção pela Comunidade** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Justificativa:** uv oferece velocidade de instalação 10-100x superior (crítico para setup rápido do PoC). Suporta nativamente `pyproject.toml` (PEP 621) eliminando necessidade de requirements.txt.

### 3.5 Detalhamento das Alternativas — PDF Processing

**Alternativa 1: PyMuPDF + pdfplumber (Escolhida)**

* **Descrição:** Abordagem híbrida usando PyMuPDF (também conhecido como fitz) para extração rápida de texto corrido e pdfplumber para parsing preciso de tabelas complexas
* **Vantagens:**
  - PyMuPDF processa 25MB de PDF em ~30-60 segundos (60x mais rápido que pdfplumber puro)
  - pdfplumber detecta células mescladas, bordas de tabelas e layouts complexos
  - Ambas instaláveis via pip wheel pré-compilado (sem dependências C externas)
  - Preservação de hierarquia de seções via regex de títulos numerados
* **Desvantagens:**
  - Requer manutenção de 2 bibliotecas diferentes (updates, bugs)
  - Lógica de decisão: "quando usar PyMuPDF vs pdfplumber?" adiciona complexidade
  - pdfplumber pode ser lento em páginas com muitas tabelas (1-2s/página)
* **Adequação:** **Escolhida porque maximiza performance (PyMuPDF) e qualidade de tabelas (pdfplumber). Complexidade adicional é aceitável para PoC.**

**Alternativa 2: pdfplumber puro**

* **Descrição:** Usar apenas pdfplumber para todas as operações (texto + tabelas)
* **Vantagens:**
  - Biblioteca única (simplicidade, menos dependências)
  - Extração de tabelas superior (detecta células mescladas, layouts complexos)
  - Preservação de layout espacial (posição x,y de elementos)
  - Instalação trivial via pip
* **Desvantagens:**
  - 60x mais lento que PyMuPDF para texto corrido (90-120 segundos para 25MB vs 30-60s)
  - Pode exceder target de 3 minutos end-to-end se PDF tiver muitas páginas
  - Consumo de memória maior (processa página inteira em RAM)
* **Adequação:** **Rejeitada devido à performance. Risco de exceder 3 minutos end-to-end.**

**Alternativa 3: PyPDF2 + camelot**

* **Descrição:** PyPDF2 para extração de texto, camelot-py para tabelas
* **Vantagens:**
  - camelot-py usa Lattice mode (detecção de bordas via OpenCV) para tabelas complexas
  - PyPDF2 é lightweight (pacote pequeno, <1MB)
  - Open source sem dependências de licenças comerciais
* **Desvantagens:**
  - camelot requer Ghostscript + Tkinter instalados no sistema (não via pip puro)
  - PyPDF2 tem bugs conhecidos em PDFs malformados (menos robusto que PyMuPDF)
  - Instalação não é zero-friction (requer sudo apt-get install ghostscript)
* **Adequação:** **Rejeitada devido à complexidade de instalação (viola RNF-017: 100% via pip).**

**Alternativa 4: Adobe PDF Services API**

* **Descrição:** API cloud da Adobe para parsing de PDFs com IA (extract text, tables, figures)
* **Vantagens:**
  - Qualidade state-of-the-art (treinado em milhões de PDFs)
  - Zero dependências locais (chamada HTTP)
  - Suporta PDFs complexos (escaneados, multi-coluna, layouts exóticos)
  - Extrai figuras e metadados estruturados
* **Desvantagens:**
  - Custo: $0.05-0.15 por PDF (~$1-3 para 10 execuções, mas limite de 500 páginas free tier)
  - Latência: 10-30 segundos por PDF (upload + processamento cloud)
  - Requer conta Adobe + cartão de crédito mesmo em free tier
  - Vendor lock-in (migrar para outra solução requer reescrita total)
* **Adequação:** **Rejeitada devido a custo adicional e dependência de serviço externo. PoC deve ser 100% local.**

**Alternativa 5: Apache PDFBox (via py4j)**

* **Descrição:** Usar PDFBox (biblioteca Java) via py4j bridge para parsing de PDFs
* **Vantagens:**
  - PDFBox é enterprise-grade (usado por Apache Solr, Tika)
  - Suporte robusto a PDFs malformados
  - Extração de metadados XMP completa
  - Comunidade ativa (Apache Foundation)
* **Desvantagens:**
  - Requer JVM instalado (Java 8+) no sistema local
  - py4j adiciona overhead de comunicação inter-processo (20-30% slower)
  - Setup complexo (JAVA_HOME, classpath, jars)
  - Debugging difícil (stacktraces Java misturados com Python)
* **Adequação:** **Rejeitada devido à complexidade de setup (requer JVM). Viola princípio de instalação zero-friction.**

### 3.6 Detalhamento das Alternativas — LLM Framework

**Alternativa 1: Agno Framework (Escolhida)**

* **Descrição:** Framework Python moderno para orchestração de workflows com LLMs, lançado em Set/2025
* **Vantagens:**
  - **Atende objetivo primário do PoC:** validar viabilidade técnica do Agno (requisito de negócio)
  - Abstrações de alto nível para workflows (chains, agents, tools)
  - Integração nativa com OpenAI, Anthropic, open-source models
  - Sintaxe declarativa para prompts e parsing de outputs
* **Desvantagens:**
  - **Imaturidade:** Lançado recentemente (Set/2025), comunidade pequena, poucos exemplos
  - Possíveis bugs críticos ou breaking changes em versões minor
  - Documentação incompleta ou desatualizada
  - Risco de bloqueio do PoC se bugs não forem resolvidos rapidamente
* **Adequação:** **Escolhida PORQUE validação do Agno é objetivo primário do PoC. Risco mitigado com fallback OpenAI SDK.**

**Alternativa 2: LangChain**

* **Descrição:** Framework maduro (2022) para aplicações LLM com ampla adoção
* **Vantagens:**
  - Maturidade: 2+ anos, 100k+ estrelas GitHub, documentação extensa
  - Ecossistema rico: agents, tools, retrievers, memory, callbacks
  - Suporte a 50+ LLM providers (OpenAI, Anthropic, Cohere, HuggingFace)
  - Comunidade ativa (respostas rápidas no Discord)
* **Desvantagens:**
  - **Não atende objetivo do PoC:** validar Agno, não LangChain
  - Over-engineering para caso de uso simples (comparação de texto)
  - Abstrações pesadas (muitos conceitos: chains, agents, memory, tools)
  - Mudanças frequentes de API (breaking changes entre minor versions)
* **Adequação:** **Rejeitada porque não atende objetivo de aprendizado do Agno. Tecnicamente superior mas fora do escopo.**

**Alternativa 3: OpenAI SDK direto**

* **Descrição:** Usar openai Python library diretamente sem framework de orchestração
* **Vantagens:**
  - Simplicidade máxima (código direto, sem abstrações)
  - Zero curva de aprendizado (API oficial, documentação excelente)
  - Estabilidade garantida (mantido pela OpenAI)
  - Debugging trivial (1 chamada = 1 request HTTP)
* **Desvantagens:**
  - **Não atende objetivo do PoC:** validar Agno Framework
  - Sem abstrações para workflows complexos (retry logic, fallbacks, parsing)
  - Código verbose para casos complexos (multi-step reasoning, tool use)
  - Vendor lock-in OpenAI (migrar para Claude requer reescrita)
* **Adequação:** **Rejeitada como solução primária. Usada como fallback se Agno bloquear.**

**Alternativa 4: LlamaIndex**

* **Descrição:** Framework focado em RAG (Retrieval-Augmented Generation) e knowledge bases
* **Vantagens:**
  - Otimizado para casos de uso de busca/recuperação de documentos
  - Índices eficientes (vector stores, graph stores)
  - Query engines sofisticados (sub-question, multi-step reasoning)
  - Integração com 15+ vector databases
* **Desvantagens:**
  - **Foco errado:** RAG não é necessário neste PoC (comparação direta de 2 PDFs)
  - Over-engineering: vector stores, embeddings, retrieval desnecessários
  - Curva de aprendizado moderada (conceitos de indexing, querying)
  - Não atende objetivo de validar Agno
* **Adequação:** **Rejeitada porque caso de uso não é RAG. Framework excelente mas inadequado para este problema.**

**Alternativa 5: Anthropic SDK (Claude)**

* **Descrição:** Usar anthropic Python library para integração com Claude models
* **Vantagens:**
  - Claude 3 Haiku: latência baixíssima (1-3s), custo competitivo ($0.00025/1k tokens)
  - Context window gigante (200k tokens — processa PDFs completos)
  - Qualidade de análise superior para textos longos
  - API simples e estável
* **Desvantagens:**
  - **Não atende objetivo do PoC:** validar Agno com OpenAI models
  - Vendor lock-in Anthropic
  - Menor adoção que OpenAI (menos exemplos, comunidade menor)
  - Agno pode ter integração menos testada com Anthropic
* **Adequação:** **Rejeitada como solução primária. Considerada para Fase 2 se custo OpenAI exceder budget.**

### 3.7 Justificativa da Escolha — Stack Completa

A stack escolhida (Python 3.12 + uv + PyMuPDF/pdfplumber + Agno + GPT-4o) foi selecionada porque:

1. **Atende objetivo primário do PoC:** Validar framework Agno (requisito de negócio não-negociável)
2. **Maximiza velocidade de implementação:** Todas as bibliotecas instaláveis via pip em <10 minutos
3. **Balanceia custo-qualidade:** GPT-4o mantém custo dentro do budget (~$12-25 para 10 execuções vs $50 limite) enquanto oferece análise semântica superior ao GPT-3.5-turbo
4. **Balanceia performance:** PyMuPDF (rápido) + pdfplumber (preciso) atende target ≤3 minutos
5. **Minimiza riscos:** Fallback OpenAI SDK se Agno bloquear (migração estimada em 2-3 horas)
6. **Compatibilidade garantida:** Python 3.12 + todas as libs testadas em Linux/Windows/Mac

**Comparação com runners-up:**

* **LangChain:** Tecnicamente superior mas não atende objetivo de aprendizado Agno
* **GPT-4:** Qualidade marginalmente melhor (5-10%) mas custo 60x maior (inviável para PoC)
* **pdfplumber puro:** Mais simples mas risco de exceder 3 minutos (performance crítica)

---

## 4. Consequências

### 4.1 Positivas

**Desenvolvimento:**

* Setup inicial rápido: `uv install` em <2 minutos (10-100x faster que pip tradicional)
* Debugging facilitado: Bibliotecas maduras (PyMuPDF, pandas) com stacktraces claros
* Documentação abundante: PyMuPDF, pdfplumber, OpenAI SDK têm centenas de exemplos online
* Modularidade: Trocar PyMuPDF por alternativa é mudança de 1 arquivo (`text_extractor.py`)

**Negócio:**

* Custo total estimado: $12-25 para 10 execuções completas (GPT-4o: ~200k tokens @ $0.0025/1k input, $0.01/1k output)
* Validação do Agno entregue (objetivo primário do PoC)
* Decisão go/no-go informada sobre viabilidade técnica do framework
* Conhecimento reutilizável em futuros projetos SIDI

**Técnico:**

* Performance: Pipeline end-to-end estimado em 90-150 segundos (bem abaixo de 3 minutos)
* Compatibilidade: Python 3.12 suportado por todas as bibliotecas escolhidas
* Zero dependências do sistema: Todas as libs via pip wheel (exceto Tesseract para OCR — desejável)
* Facilidade de migração: Código modular permite evoluir para CLI/API em MVP

### 4.2 Negativas ou Riscos + Mitigações

**Risco: Agno Framework instável ou com bugs críticos**

* **Probabilidade:** Alta (framework lançado em Set/2025, <6 meses de maturidade)
* **Impacto:** Alto (bloqueia objetivo primário do PoC — validação do Agno)
* **Mitigação:**
  - **Checkpoint Dia 5:** Validar Agno com "Hello World" (criar agente + executar prompt simples)
  - **Plano B (Semana 2):** Se bugs críticos em >30% das execuções, migrar `semantic_comparator.py` para OpenAI SDK direto (estimado 2-3 horas)
  - **Documentar bugs:** Reportar issues no GitHub Agno para contribuir com comunidade
  - **Versão pinada:** Usar `agno==0.x.x` exata no pyproject.toml (evitar updates automáticos)

**Risco: PyMuPDF falha em PDFs complexos (multiplas colunas, layouts exóticos)**

* **Probabilidade:** Média (PDFs técnicos ASTM geralmente bem-formados)
* **Impacto:** Alto (extração incorreta invalida comparação)
* **Mitigação:**
  - **Validação manual:** Comparar extração PyMuPDF com leitura manual de 2-3 seções críticas
  - **Fallback pdfplumber:** Se PyMuPDF falhar, processar página com pdfplumber (mais lento mas robusto)
  - **Logging detalhado:** Registrar número de caracteres extraídos por página (detectar páginas vazias)
  - **OCR como último recurso:** Se texto <50 chars/página, tentar pytesseract OCR

**Risco: Custo GPT-4o excede $50 no PoC**

* **Probabilidade:** Baixa (estimativa: 200k tokens × $0.0005 = $100, mas contexto menor esperado)
* **Impacto:** Baixo (orçamento pode ser estendido se PoC for bem-sucedido)
* **Mitigação:**
  - **Limitar contexto:** Enviar apenas diff textual para LLM (não PDF completo)
  - **Filtrar diferenças triviais:** Ignorar mudanças <10 palavras antes de chamar LLM
  - **Cache de respostas:** Salvar outputs LLM em `.cache/` para re-execuções sem custo
  - **Monitorar uso:** Exibir custo estimado após cada execução completa

**Risco: Compatibilidade Python 3.12 quebrada em alguma biblioteca**

* **Probabilidade:** Baixa (Python 3.12 lançado em Out/2023, >1 ano de adoção)
* **Impacto:** Alto (bloqueia setup inicial do PoC)
* **Mitigação:**
  - **Teste de compatibilidade Dia 1:** Executar `uv install` + import de todas as libs
  - **Fallback Python 3.11:** Se incompatibilidade detectada, downgrade para Python 3.11.9 (todas as libs compatíveis)
  - **Uso de wheels pré-compilados:** uv prioriza wheels (evita compilação que pode falhar em 3.12)
  - **Documentar no README:** Especificar versão Python testada

**Risco: pytesseract OCR de baixa qualidade (<70% acurácia)**

* **Probabilidade:** Média (depende da qualidade de digitalização dos PDFs)
* **Impacto:** Médio (OCR é requisito desejável, não essencial)
* **Mitigação:**
  - **Marcar como desejável:** OCR não bloqueia validação core do PoC
  - **Pré-processamento de imagens:** Usar Pillow para binarização, remoção de ruído
  - **Tesseract config:** Ajustar `--psm 6` (uniform text block) para documentos técnicos
  - **Fallback manual:** Documentar páginas com OCR falho para revisão manual

---

## 5. Plano de Implementação

### 5.1 Fase 1: Setup e Validação de Compatibilidade (Dia 1)

* **Atividade 1.1:** Instalar Python 3.12 + uv via script oficial
* **Atividade 1.2:** Validar `pyproject.toml` com todas as libs escolhidas (versões mínimas)
* **Atividade 1.3:** Executar `uv install` e validar imports (PyMuPDF, pdfplumber, pandas, agno, openai)
* **Atividade 1.4:** Configurar `.env` com `OPENAI_API_KEY` (teste com `openai.chat.completions.create`)
* **Atividade 1.5:** Executar Agno "Hello World": criar agente + prompt simples + validar resposta

**Critérios de Sucesso Fase 1:**
- [ ] Todas as bibliotecas instaladas sem erros de compilação
- [ ] Imports funcionando em notebook Jupyter
- [ ] OpenAI API key validada (chamada teste bem-sucedida)
- [ ] Agno Framework funcional (executou prompt simples)

### 5.2 Fase 2: Integração de Bibliotecas de PDF (Dias 2-4)

* **Atividade 2.1:** Implementar `pdf_loader.py` com validação de tamanho (≤25MB)
* **Atividade 2.2:** Implementar `text_extractor.py` usando PyMuPDF para extração rápida
* **Atividade 2.3:** Implementar detecção de tabelas e extração via pdfplumber
* **Atividade 2.4:** Implementar fallback OCR com pytesseract para PDFs escaneados
* **Atividade 2.5:** Testar extração nos PDFs ASTM 2015/2016 e validar qualidade

**Critérios de Sucesso Fase 2:**
- [ ] PDFs ASTM carregados e validados
- [ ] Texto extraído com PyMuPDF em <60 segundos
- [ ] Tabelas detectadas e extraídas com pdfplumber
- [ ] Hierarquia de seções preservada (regex de títulos funcionando)

### 5.3 Fase 3: Integração Agno + GPT-4o (Dias 11-13)

* **Atividade 3.1:** Implementar `semantic_comparator.py` com Agno Framework
* **Atividade 3.2:** Criar prompts para classificação semântica (equivalent/minor/significant)
* **Atividade 3.3:** Configurar retry logic e timeout (30s por chamada LLM)
* **Atividade 3.4:** Implementar fallback OpenAI SDK direto se Agno falhar
* **Atividade 3.5:** Testar análise semântica em 5-10 diferenças reais

**Critérios de Sucesso Fase 3:**
- [ ] Agno executa prompts de classificação sem erros
- [ ] Respostas LLM parseadas corretamente (JSON structured output)
- [ ] Fallback OpenAI SDK funciona se Agno bloquear
- [ ] Custo por execução <$2 (validado em testes)

### 5.4 Fase 4: Otimização e Documentação (Dias 16-17)

* **Atividade 4.1:** Adicionar cache de respostas LLM (evitar re-processamento)
* **Atividade 4.2:** Otimizar prompts (reduzir tokens enviados)
* **Atividade 4.3:** Documentar setup em `README.md` (passo a passo instalação)
* **Atividade 4.4:** Gerar `uv.lock` final para reprodutibilidade de ambiente
* **Atividade 4.5:** Validar instalação zero-friction em máquina limpa

**Critérios de Sucesso Fase 4:**
- [ ] Setup completo ≤10 minutos (fresh install)
- [ ] Documentação completa (qualquer pessoa pode executar)
- [ ] Cache funcional (re-execuções não custam $)
- [ ] Versões pinadas (reprodutibilidade garantida)

---

## 6. Critérios de Revisão

Revisitar esta decisão se:

**Mudanças de Contexto:**

* PoC validado e decisão é GO para MVP (considerar FastAPI + async processing)
* Requisito de processar >10 PDFs em batch adicionado (avaliar processamento paralelo)
* Budget de LLM aumentado para >$200 (considerar GPT-4 para melhor qualidade)
* Necessidade de deploy em produção (adicionar Docker, CI/CD, monitoring)

**Gatilhos Técnicos:**

* Agno Framework causa bugs em >30% das execuções (migrar para LangChain ou OpenAI SDK)
* Performance PyMuPDF + pdfplumber excede 3 minutos consistentemente (avaliar serverless processing)
* Custo GPT-4o excede $50 no PoC (otimizar prompts, cache de respostas, ou downgrade para GPT-3.5-turbo)
* Incompatibilidade Python 3.12 detectada (downgrade para Python 3.11)
* OCR pytesseract com acurácia <50% (avaliar EasyOCR ou Textract)

---

## 7. Métricas de Aceite

**Métricas de Instalação:**

* **Tempo de setup:** ≤10 minutos (fresh install com uv)
* **Taxa de sucesso de instalação:** 100% em Linux/Windows/Mac
* **Dependências via pip:** 100% (exceto Tesseract opcional para OCR)

**Métricas de Performance:**

* **Tempo de extração texto (PyMuPDF):** ≤60 segundos para 25MB PDF
* **Tempo de extração tabelas (pdfplumber):** ≤30 segundos para 20 tabelas
* **Latência LLM (GPT-4o):** ≤4 segundos P95 por chamada
* **Tempo end-to-end:** ≤3 minutos para pipeline completo

**Métricas de Custo:**

* **Custo por execução:** ≤$1.50 (10 execuções = $15)
* **Custo total PoC:** ≤$50 (incluindo experimentação e erros)

**Métricas de Qualidade:**

* **Taxa de sucesso PyMuPDF:** ≥95% em PDFs nativos bem-formados
* **Taxa de sucesso pdfplumber:** ≥90% em tabelas grid simples
* **Acurácia OCR pytesseract:** ≥70% em PDFs escaneados qualidade média
* **Taxa de sucesso Agno:** ≥70% (30% podem usar fallback OpenAI SDK)

**Métricas de Compatibilidade:**

* **Python 3.12:** 100% compatível
* **uv install:** 100% sucesso
* **Cross-platform:** Testado em Linux + (Windows ou Mac)

---

## 8. ADRs Relacionados

### **Arquitetura e Pipeline**

* **ADR-0001** — Arquitetura Macro do Sistema (define pipeline linear em notebook)

### **Tecnologia e Integrações (Futuros)**

* **ADR-0003** — Algoritmo de Alinhamento de Seções (usa rapidfuzz desta stack)
* **ADR-0004** — Escolha de Modelo LLM para MVP (avaliar GPT-4 vs Claude se go)
* **ADR-0005** — Estratégia de Cache de Respostas LLM (otimizar custos)

### **Qualidade e Performance (Futuros)**

* **ADR-0006** — Estratégia de Testes de Performance (validar ≤3 minutos)
* **ADR-0007** — Tratamento de Erros de Bibliotecas de PDF (fallbacks robustos)

---

**Notas de Implementação:**

Este ADR documenta as escolhas tecnológicas específicas para cada camada do sistema. Todas as versões especificadas são mínimas; versões patch superiores são compatíveis (ex: `pymupdf>=1.23.0` aceita 1.23.5). Decisões sobre configurações específicas de cada biblioteca (ex: Tesseract PSM mode, GPT-4o temperature) serão documentadas inline no código.

**Histórico de Revisões:**

* **2025-09-30:** Versão inicial (Status: Accepted)
