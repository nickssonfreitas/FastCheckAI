# Especificação Completa de Requisitos — FastCheckAI PoC

**Versão:** 1.0
**Data:** 30 de Setembro de 2025
**Status:** Baseline Aprovada
**Projeto:** FastCheckAI — Prova de Conceito para Comparação Automatizada de PDFs Técnicos
**Organização:** SIDI — Área de Engenharia de Produto

---

## 1. Executive Summary

### 1.1 Visão Geral do Projeto

O **FastCheckAI** é uma Prova de Conceito (PoC) desenvolvida para validar a viabilidade técnica da comparação automatizada entre versões de documentos técnicos em formato PDF, com foco inicial em normas técnicas como ASTM A29/A29M (versões 2015 e 2016).

A PoC será desenvolvida em ambiente Jupyter Notebook local, sem necessidade de deploy ou containerização, com duração estimada de **3.5 semanas** e execução por **1 desenvolvedor solo**.

### 1.2 Objetivos de Negócio

| Objetivo | Descrição | KPI |
|----------|-----------|-----|
| **Validação Técnica** | Comprovar viabilidade do framework Agno para comparação semântica de documentos técnicos | Implementação funcional do pipeline end-to-end |
| **Aprendizado** | Capacitar o desenvolvedor no uso do framework Agno durante a PoC | Domínio básico do framework ao final das 3.5 semanas |
| **Decisão Go/No-Go** | Fornecer evidências técnicas para decisão de continuidade do projeto | Relatório técnico apresentável à Engenharia de Produto |
| **Redução de Esforço Manual** | Demonstrar potencial de automação na revisão de normas técnicas | Processamento completo de 2 PDFs em até 3 minutos |

### 1.3 Stakeholders

| Papel | Descrição | Nível de Engajamento |
|-------|-----------|---------------------|
| **Desenvolvedor** | Responsável pela implementação e decisão go/no-go | Alto (único executor) |
| **Área de Engenharia de Produto** | Avaliadores finais da viabilidade técnica | Médio (revisão final) |
| **SIDI** | Patrocinador institucional | Baixo (acompanhamento) |

### 1.4 Escopo Geral

**INCLUI:**
- Comparação de PDFs técnicos (até 25MB)
- Extração de texto nativo e via OCR
- Alinhamento de seções correspondentes
- Detecção de diferenças textuais e semânticas com LLM
- Comparação de tabelas numéricas
- Visualização de resultados no notebook

**EXCLUI:**
- Deploy em produção
- Interface web ou mobile
- Processamento batch de múltiplos PDFs
- Análise de figuras e diagramas
- Sistema de autenticação/autorização
- Integração com sistemas externos
- Persistência em banco de dados

### 1.5 Restrições Críticas

| Categoria | Restrição |
|-----------|-----------|
| **Tempo** | 3.5 semanas (deadline fixo) |
| **Recursos** | 1 desenvolvedor (sem equipe) |
| **Infraestrutura** | Ambiente local (laptop/desktop) |
| **Tecnologia** | Framework Agno (aprendizado requerido) |
| **Formato Entrega** | Jupyter Notebook executável |
| **Usuários** | Validação técnica interna (sem piloto externo) |

---

## 2. Stage Recaps — Análise Detalhada das 12 Etapas

### 2.1 Stage 1: Definição de Escopo e Contexto do Projeto

**FATOS CONFIRMADOS:**
- PoC para uso interno do SIDI
- Objetivo: validar framework e abordagem de comparação de PDFs técnicos
- Duração: 3.5 semanas (deadline fixo)
- Desenvolvedor: 1 pessoa (trabalho solo)
- Foco inicial: normas ASTM A29/A29M (versões 2015 vs 2016)

**PREMISSAS ESTABELECIDAS:**
- O desenvolvedor tem conhecimento básico de Python e Jupyter Notebooks
- Infraestrutura local suficiente para processar PDFs de até 25MB
- Framework Agno possui documentação acessível para aprendizado rápido
- ASTM 2015 vs 2016 representam caso de uso suficiente para validação

**DADOS FALTANTES:**
- Background técnico exato do desenvolvedor com NLP/LLMs
- Especificações de hardware da máquina local
- Versão específica do framework Agno a ser utilizada

---

### 2.2 Stage 2: Tipo de Artefato e Ambiente de Execução

**FATOS CONFIRMADOS:**
- Ambiente: Jupyter Notebook local (sem deploy)
- Sem necessidade de Docker ou containerização
- Framework preferencial: Agno (necessário aprender durante PoC)
- LLM para comparação semântica de diferenças

**PREMISSAS ESTABELECIDAS:**
- Desenvolvedor possui Python 3.8+ instalado localmente
- Acesso a APIs de LLM (OpenAI, Anthropic ou similar)
- Bibliotecas Python compatíveis com ambiente local (sem conflitos de versão)
- Jupyter Notebook suficiente para demonstração de viabilidade

**DADOS FALTANTES:**
- Modelo LLM específico a ser utilizado (GPT-4, Claude, Llama?)
- Orçamento/limites de uso de APIs de LLM
- Versão do Python e bibliotecas já instaladas no ambiente

---

### 2.3 Stage 3: Stakeholders e Usuários

**FATOS CONFIRMADOS:**
- Stakeholder principal: Área de Engenharia de Produto (avaliação final)
- Sem usuário-piloto (validação técnica interna apenas)
- Decisão go/no-go: próprio desenvolvedor
- Formato de entrega: Jupyter Notebook executável

**PREMISSAS ESTABELECIDAS:**
- Engenharia de Produto tem conhecimento técnico para avaliar resultados
- Critérios de aceitação implícitos (não formalmente definidos)
- Apresentação final será demonstração técnica (não comercial)

**DADOS FALTANTES:**
- Critérios específicos da Engenharia de Produto para aprovação
- Formato esperado da apresentação final
- Necessidade de documentação técnica adicional

---

### 2.4 Stage 4: Perfis de Acesso e Permissões

**FATOS CONFIRMADOS:**
- Não aplicável (execução local, sem sistema multi-usuário)
- Sem necessidade de autenticação/autorização

**PREMISSAS ESTABELECIDAS:**
- PDFs de entrada podem ser acessados diretamente via filesystem local
- Sem controle de acesso a ser implementado

**DADOS FALTANTES:**
- Nenhum (escopo não aplicável)

---

### 2.5 Stage 5: Infraestrutura e Recursos Técnicos

**FATOS CONFIRMADOS:**
- Time: 1 desenvolvedor
- Infraestrutura: Local (laptop/desktop)
- Bibliotecas: Agno + bibliotecas Python de fácil instalação
- Deploy: Não aplicável
- Docker: Não

**PREMISSAS ESTABELECIDAS:**
- Máquina local tem capacidade para processar PDFs de até 25MB
- Conexão com internet para APIs de LLM
- Pip/conda disponível para instalação de dependências

**DADOS FALTANTES:**
- Especificações de hardware (RAM, CPU)
- Limitações de rede/firewall para acesso a APIs externas

---

### 2.6 Stage 6: Tecnologias e Frameworks

**FATOS CONFIRMADOS:**
- Framework Agno (aprendizado durante PoC)
- LLM para comparação semântica
- Python como linguagem base
- Bibliotecas "fáceis de instalar" (evitar compilação complexa)

**PREMISSAS ESTABELECIDAS:**
- Agno possui integração nativa com LLMs populares
- OCR será necessário: Tesseract ou biblioteca similar
- Parsing de PDFs: PyMuPDF, pdfplumber ou similar
- Pandas para manipulação de tabelas

**DADOS FALTANTES:**
- Compatibilidade específica do Agno com versão do Python
- Requisitos de GPU para OCR/LLM (se aplicável)

---

### 2.7 Stage 7: Requisitos Funcionais — Entrada de Dados

**FATOS CONFIRMADOS:**
- PDFs: até 25MB
- Documentos base: ASTM 2015 vs 2016
- OCR: Obrigatório (suportar PDFs escaneados)
- Processamento: Um par de PDFs por vez (não batch)
- Entrada via path local (não upload web)

**PREMISSAS ESTABELECIDAS:**
- PDFs bem formados (não corrompidos)
- Estrutura de seções identificável (headers, numeração)
- Tabelas em formato grid reconhecível

**DADOS FALTANTES:**
- Tratamento de erros para PDFs inválidos
- Validação de tamanho/formato antes do processamento

---

### 2.8 Stage 8: Requisitos Funcionais — Processamento

**FATOS CONFIRMADOS:**
- Detecção de diferenças: todas (texto, tabelas, estrutura)
- Alinhamento de seções correspondentes obrigatório
- Comparação textual (diff tradicional)
- Comparação semântica com LLM (via Agno)
- Comparação de tabelas numéricas

**PREMISSAS ESTABELECIDAS:**
- Seções podem ser alinhadas por título/número
- Diferenças semânticas detectáveis por prompt engineering
- Tolerância numérica para comparação de tabelas (a definir)

**DADOS FALTANTES:**
- Critérios de "equivalência semântica" (threshold de similaridade)
- Tratamento de seções renumeradas/reorganizadas
- Algoritmo de alinhamento (Needleman-Wunsch, heurístico?)

---

### 2.9 Stage 9: Requisitos Funcionais — Saída de Dados

**FATOS CONFIRMADOS:**
- Saída: Visualização elaborada no notebook
- DataFrame pandas estruturado (desejável)
- Classificação de severidade: crítica/média/baixa (desejável)
- Exportação de arquivos externos: não prioritário (fora de escopo inicial)

**PREMISSAS ESTABELECIDAS:**
- Visualização via IPython display, matplotlib ou similar
- DataFrame com colunas: seção, tipo de diferença, severidade, conteúdo original, conteúdo modificado

**DADOS FALTANTES:**
- Formato exato da visualização esperada
- Critérios para classificação de severidade

---

### 2.10 Stage 10: Dados e Performance

**FATOS CONFIRMADOS:**
- 2 PDFs ASTM suficientes para validação (não precisa de dataset extenso)
- Persistência: tudo em memória (sem banco de dados)
- Histórico: não necessário
- Tempo de processamento: 2-3 minutos aceitável

**PREMISSAS ESTABELECIDAS:**
- Sem necessidade de cache entre execuções
- Cada execução do notebook é independente
- Performance não é fator crítico (PoC)

**DADOS FALTANTES:**
- Tempo máximo tolerável antes de considerar falha
- Uso de memória aceitável (limite antes de crash)

---

### 2.11 Stage 11: Tecnologia e Integrações

**FATOS CONFIRMADOS:**
- Aprender Agno durante a PoC (aberto a sugestões)
- LLM para comparação semântica
- Sem integrações com sistemas externos

**PREMISSAS ESTABELECIDAS:**
- Documentação do Agno suficiente para aprendizado em 3.5 semanas
- APIs de LLM padrão (OpenAI/Anthropic) facilmente integráveis
- Bibliotecas Python padrão para OCR/parsing

**DADOS FALTANTES:**
- Curva de aprendizado real do Agno
- Maturidade/estabilidade do framework Agno

---

### 2.12 Stage 12: Segurança e Compliance

**FATOS CONFIRMADOS:**
- PDFs: normas técnicas públicas (sem confidencialidade)
- LGPD: não aplicável (sem dados pessoais)
- Sem requisitos de segurança críticos

**PREMISSAS ESTABELECIDAS:**
- PDFs não contêm informações proprietárias sensíveis
- Execução local elimina riscos de exfiltração de dados
- APIs de LLM externas podem processar o conteúdo (sem restrições contratuais)

**DADOS FALTANTES:**
- Política de retenção de logs/outputs (se aplicável)
- Revisão legal de envio de normas técnicas para APIs externas

---

## 3. Catálogo Completo de Requisitos Funcionais

### 3.1 Módulo de Ingestão de PDFs

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-001** | O sistema deve aceitar como entrada 2 arquivos PDF via path absoluto no filesystem local | ESSENCIAL | Entrada |
| **RF-002** | O sistema deve validar que os PDFs não excedam 25MB cada | ESSENCIAL | Entrada |
| **RF-003** | O sistema deve emitir erro legível caso um PDF seja inválido ou corrompido | DESEJÁVEL | Entrada |
| **RF-004** | O sistema deve identificar automaticamente se o PDF é nativo (texto selecionável) ou escaneado (requer OCR) | ESSENCIAL | Entrada |

### 3.2 Módulo de Extração de Conteúdo

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-005** | O sistema deve extrair texto de PDFs nativos preservando estrutura de parágrafos | ESSENCIAL | Extração |
| **RF-006** | O sistema deve aplicar OCR em PDFs escaneados para extrair texto | DESEJÁVEL | Extração |
| **RF-007** | O sistema deve identificar e extrair tabelas numéricas de ambos os PDFs | DESEJÁVEL | Extração |
| **RF-008** | O sistema deve preservar hierarquia de seções (capítulos, subseções) durante extração | ESSENCIAL | Extração |
| **RF-009** | O sistema deve extrair metadados básicos dos PDFs (número de páginas, título se disponível) | DESEJÁVEL | Extração |

### 3.3 Módulo de Alinhamento de Seções

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-010** | O sistema deve identificar seções correspondentes entre os dois PDFs com base em títulos e numeração | ESSENCIAL | Alinhamento |
| **RF-011** | O sistema deve lidar com seções renomeadas mas semanticamente equivalentes | DESEJÁVEL | Alinhamento |
| **RF-012** | O sistema deve detectar seções adicionadas no PDF mais recente | ESSENCIAL | Alinhamento |
| **RF-013** | O sistema deve detectar seções removidas do PDF mais antigo | ESSENCIAL | Alinhamento |
| **RF-014** | O sistema deve gerar um mapeamento explícito entre seções alinhadas (seção A → seção B) | ESSENCIAL | Alinhamento |

### 3.4 Módulo de Comparação Textual

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-015** | O sistema deve comparar texto corrido de seções alinhadas usando algoritmo de diff textual | ESSENCIAL | Comparação |
| **RF-016** | O sistema deve identificar adições, remoções e modificações no texto | ESSENCIAL | Comparação |
| **RF-017** | O sistema deve ignorar diferenças triviais (espaços extras, quebras de linha) | DESEJÁVEL | Comparação |
| **RF-018** | O sistema deve destacar mudanças em termos técnicos ou valores numéricos com maior importância | DESEJÁVEL | Comparação |

### 3.5 Módulo de Comparação Semântica com LLM

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-019** | O sistema deve utilizar LLM (via framework Agno) para avaliar se diferenças textuais são semanticamente significativas | ESSENCIAL | Comparação Semântica |
| **RF-020** | O sistema deve classificar diferenças em: "equivalente semanticamente", "mudança menor", "mudança significativa" | DESEJÁVEL | Comparação Semântica |
| **RF-021** | O sistema deve fornecer justificativa textual da classificação semântica (output do LLM) | DESEJÁVEL | Comparação Semântica |
| **RF-022** | O sistema deve processar seções de até 4000 tokens por chamada de LLM | ESSENCIAL | Comparação Semântica |

### 3.6 Módulo de Comparação de Tabelas

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-023** | O sistema deve comparar tabelas numéricas célula por célula | DESEJÁVEL | Comparação Tabelas |
| **RF-024** | O sistema deve detectar mudanças em valores numéricos com tolerância configurável (ex: ±0.01) | DESEJÁVEL | Comparação Tabelas |
| **RF-025** | O sistema deve identificar linhas/colunas adicionadas ou removidas em tabelas | DESEJÁVEL | Comparação Tabelas |
| **RF-026** | O sistema deve destacar mudanças em headers de tabelas (nomes de colunas) | DESEJÁVEL | Comparação Tabelas |

### 3.7 Módulo de Classificação de Severidade

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-027** | O sistema deve classificar diferenças detectadas em 3 níveis: CRÍTICA, MÉDIA, BAIXA | DESEJÁVEL | Classificação |
| **RF-028** | Mudanças em valores numéricos de especificações devem ser classificadas como CRÍTICA por padrão | DESEJÁVEL | Classificação |
| **RF-029** | Mudanças em texto descritivo devem ser classificadas como MÉDIA ou BAIXA dependendo do contexto | DESEJÁVEL | Classificação |
| **RF-030** | O sistema deve permitir override manual da classificação (comentário no notebook) | DESEJÁVEL | Classificação |

### 3.8 Módulo de Visualização e Output

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-031** | O sistema deve gerar DataFrame pandas estruturado com todas as diferenças detectadas | DESEJÁVEL | Output |
| **RF-032** | O DataFrame deve conter colunas mínimas: ID, Seção, Tipo Diferença, Severidade, Conteúdo Original, Conteúdo Modificado | DESEJÁVEL | Output |
| **RF-033** | O sistema deve exibir visualização elaborada no notebook (tabelas formatadas, highlights) | ESSENCIAL | Output |
| **RF-034** | O sistema deve exibir estatísticas resumidas: total de diferenças, % críticas, % médias, % baixas | DESEJÁVEL | Output |
| **RF-035** | O sistema deve permitir filtragem interativa de diferenças por severidade no notebook | FORA DE ESCOPO | Output |
| **RF-036** | O sistema deve exportar resultados para CSV/Excel | FORA DE ESCOPO | Output |

### 3.9 Módulo de Pipeline End-to-End

| ID | Requisito | Prioridade | Categoria |
|----|-----------|------------|-----------|
| **RF-037** | O sistema deve executar pipeline completo (ingestão → extração → alinhamento → comparação → output) em células sequenciais do notebook | DESEJÁVEL | Pipeline |
| **RF-038** | O sistema deve permitir execução modular (testar cada etapa independentemente) | DESEJÁVEL | Pipeline |
| **RF-039** | O sistema deve exibir logs de progresso durante execução (ex: "Extraindo página 5/20...") | DESEJÁVEL | Pipeline |
| **RF-040** | O sistema deve capturar e exibir erros de forma legível em caso de falha em qualquer etapa | ESSENCIAL | Pipeline |

---

## 4. Requisitos Não-Funcionais (ISO/IEC 25010)

### 4.1 Performance (Eficiência de Performance)

| ID | Requisito | Métrica | Target | Prioridade |
|----|-----------|---------|--------|------------|
| **RNF-001** | Tempo de processamento end-to-end de 2 PDFs (até 25MB cada) | Tempo total | ≤ 3 minutos | ALTO |
| **RNF-002** | Uso de memória RAM durante processamento | RAM Peak | ≤ 4 GB | MÉDIO |
| **RNF-003** | Tempo de resposta de uma chamada LLM individual | Latência | ≤ 30 segundos | MÉDIO |
| **RNF-004** | Throughput de extração de texto | Páginas/segundo | ≥ 2 páginas/seg (PDFs nativos) | BAIXO |

### 4.2 Usabilidade

| ID | Requisito | Métrica | Target | Prioridade |
|----|-----------|---------|--------|------------|
| **RNF-005** | Clareza das mensagens de erro | % erros com mensagem legível | 100% | ALTO |
| **RNF-006** | Documentação inline no notebook (comentários, markdown) | Cobertura de células | ≥ 80% células documentadas | MÉDIO |
| **RNF-007** | Tempo para executar notebook completo pela primeira vez (cold start com instalação de dependências) | Tempo total | ≤ 10 minutos | MÉDIO |
| **RNF-008** | Facilidade de modificação de parâmetros (paths, thresholds) | Localização de configurações | Todas em célula única de configuração | ALTO |

### 4.3 Confiabilidade

| ID | Requisito | Métrica | Target | Prioridade |
|----|-----------|---------|--------|------------|
| **RNF-009** | Taxa de sucesso de extração em PDFs nativos bem formados | Success rate | ≥ 95% | ALTO |
| **RNF-010** | Taxa de sucesso de OCR em PDFs escaneados (qualidade boa/média) | Success rate | ≥ 70% | MÉDIO |
| **RNF-011** | Robustez a PDFs malformados (sem crash) | % tratamento de exceções | 100% | ALTO |
| **RNF-012** | Consistência de resultados em execuções repetidas (mesmo input) | Variação de resultados | ≤ 5% divergência | MÉDIO |

### 4.4 Manutenibilidade

| ID | Requisito | Métrica | Target | Prioridade |
|----|-----------|---------|--------|------------|
| **RNF-013** | Modularidade do código (funções reutilizáveis) | % código em funções | ≥ 70% | MÉDIO |
| **RNF-014** | Cobertura de comentários no código | % linhas comentadas | ≥ 20% | BAIXO |
| **RNF-015** | Uso de convenções Python (PEP 8) | Score pylint/flake8 | ≥ 7.0/10 | BAIXO |

### 4.5 Portabilidade

| ID | Requisito | Métrica | Target | Prioridade |
|----|-----------|---------|--------|------------|
| **RNF-016** | Compatibilidade com Python 3.8+ | Versões suportadas | Python 3.8, 3.9, 3.10, 3.11 | ALTO |
| **RNF-017** | Instalação de dependências via pip (sem compilação manual) | % dependências via pip | 100% | ALTO |
| **RNF-018** | Execução em ambiente Windows/Linux/Mac | SOs suportados | 3 SOs | MÉDIO |

### 4.6 Segurança

| ID | Requisito | Métrica | Target | Prioridade |
|----|-----------|---------|--------|------------|
| **RNF-019** | Não armazenar credenciais hardcoded no notebook | Ocorrências de secrets | 0 | ALTO |
| **RNF-020** | Uso de variáveis de ambiente para API keys de LLM | Método de configuração | 100% via env vars | ALTO |
| **RNF-021** | Validação de paths de entrada (evitar path traversal) | Validação implementada | Sim | MÉDIO |

---

## 5. Matriz de Riscos e Mitigação

### 5.1 Riscos Técnicos

| ID | Risco | Probabilidade | Impacto | Severidade | Mitigação |
|----|-------|---------------|---------|------------|-----------|
| **RT-001** | Curva de aprendizado do Agno maior que 3.5 semanas | ALTA | CRÍTICO | 🔴 ALTA | **Plano B:** substituir por LangChain ou direct API calls se bloqueio >1 semana |
| **RT-002** | OCR de baixa qualidade em PDFs escaneados | MÉDIA | ALTO | 🟡 MÉDIA | Testar múltiplas bibliotecas (Tesseract, EasyOCR); marcar OCR como "desejável" |
| **RT-003** | Alinhamento de seções falha em documentos muito diferentes | MÉDIA | ALTO | 🟡 MÉDIA | Implementar fallback heurístico simples; usar LLM para sugerir alinhamento |
| **RT-004** | APIs de LLM com latência alta (>1min) ou instáveis | BAIXA | MÉDIO | 🟢 BAIXA | Implementar retry logic; usar modelos locais menores como fallback |
| **RT-005** | Parsing de tabelas complexas falha (células mescladas, tabelas aninhadas) | ALTA | MÉDIO | 🟡 MÉDIA | Focar em tabelas simples grid; documentar limitações conhecidas |
| **RT-006** | Consumo de memória >8GB para PDFs grandes (25MB) | MÉDIA | MÉDIO | 🟡 MÉDIA | Implementar processamento por chunks/páginas; liberar memória explicitamente |

### 5.2 Riscos de Escopo

| ID | Risco | Probabilidade | Impacto | Severidade | Mitigação |
|----|-------|---------------|---------|------------|-----------|
| **RE-001** | Stakeholders solicitam features além do MVP durante PoC | ALTA | MÉDIO | 🟡 MÉDIA | Definir escopo fechado neste documento; escalar pedidos para "fase 2" |
| **RE-002** | PDFs ASTM não representam casos complexos suficientes | MÉDIA | BAIXO | 🟢 BAIXA | Testar com 1-2 PDFs adicionais se tempo permitir; documentar edge cases |
| **RE-003** | Expectativas de visualização "elaborada" não alinhadas | ALTA | MÉDIO | 🟡 MÉDIA | Criar mockup simples da visualização esperada na primeira semana |

### 5.3 Riscos de Recursos

| ID | Risco | Probabilidade | Impacto | Severidade | Mitigação |
|----|-------|---------------|---------|------------|-----------|
| **RR-001** | Desenvolvedor com impedimentos (férias, doença) durante PoC | BAIXA | CRÍTICO | 🟡 MÉDIA | Buffer de 0.5 semana já incluído no prazo de 3.5 semanas |
| **RR-002** | Hardware local insuficiente (RAM, CPU) | BAIXA | ALTO | 🟡 MÉDIA | Benchmark inicial com PDFs; considerar cloud notebook (Colab/Kaggle) como fallback |
| **RR-003** | Orçamento de API de LLM excedido | MÉDIA | MÉDIO | 🟡 MÉDIA | Estimar custos antecipadamente; usar modelos mais baratos (GPT-3.5 vs GPT-4) |

### 5.4 Riscos de Qualidade

| ID | Risco | Probabilidade | Impacto | Severidade | Mitigação |
|----|-------|---------------|---------|------------|-----------|
| **RQ-001** | Taxa de falsos positivos/negativos na detecção de diferenças >20% | MÉDIA | ALTO | 🟡 MÉDIA | Validação manual de resultados; ajuste de thresholds; documentar limitações |
| **RQ-002** | Classificação de severidade inconsistente (subjetiva) | ALTA | BAIXO | 🟢 BAIXA | Definir regras simples baseadas em palavras-chave; permitir override manual |
| **RQ-003** | Output difícil de interpretar (muitos dados, pouca estrutura) | MÉDIA | MÉDIO | 🟡 MÉDIA | Iterar na visualização com feedback incremental; priorizar clareza sobre completude |

---

## 6. Matriz de Rastreabilidade

### 6.1 Requisitos Essenciais

| Req ID | Descrição Resumida | Stakeholder | Objetivo de Negócio | Critério de Aceitação |
|--------|-------------------|-------------|---------------------|----------------------|
| **RF-001** | Entrada de 2 PDFs via path local | Desenvolvedor | Validação Técnica | Notebook aceita paths e carrega PDFs sem erro |
| **RF-002** | Validação de tamanho ≤25MB | Desenvolvedor | Validação Técnica | PDFs >25MB rejeitados com mensagem clara |
| **RF-004** | Detecção automática PDF nativo vs escaneado | Desenvolvedor | Validação Técnica | Sistema escolhe extração nativa ou OCR automaticamente |
| **RF-005** | Extração de texto de PDFs nativos | Desenvolvedor | Validação Técnica | Texto extraído preserva parágrafos e estrutura |
| **RF-008** | Preservação de hierarquia de seções | Eng. Produto | Redução Esforço Manual | Seções numeradas/títulos identificados corretamente |
| **RF-010** | Alinhamento de seções correspondentes | Eng. Produto | Redução Esforço Manual | Seções equivalentes entre PDFs mapeadas corretamente |
| **RF-012** | Detecção de seções adicionadas | Eng. Produto | Redução Esforço Manual | Seções novas marcadas explicitamente no output |
| **RF-013** | Detecção de seções removidas | Eng. Produto | Redução Esforço Manual | Seções deletadas marcadas explicitamente no output |
| **RF-014** | Mapeamento explícito de seções | Eng. Produto | Decisão Go/No-Go | DataFrame ou visualização mostra alinhamento seção A → B |
| **RF-015** | Comparação textual (diff) | Eng. Produto | Validação Técnica | Adições/remoções/modificações identificadas corretamente |
| **RF-016** | Identificação de adições/remoções/modificações | Eng. Produto | Validação Técnica | Tipos de diferença categorizados (add/remove/modify) |
| **RF-019** | Comparação semântica com LLM (Agno) | Desenvolvedor | Aprendizado + Validação | Agno integrado e processando comparações semânticas |
| **RF-022** | Processamento de seções até 4000 tokens | Desenvolvedor | Validação Técnica | Seções longas não causam erro de limite de contexto |
| **RF-033** | Visualização elaborada no notebook | Eng. Produto | Decisão Go/No-Go | Output legível com highlights/formatação clara |
| **RF-040** | Captura de erros legíveis | Desenvolvedor | Validação Técnica | Falhas exibem mensagem clara em vez de stacktrace críptico |

### 6.2 Requisitos Desejáveis

| Req ID | Descrição Resumida | Stakeholder | Objetivo de Negócio | Critério de Aceitação |
|--------|-------------------|-------------|---------------------|----------------------|
| **RF-003** | Validação de PDFs inválidos | Desenvolvedor | Confiabilidade | PDFs corrompidos rejeitados sem crash |
| **RF-006** | OCR para PDFs escaneados | Eng. Produto | Redução Esforço Manual | Texto extraído de PDFs escaneados com ≥70% acurácia |
| **RF-007** | Extração de tabelas numéricas | Eng. Produto | Redução Esforço Manual | Tabelas convertidas para DataFrames parseáveis |
| **RF-009** | Extração de metadados | Desenvolvedor | Rastreabilidade | Metadados (páginas, título) exibidos no output |
| **RF-011** | Alinhamento de seções renomeadas | Eng. Produto | Redução Esforço Manual | Seções com títulos diferentes mas conteúdo similar alinhadas |
| **RF-017** | Ignorar diferenças triviais | Eng. Produto | Redução Ruído | Espaços/quebras de linha não contam como diferença |
| **RF-018** | Priorização de termos técnicos | Eng. Produto | Redução Esforço Manual | Mudanças em valores/termos destacadas com maior peso |
| **RF-020** | Classificação semântica (equivalente/menor/significativa) | Eng. Produto | Decisão Go/No-Go | LLM retorna classificação de 3 níveis para cada diferença |
| **RF-021** | Justificativa textual da classificação | Eng. Produto | Transparência | Output do LLM explicando razão da classificação exibido |
| **RF-023-026** | Comparação de tabelas célula por célula | Eng. Produto | Redução Esforço Manual | Mudanças em células numéricas detectadas com tolerância |
| **RF-027-030** | Classificação de severidade (crítica/média/baixa) | Eng. Produto | Priorização | Diferenças categorizadas em 3 níveis com regras claras |
| **RF-031-034** | DataFrame estruturado + estatísticas | Eng. Produto | Decisão Go/No-Go | DataFrame com colunas definidas + resumo quantitativo |
| **RF-037-039** | Pipeline end-to-end modular | Desenvolvedor | Manutenibilidade | Execução célula por célula ou completa com logs de progresso |

---

## 7. Critérios de Aceitação (Gherkin)

### 7.1 Funcionalidade: Carregamento de PDFs

```gherkin
Feature: Carregamento de PDFs Técnicos

  Scenario: Carregar 2 PDFs válidos com sucesso
    Given o desenvolvedor possui 2 arquivos PDF em "/path/to/astm_2015.pdf" e "/path/to/astm_2016.pdf"
    And ambos os PDFs têm tamanho ≤ 25MB
    When o notebook executa a célula de carregamento com os paths fornecidos
    Then os PDFs são carregados sem erro
    And o sistema exibe mensagem "PDFs carregados com sucesso: 2 arquivos"
    And o sistema exibe metadados básicos (número de páginas) de cada PDF

  Scenario: Rejeitar PDF maior que 25MB
    Given o desenvolvedor fornece path para PDF de 30MB
    When o notebook executa a célula de carregamento
    Then o sistema exibe erro "PDF excede 25MB: /path/to/large.pdf (30.5MB)"
    And a execução é interrompida sem tentar processar

  Scenario: Detecção automática de tipo de PDF
    Given o desenvolvedor carrega 1 PDF nativo e 1 PDF escaneado
    When o sistema analisa os PDFs
    Then o PDF nativo é marcado como "text_extractable: True"
    And o PDF escaneado é marcado como "requires_ocr: True"
    And o sistema exibe log "PDF 1: Nativo (extração direta) | PDF 2: Escaneado (OCR necessário)"
```

### 7.2 Funcionalidade: Extração de Texto

```gherkin
Feature: Extração de Conteúdo Textual

  Scenario: Extração de texto de PDF nativo
    Given um PDF nativo com 20 páginas e estrutura de seções numeradas
    When o sistema executa extração de texto
    Then o texto completo é extraído preservando parágrafos
    And as seções são identificadas por numeração (ex: "1. Introduction", "2.1 Scope")
    And o tempo de extração é ≤ 30 segundos
    And nenhuma página é pulada

  Scenario: Extração com OCR de PDF escaneado
    Given um PDF escaneado com 15 páginas de qualidade média
    When o sistema executa OCR via Tesseract ou similar
    Then o texto é extraído com ≥ 70% de acurácia
    And o sistema exibe log de progresso "OCR página 5/15..."
    And o tempo de extração é ≤ 2 minutos
    And erros de OCR são registrados mas não interrompem processamento

  Scenario: Extração de hierarquia de seções
    Given um PDF com estrutura "1. Capítulo → 1.1 Subseção → 1.1.1 Item"
    When o sistema extrai conteúdo
    Then a hierarquia é preservada em estrutura de dados (dict ou JSON)
    And cada nível hierárquico é identificável (nível 1, 2, 3)
    And o sistema pode navegar de parent para child e vice-versa
```

### 7.3 Funcionalidade: Alinhamento de Seções

```gherkin
Feature: Alinhamento de Seções Correspondentes

  Scenario: Alinhamento por numeração idêntica
    Given PDF_A tem seção "3.2 Chemical Composition" e PDF_B tem seção "3.2 Chemical Composition"
    When o sistema executa alinhamento
    Then as seções são alinhadas automaticamente como par correspondente
    And o mapeamento é registrado: "PDF_A[3.2] ↔ PDF_B[3.2]"

  Scenario: Alinhamento de seção renumerada
    Given PDF_A tem seção "4.1 Tensile Requirements" e PDF_B renumerou para "5.1 Tensile Requirements"
    When o sistema executa alinhamento (com suporte a matching por título)
    Then as seções são alinhadas por similaridade de título
    And o sistema exibe log "Alinhamento por título: 4.1 ↔ 5.1 (match: 100%)"

  Scenario: Detecção de seção adicionada
    Given PDF_B contém nova seção "6.3 Corrosion Resistance" não presente em PDF_A
    When o sistema executa alinhamento
    Then a seção é marcada como "ADICIONADA no PDF_B"
    And aparece no output com flag "status: added"

  Scenario: Detecção de seção removida
    Given PDF_A contém seção "7.2 Obsolete Process" que não existe em PDF_B
    When o sistema executa alinhamento
    Then a seção é marcada como "REMOVIDA no PDF_B"
    And aparece no output com flag "status: removed"
```

### 7.4 Funcionalidade: Comparação Textual

```gherkin
Feature: Comparação de Texto Corrido

  Scenario: Detecção de modificação simples
    Given seção alinhada "2.1 Scope" com textos:
      | PDF_A | "This standard covers carbon steel bars" |
      | PDF_B | "This standard covers carbon and alloy steel bars" |
    When o sistema executa diff textual
    Then a diferença é categorizada como "MODIFICAÇÃO"
    And o output destaca: "adição: 'and alloy'"
    And a posição exata da mudança é identificada (palavra 6)

  Scenario: Ignorar diferenças triviais
    Given seção com diferença apenas em espaçamento: "Test  method" vs "Test method"
    When o sistema executa comparação
    Then a diferença é ignorada (não aparece no output)
    And o log exibe "Diferenças triviais ignoradas: 1"

  Scenario: Priorização de valores numéricos
    Given seção com mudança "tensile strength ≥ 500 MPa" → "tensile strength ≥ 550 MPa"
    When o sistema detecta a diferença
    Then a mudança é marcada com tag "numeric_change: True"
    And aparece no topo da lista de diferenças (alta prioridade)
```

### 7.5 Funcionalidade: Comparação Semântica com LLM

```gherkin
Feature: Análise Semântica de Diferenças

  Scenario: Classificação de equivalência semântica
    Given seção com mudança "automobile" → "vehicle"
    When o LLM (via Agno) analisa a diferença
    Then a classificação retornada é "EQUIVALENTE_SEMÂNTICO"
    And a justificativa é "Ambos os termos referem-se ao mesmo conceito"
    And a diferença é marcada como "severidade: BAIXA"

  Scenario: Classificação de mudança significativa
    Given seção com mudança "mandatory testing" → "optional testing"
    When o LLM analisa a diferença
    Then a classificação retornada é "MUDANÇA_SIGNIFICATIVA"
    And a justificativa é "Alteração de requisito obrigatório para opcional"
    And a diferença é marcada como "severidade: CRÍTICA"

  Scenario: Processamento de seção longa (4000 tokens)
    Given uma seção com 3500 tokens de conteúdo técnico
    When o sistema envia para LLM via Agno
    Then a requisição é bem-sucedida (sem erro de limite de contexto)
    And o tempo de resposta é ≤ 30 segundos
    And a classificação semântica é retornada normalmente
```

### 7.6 Funcionalidade: Comparação de Tabelas

```gherkin
Feature: Comparação de Tabelas Numéricas

  Scenario: Detecção de mudança em valor numérico
    Given tabela "Chemical Composition" com célula:
      | PDF_A | Carbon: 0.40% |
      | PDF_B | Carbon: 0.42% |
    When o sistema compara as tabelas
    Then a diferença é detectada: "0.40 → 0.42"
    And a mudança é marcada como "severidade: CRÍTICA" (especificação técnica)
    And a localização é registrada: "Tabela 3, Linha 2, Coluna 'Carbon'"

  Scenario: Aplicar tolerância numérica
    Given tabela com mudança "5.00 mm" → "5.01 mm"
    And tolerância configurada como ±0.05
    When o sistema compara
    Then a diferença é ignorada (dentro da tolerância)
    And o log exibe "Diferença dentro da tolerância: 5.00 ≈ 5.01"

  Scenario: Detecção de coluna adicionada
    Given tabela em PDF_A com colunas [Grade, Carbon, Manganese]
    And tabela em PDF_B com colunas [Grade, Carbon, Manganese, Silicon]
    When o sistema compara
    Then a coluna "Silicon" é marcada como "ADICIONADA"
    And aparece no output com flag "column_status: added"
```

### 7.7 Funcionalidade: Output e Visualização

```gherkin
Feature: Geração de Output Estruturado

  Scenario: Geração de DataFrame com diferenças
    Given processamento completo de 2 PDFs com 12 diferenças detectadas
    When o sistema gera output
    Then um DataFrame pandas é criado com colunas:
      | ID | Seção | Tipo | Severidade | Original | Modificado | Justificativa |
    And o DataFrame contém 12 linhas (uma por diferença)
    And o DataFrame é exibido no notebook com formatação legível

  Scenario: Exibição de estatísticas resumidas
    Given processamento com 15 diferenças: 3 críticas, 7 médias, 5 baixas
    When o sistema gera visualização resumida
    Then o output exibe:
      """
      === RESUMO DE DIFERENÇAS ===
      Total: 15 diferenças detectadas
      Críticas: 3 (20%)
      Médias: 7 (47%)
      Baixas: 5 (33%)
      """
    And um gráfico de barras simples é exibido (opcional)

  Scenario: Visualização elaborada com highlights
    Given diferenças categorizadas e processadas
    When o sistema gera visualização final
    Then cada diferença é exibida com:
      - Header: [CRÍTICA] Seção 3.2 - Mudança em valor numérico
      - Conteúdo: Texto original vs modificado com highlight colorido
      - Rodapé: Justificativa do LLM (se aplicável)
    And a visualização usa formatação HTML/Markdown para clareza
```

### 7.8 Funcionalidade: Pipeline End-to-End

```gherkin
Feature: Execução de Pipeline Completo

  Scenario: Execução bem-sucedida end-to-end
    Given notebook com células configuradas e 2 PDFs válidos fornecidos
    When o desenvolvedor executa "Run All Cells"
    Then o pipeline completa todas as etapas:
      1. Carregamento (5s)
      2. Extração (30s)
      3. Alinhamento (15s)
      4. Comparação textual (20s)
      5. Comparação semântica LLM (60s)
      6. Comparação de tabelas (20s)
      7. Geração de output (10s)
    And o tempo total é ≤ 3 minutos
    And o DataFrame final e visualização são exibidos sem erro

  Scenario: Execução modular para debug
    Given o desenvolvedor quer testar apenas alinhamento de seções
    When executa apenas a célula "3. Alinhamento"
    Then a célula usa resultados salvos da etapa anterior (Extração)
    And o alinhamento é executado independentemente
    And o output da etapa é exibido para validação

  Scenario: Tratamento de erro em etapa intermediária
    Given erro de OCR na extração de PDF_B (página corrompida)
    When o pipeline tenta processar
    Then o erro é capturado na célula de Extração
    And a mensagem exibida é "ERRO na extração: Página 12 do PDF_B corrompida. OCR falhou."
    And as células seguintes não são executadas automaticamente
    And o desenvolvedor pode corrigir o PDF e re-executar
```

---

## 8. Análise de Gaps (O que ainda falta definir)

### 8.1 Gaps Técnicos

| ID | Gap Identificado | Impacto | Ação Recomendada | Responsável |
|----|------------------|---------|------------------|-------------|
| **GT-001** | Versão específica do framework Agno não definida | MÉDIO | Pesquisar versão estável mais recente na primeira semana; documentar no notebook | Desenvolvedor |
| **GT-002** | Modelo LLM exato (GPT-4, Claude, Llama?) não especificado | MÉDIO | Decisão baseada em custo vs performance; testar GPT-3.5 primeiro como baseline | Desenvolvedor |
| **GT-003** | Algoritmo de alinhamento de seções não detalhado | ALTO | Propor 2 abordagens: (1) matching por título+número, (2) LLM sugerir alinhamento | Desenvolvedor |
| **GT-004** | Threshold de similaridade semântica não definido | BAIXO | Experimentar valores 0.7, 0.8, 0.9 e validar manualmente | Desenvolvedor |
| **GT-005** | Tolerância numérica para comparação de tabelas não especificada | BAIXO | Usar ±0.01 como padrão; tornar configurável via parâmetro | Desenvolvedor |
| **GT-006** | Formato exato da visualização "elaborada" não mockado | MÉDIO | Criar mockup simples na primeira semana e validar com Eng. Produto | Desenvolvedor |

### 8.2 Gaps de Requisitos

| ID | Gap Identificado | Impacto | Ação Recomendada | Responsável |
|----|------------------|---------|------------------|-------------|
| **GR-001** | Critérios específicos da Eng. Produto para aprovação final não documentados | ALTO | Agendar sessão de alinhamento na semana 1; documentar critérios | Eng. Produto |
| **GR-002** | Regras explícitas para classificação de severidade (crítica/média/baixa) não definidas | MÉDIO | Definir heurística baseada em palavras-chave (ex: "mandatory" = crítica) | Desenvolvedor + Eng. Produto |
| **GR-003** | Formato de apresentação final (slides, demo ao vivo, relatório?) não especificado | BAIXO | Assumir demo ao vivo do notebook + slides curtos de conclusão | Desenvolvedor |

### 8.3 Gaps de Ambiente

| ID | Gap Identificado | Impacto | Ação Recomendada | Responsável |
|----|------------------|---------|------------------|-------------|
| **GA-001** | Especificações de hardware da máquina local não conhecidas | MÉDIO | Documentar specs no README; testar benchmark inicial | Desenvolvedor |
| **GA-002** | Acesso/restrições de rede para APIs externas (LLM) não validado | ALTO | Testar conexão com OpenAI/Anthropic API na primeira semana | Desenvolvedor |
| **GA-003** | Orçamento para uso de APIs de LLM não definido | MÉDIO | Estimar custos baseado em 10 execuções completas; solicitar budget se necessário | Desenvolvedor |

### 8.4 Gaps de Dados

| ID | Gap Identificado | Impacto | Ação Recomendada | Responsável |
|----|------------------|---------|------------------|-------------|
| **GD-001** | Acesso aos PDFs ASTM 2015 e 2016 não confirmado | CRÍTICO | Baixar ou solicitar acesso aos PDFs na primeira semana | Desenvolvedor |
| **GD-002** | Ground truth de diferenças esperadas entre ASTM 2015/2016 não disponível | MÉDIO | Gerar manualmente lista de 5-10 diferenças conhecidas para validação | Eng. Produto |
| **GD-003** | PDFs adicionais para testes (além de ASTM) não identificados | BAIXO | Opcional: buscar 1-2 PDFs similares de normas públicas para testes extras | Desenvolvedor |

---

## 9. Pacote de Handoff para architect-specialist

### 9.1 Visão Geral de Arquitetura

**Tipo de Artefato:** Jupyter Notebook executável
**Padrão Arquitetural:** Pipeline linear modular (ETL-like)
**Ambiente de Execução:** Local (Python 3.8+ em laptop/desktop)

### 9.2 Requisitos Não-Funcionais Prioritários

| Categoria | Requisito | Target | Justificativa |
|-----------|-----------|--------|---------------|
| **Performance** | Tempo end-to-end ≤ 3 min | HARD LIMIT | Experiência de uso aceitável para PoC |
| **Performance** | Uso de RAM ≤ 4 GB | SOFT LIMIT | Compatibilidade com hardware médio |
| **Confiabilidade** | Taxa de sucesso extração ≥ 95% | HARD LIMIT | Qualidade mínima para validação |
| **Usabilidade** | Todas configurações em célula única | HARD LIMIT | Facilitar ajustes rápidos sem buscar no código |
| **Portabilidade** | 100% dependências via pip | HARD LIMIT | Instalação sem compilação manual |
| **Segurança** | API keys via variáveis de ambiente | HARD LIMIT | Evitar hardcoding de credenciais |

### 9.3 Restrições Técnicas

| Tipo | Restrição | Rationale |
|------|-----------|-----------|
| **Linguagem** | Python 3.8+ (sem TypeScript, Java, etc.) | Compatibilidade com ecossistema de bibliotecas NLP/ML |
| **Framework** | Agno para orchestração de LLM | Objetivo de aprendizado da PoC |
| **Deploy** | Execução local (sem server, Docker, Kubernetes) | Simplificação para PoC |
| **Banco de Dados** | Sem persistência (tudo em memória) | Redução de complexidade |
| **Interface** | Jupyter Notebook (sem web framework) | Foco em validação técnica, não UX |

### 9.4 Stack Tecnológica Recomendada

```python
# Core
python = "^3.8"
jupyter = "^1.0.0"
pandas = "^2.0.0"
numpy = "^1.24.0"

# PDF Processing
pymupdf = "^1.23.0"  # ou pdfplumber = "^0.10.0"
pytesseract = "^0.3.10"  # OCR
pillow = "^10.0.0"  # Manipulação de imagens para OCR

# NLP e LLM
agno = "^0.x.x"  # Verificar versão estável
openai = "^1.0.0"  # ou anthropic = "^0.8.0"
langchain = "^0.1.0"  # Opcional, fallback se Agno bloquear

# Text Processing
python-Levenshtein = "^0.20.0"  # Similaridade de strings
difflib = "built-in"  # Diff textual
rapidfuzz = "^3.0.0"  # Fuzzy matching rápido

# Visualização
matplotlib = "^3.7.0"
seaborn = "^0.12.0"  # Opcional, para gráficos mais bonitos
tabulate = "^0.9.0"  # Formatação de tabelas

# Utilidades
python-dotenv = "^1.0.0"  # Gerenciamento de env vars
tqdm = "^4.65.0"  # Progress bars
```

### 9.5 Estrutura de Módulos Recomendada

```
fastcheckai_poc/
│
├── notebooks/
│   └── main_pipeline.ipynb          # Notebook principal
│
├── src/
│   ├── __init__.py
│   ├── config.py                    # Configurações centralizadas
│   ├── pdf_loader.py                # RF-001 a RF-004
│   ├── text_extractor.py            # RF-005, RF-006, RF-008
│   ├── table_extractor.py           # RF-007
│   ├── section_aligner.py           # RF-010 a RF-014
│   ├── text_comparator.py           # RF-015 a RF-018
│   ├── semantic_comparator.py       # RF-019 a RF-022 (Agno + LLM)
│   ├── table_comparator.py          # RF-023 a RF-026
│   ├── severity_classifier.py       # RF-027 a RF-030
│   ├── output_generator.py          # RF-031 a RF-034
│   └── utils.py                     # Funções auxiliares
│
├── tests/
│   └── test_basic.py                # Testes unitários simples (opcional)
│
├── data/
│   ├── inputs/
│   │   ├── astm_2015.pdf
│   │   └── astm_2016.pdf
│   └── outputs/                     # Resultados temporários (opcional)
│
├── .env.example                     # Template de variáveis de ambiente
├── requirements.txt                 # Dependências Python
└── README.md                        # Instruções de setup
```

### 9.6 Integrações Externas

| Sistema/API | Propósito | Criticidade | Configuração |
|-------------|-----------|-------------|--------------|
| **OpenAI API** (ou Anthropic) | Comparação semântica via LLM | CRÍTICA | API key via `OPENAI_API_KEY` env var |
| **Tesseract OCR** | OCR de PDFs escaneados | MÉDIA | Instalação local via apt/brew + `pytesseract` |
| **Agno Framework** | Orchestração de workflows com LLM | ALTA | Instalação via pip; configuração conforme docs |

### 9.7 Considerações de Performance

**Bottlenecks Esperados:**
1. **OCR de PDFs escaneados:** 2-5s por página → usar processamento paralelo se possível
2. **Chamadas LLM:** 10-30s por seção → limitar contexto, usar batching se API suportar
3. **Parsing de tabelas complexas:** heurísticas podem falhar → priorizar tabelas simples

**Otimizações Recomendadas:**
- Implementar cache de embeddings de texto (se usar embeddings para alinhamento)
- Processar páginas de PDF em paralelo (multiprocessing)
- Limitar profundidade de análise semântica (ex: apenas diferenças >10 palavras)

### 9.8 Tratamento de Erros e Logging

**Estratégia de Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('fastcheckai')
```

**Erros Críticos (interrompem pipeline):**
- PDF corrompido/ilegível
- API key de LLM inválida
- Limite de contexto LLM excedido sem fallback

**Erros Recuperáveis (logam mas continuam):**
- Falha de OCR em 1 página (pula e continua)
- Timeout em 1 chamada LLM (usa fallback ou marca como "não classificado")
- Tabela não parseável (registra e pula)

### 9.9 Decisões Arquiteturais Pendentes

| Decisão | Opções | Recomendação | Critério |
|---------|--------|--------------|----------|
| **Biblioteca de PDF** | PyMuPDF vs pdfplumber | **pdfplumber** | Melhor suporte a tabelas |
| **Modelo LLM** | GPT-4 vs GPT-3.5 vs Claude | **GPT-3.5 Turbo** | Custo vs performance (PoC) |
| **Estratégia de alinhamento** | Heurística vs LLM-based | **Híbrido** | Heurística primeiro, LLM se falhar |
| **Formato de output** | JSON vs DataFrame vs HTML | **DataFrame + HTML** | Flexibilidade + visualização |

---

## 10. Pacote de Handoff para product-manager

### 10.1 Requisitos Funcionais Resumidos

**ESSENCIAIS (Devem estar funcionando para considerar PoC bem-sucedida):**

1. **Ingestão de PDFs**
   - Carregar 2 PDFs via path local
   - Validar tamanho ≤ 25MB
   - Detectar automaticamente se PDF é nativo ou escaneado

2. **Extração de Conteúdo**
   - Extrair texto de PDFs nativos preservando estrutura
   - Identificar hierarquia de seções (capítulos, subseções)

3. **Alinhamento de Seções**
   - Mapear seções correspondentes entre os 2 PDFs
   - Detectar seções adicionadas/removidas

4. **Comparação Textual**
   - Identificar adições, remoções e modificações no texto
   - Gerar diff textual linha por linha

5. **Comparação Semântica**
   - Usar LLM (via Agno) para avaliar significância semântica das diferenças
   - Classificar diferenças em níveis (equivalente/menor/significativa)

6. **Output Estruturado**
   - Exibir visualização elaborada no notebook
   - Mostrar todas diferenças detectadas de forma legível

**DESEJÁVEIS (Agregam valor mas não são bloqueantes):**

7. **OCR para PDFs Escaneados**
   - Extrair texto de PDFs digitalizados via OCR

8. **Comparação de Tabelas**
   - Detectar mudanças em tabelas numéricas célula por célula

9. **Classificação de Severidade**
   - Categorizar diferenças em CRÍTICA/MÉDIA/BAIXA

10. **Pipeline Modular**
    - Permitir execução célula por célula para debug
    - Logs de progresso em cada etapa

### 10.2 User Stories Priorizadas

#### Epic 1: Preparação de Dados

**US-001:** Como desenvolvedor, eu quero carregar 2 PDFs técnicos via path local, para que eu possa iniciar o processo de comparação.
- **Critério de Aceitação:** Notebook aceita 2 paths, valida tamanho, exibe confirmação de carregamento.
- **Prioridade:** P0 (Essential)

**US-002:** Como desenvolvedor, eu quero que o sistema identifique automaticamente se um PDF é nativo ou escaneado, para que a estratégia de extração correta seja aplicada.
- **Critério de Aceitação:** Sistema detecta tipo e exibe log "PDF 1: Nativo | PDF 2: Escaneado".
- **Prioridade:** P0 (Essential)

#### Epic 2: Extração de Conteúdo

**US-003:** Como desenvolvedor, eu quero extrair texto de PDFs nativos preservando estrutura de seções, para que o alinhamento seja facilitado.
- **Critério de Aceitação:** Texto extraído mantém numeração de seções (ex: "1.1 Scope").
- **Prioridade:** P0 (Essential)

**US-004:** Como engenheiro de produto, eu quero que PDFs escaneados tenham texto extraído via OCR, para que eu possa comparar documentos digitalizados.
- **Critério de Aceitação:** OCR processa PDF escaneado com ≥70% acurácia.
- **Prioridade:** P1 (Desirable)

**US-005:** Como desenvolvedor, eu quero extrair tabelas numéricas de ambos os PDFs, para que eu possa comparar dados tabulares.
- **Critério de Aceitação:** Tabelas convertidas para DataFrames pandas com headers corretos.
- **Prioridade:** P1 (Desirable)

#### Epic 3: Alinhamento e Comparação

**US-006:** Como engenheiro de produto, eu quero que seções correspondentes entre 2 versões de um documento sejam alinhadas automaticamente, para que eu não precise mapear manualmente.
- **Critério de Aceitação:** Seções com mesma numeração/título alinhadas; mapeamento exibido.
- **Prioridade:** P0 (Essential)

**US-007:** Como engenheiro de produto, eu quero detectar seções que foram adicionadas na versão mais recente, para que eu saiba o que é novo.
- **Critério de Aceitação:** Seções novas marcadas como "ADICIONADA" no output.
- **Prioridade:** P0 (Essential)

**US-008:** Como engenheiro de produto, eu quero comparar texto de seções alinhadas e ver adições/remoções/modificações, para que eu identifique mudanças exatas.
- **Critério de Aceitação:** Diff textual exibido com highlights (verde=adição, vermelho=remoção).
- **Prioridade:** P0 (Essential)

**US-009:** Como engenheiro de produto, eu quero que um LLM avalie se diferenças textuais são semanticamente significativas, para que eu foque apenas em mudanças importantes.
- **Critério de Aceitação:** LLM classifica diferenças e fornece justificativa textual.
- **Prioridade:** P0 (Essential)

**US-010:** Como engenheiro de produto, eu quero comparar tabelas numéricas e detectar mudanças em valores, para que eu identifique alterações em especificações técnicas.
- **Critério de Aceitação:** Mudanças em células numéricas detectadas e exibidas com localização.
- **Prioridade:** P1 (Desirable)

#### Epic 4: Visualização e Relatório

**US-011:** Como engenheiro de produto, eu quero ver todas as diferenças detectadas em formato estruturado e legível no notebook, para que eu possa revisar rapidamente.
- **Critério de Aceitação:** DataFrame com colunas [ID, Seção, Tipo, Severidade, Original, Modificado] exibido.
- **Prioridade:** P0 (Essential)

**US-012:** Como engenheiro de produto, eu quero que diferenças sejam classificadas por severidade (crítica/média/baixa), para que eu priorize revisão de mudanças importantes.
- **Critério de Aceitação:** Severidade atribuída automaticamente com base em regras; exibida no output.
- **Prioridade:** P1 (Desirable)

**US-013:** Como desenvolvedor, eu quero ver estatísticas resumidas (total, % críticas, etc.), para que eu tenha visão geral rápida dos resultados.
- **Critério de Aceitação:** Resumo exibido no notebook: "15 diferenças (3 críticas, 7 médias, 5 baixas)".
- **Prioridade:** P1 (Desirable)

#### Epic 5: Experiência de Desenvolvimento

**US-014:** Como desenvolvedor, eu quero executar o pipeline completo em até 3 minutos, para que a PoC seja viável em demonstrações.
- **Critério de Aceitação:** Execução "Run All Cells" completa em ≤ 3 minutos para PDFs de 25MB.
- **Prioridade:** P0 (Essential)

**US-015:** Como desenvolvedor, eu quero executar células individualmente para debug, para que eu possa testar cada etapa isoladamente.
- **Critério de Aceitação:** Cada célula funciona independentemente usando outputs salvos da anterior.
- **Prioridade:** P1 (Desirable)

**US-016:** Como desenvolvedor, eu quero logs de progresso em cada etapa, para que eu saiba o status durante execução longa.
- **Critério de Aceitação:** Logs exibidos: "Extraindo página 5/20...", "Processando seção 3/12...".
- **Prioridade:** P1 (Desirable)

### 10.3 Critérios de Sucesso da PoC

| Critério | Métrica | Target | Método de Medição |
|----------|---------|--------|-------------------|
| **Viabilidade Técnica** | Pipeline end-to-end funcional | 100% | Execução completa sem erros críticos |
| **Aprendizado Agno** | Desenvolvedor domina framework | Subjetivo | Autoavaliação: capaz de modificar prompts e workflows |
| **Qualidade de Detecção** | Taxa de detecção de diferenças conhecidas | ≥ 90% | Comparação com ground truth manual (5-10 diferenças conhecidas) |
| **Performance** | Tempo de processamento | ≤ 3 min | Medição via `%%time` no notebook |
| **Usabilidade** | Clareza do output | Qualitativo | Feedback da Eng. Produto: "output é compreensível sem explicação adicional" |
| **Decisão Go/No-Go** | Viabilidade de evolução para MVP | Sim/Não | Decisão conjunta desenvolvedor + Eng. Produto |

### 10.4 Roadmap de Entrega (3.5 Semanas)

#### Semana 1: Setup + Extração
- **Dias 1-2:** Setup do ambiente (instalação Agno, bibliotecas, PDFs)
- **Dias 3-5:** Implementar ingestão de PDFs + extração de texto nativo (RF-001 a RF-005)
- **Entregável:** Notebook com células funcionais para carregar e extrair texto de 2 PDFs
- **Checkpoint:** Demo rápida para validar extração

#### Semana 2: Alinhamento + Comparação Textual
- **Dias 6-8:** Implementar alinhamento de seções (RF-010 a RF-014)
- **Dias 9-10:** Implementar comparação textual com diff (RF-015 a RF-018)
- **Entregável:** Notebook com diff textual de seções alinhadas funcionando
- **Checkpoint:** Validar alinhamento com ASTM 2015/2016

#### Semana 3: LLM + Visualização
- **Dias 11-13:** Integrar Agno e LLM para comparação semântica (RF-019 a RF-022)
- **Dias 14-15:** Implementar output estruturado e visualização (RF-031 a RF-034)
- **Entregável:** Pipeline end-to-end funcional com output legível
- **Checkpoint:** Teste completo com ASTM 2015/2016

#### Semana 3.5: Refinamento + Apresentação
- **Dias 16-17:** Adicionar features desejáveis prioritárias (OCR, classificação severidade)
- **Dia 18:** Documentação do notebook (markdown explicativo) + preparação de apresentação
- **Dia 19:** Apresentação final para Eng. Produto + decisão go/no-go
- **Entregável:** Notebook finalizado + slides de conclusão

### 10.5 Riscos para o Product Manager

| Risco | Impacto no Negócio | Probabilidade | Mitigação |
|-------|-------------------|---------------|-----------|
| **Agno tem curva de aprendizado íngreme** | Atraso na entrega ou decisão no-go | ALTA | Plano B: usar LangChain ou APIs diretas se bloqueio >1 semana |
| **Qualidade de OCR baixa** | PoC não valida uso com PDFs escaneados | MÉDIA | Marcar OCR como "desejável"; focar em PDFs nativos para validação core |
| **Alinhamento de seções falha** | Comparação manual necessária (não escala) | MÉDIA | Implementar fallback heurístico + LLM para casos complexos |
| **Custo de LLM API alto** | Orçamento excedido | BAIXA | Estimar custos antecipadamente; usar modelos mais baratos (GPT-3.5) |
| **Stakeholders pedem features além do escopo** | Atraso ou escopo descontrolado | ALTA | Escopo fechado neste documento; escalar pedidos para "fase 2" |

### 10.6 Definição de Done (DoD)

**PoC considerada COMPLETA quando:**
- [ ] Pipeline end-to-end executa sem erros críticos
- [ ] Notebook está documentado (markdown + comentários)
- [ ] 2 PDFs ASTM processados com sucesso
- [ ] Output exibe diferenças de forma estruturada e legível
- [ ] Tempo de execução ≤ 3 minutos
- [ ] Framework Agno integrado e funcionando para comparação semântica
- [ ] Apresentação final realizada com Eng. Produto
- [ ] Decisão go/no-go documentada

**PoC considerada EXCELENTE quando (além do DoD acima):**
- [ ] OCR funciona com ≥70% acurácia
- [ ] Comparação de tabelas detecta mudanças numéricas
- [ ] Classificação de severidade implementada
- [ ] Pipeline modular (execução célula por célula)
- [ ] ≥90% das diferenças conhecidas detectadas corretamente

### 10.7 Próximos Passos Pós-PoC (se go)

**Se decisão for GO:**
1. **Fase MVP (6-8 semanas):**
   - Evoluir para Streamlit web app
   - Suportar processamento batch (múltiplos pares de PDFs)
   - Implementar exportação de relatórios (CSV, Excel, PDF)
   - Adicionar análise de figuras/diagramas (opcional)

2. **Fase Piloto (4-6 semanas):**
   - Testar com usuários reais da Eng. Produto
   - Iterar baseado em feedback
   - Implementar autenticação básica

3. **Fase Produção (8-12 semanas):**
   - Deploy em servidor interno (Docker + cloud)
   - Integração com CrewView (se aplicável)
   - Monitoramento e analytics

**Se decisão for NO-GO:**
- Documentar lições aprendidas
- Identificar blockers técnicos insolúveis
- Avaliar frameworks alternativos ou abordagem manual otimizada

---

## 11. Apêndices

### 11.1 Glossário de Termos

| Termo | Definição |
|-------|-----------|
| **Agno** | Framework para orchestração de workflows com LLMs (foco de aprendizado desta PoC) |
| **Alinhamento de Seções** | Processo de mapear seções correspondentes entre 2 versões de um documento |
| **Comparação Semântica** | Análise via LLM para determinar se diferenças textuais são significativas no contexto |
| **Diff Textual** | Algoritmo de comparação linha por linha (adições, remoções, modificações) |
| **OCR** | Optical Character Recognition — extração de texto de imagens/PDFs escaneados |
| **PDF Nativo** | PDF com texto selecionável (criado digitalmente, não escaneado) |
| **PDF Escaneado** | PDF gerado a partir de digitalização de documento físico (imagem rasterizada) |
| **Severidade** | Classificação de importância de uma diferença (crítica/média/baixa) |

### 11.2 Referências

- **ASTM A29/A29M:** Standard Specification for General Requirements for Steel Bars, Carbon and Alloy, Hot-Wrought
- **ISO/IEC 25010:** Systems and software Quality Requirements and Evaluation (SQuaRE)
- **Agno Documentation:** [URL a ser preenchido após pesquisa]
- **OpenAI API Docs:** https://platform.openai.com/docs
- **pdfplumber Documentation:** https://github.com/jsvine/pdfplumber
- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract

### 11.3 Aprovações

| Papel | Nome | Assinatura | Data |
|-------|------|------------|------|
| **Desenvolvedor** | [A preencher] | ____________ | ____/____/____ |
| **Eng. Produto** | [A preencher] | ____________ | ____/____/____ |
| **SIDI (Sponsor)** | [A preencher] | ____________ | ____/____/____ |

---

**FIM DA ESPECIFICAÇÃO COMPLETA DE REQUISITOS**

*Este documento deve ser considerado a baseline oficial para o desenvolvimento da PoC FastCheckAI.*