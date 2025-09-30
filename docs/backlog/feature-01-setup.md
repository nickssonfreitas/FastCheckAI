# Feature 1: Setup e Configuração

**Prioridade:** P0 (Essential)
**Sprint:** Semana 1, Dia 1
**Estimativa:** 3 story points
**Dependências:** Nenhuma (primeira feature)

## Objetivo

Estabelecer ambiente de desenvolvimento funcional com todas as dependências instaladas, configurações centralizadas e validação de compatibilidade de bibliotecas, permitindo iniciar implementação do pipeline ETL sem bloqueios técnicos.

## User Stories

### US-001: Setup de Ambiente Python
**Como** desenvolvedor
**Eu quero** configurar ambiente Python 3.12 com uv e todas as dependências
**Para que** eu possa iniciar o desenvolvimento sem bloqueios de instalação

**Critérios de Aceite:**
- [ ] Python 3.12+ instalado e validado com `python --version`
- [ ] uv instalado e funcional com `uv --version`
- [ ] Virtual environment criado em `.venv/` com Python 3.12
- [ ] Todas as dependências do `pyproject.toml` instaladas sem erros de compilação
- [ ] Imports de bibliotecas críticas funcionando (PyMuPDF, pdfplumber, pandas, agno, openai)

**Definição de Pronto:**
- [ ] Código implementado (script `scripts/setup.sh` criado)
- [ ] Testes manuais executados (validação de imports em notebook teste)
- [ ] Documentado no notebook (célula de setup com instruções)

**Estimativa:** 2 story points

---

### US-002: Configuração de API Keys e Variáveis de Ambiente
**Como** desenvolvedor
**Eu quero** configurar API keys de forma segura via variáveis de ambiente
**Para que** eu possa acessar serviços LLM sem hardcoding de credenciais

**Critérios de Aceite:**
- [ ] Arquivo `.env.example` criado com template de variáveis necessárias
- [ ] Arquivo `.env` criado localmente (gitignored) com `OPENAI_API_KEY`
- [ ] Biblioteca `python-dotenv` configurada para carregar variáveis
- [ ] Teste de chamada OpenAI API bem-sucedido (hello world)
- [ ] Mensagem de erro clara se `OPENAI_API_KEY` não estiver configurada

**Definição de Pronto:**
- [ ] Código implementado em `src/config.py`
- [ ] Testes manuais executados (chamada API teste)
- [ ] Documentado no README.md e notebook

**Estimativa:** 1 story point

---

### US-003: Validação de Compatibilidade Agno Framework
**Como** desenvolvedor aprendendo Agno
**Eu quero** validar instalação do Agno com exemplo "Hello World"
**Para que** eu confirme viabilidade técnica do framework antes de implementar features complexas

**Critérios de Aceite:**
- [ ] Agno instalado sem erros (versão documentada em `pyproject.toml`)
- [ ] Agente simples criado com `Agent(model="gpt-4o")`
- [ ] Prompt de teste executado com resposta válida do LLM
- [ ] Tempo de resposta <10 segundos para hello world
- [ ] Logs de execução exibidos claramente no notebook

**Definição de Pronto:**
- [ ] Código implementado (célula notebook com Agno hello world)
- [ ] Testes manuais executados (agente responde corretamente)
- [ ] Documentado no notebook (markdown explicativo sobre Agno)

**Estimativa:** 2 story points

---

## Atividades Técnicas

### Atividade Macro 1: Instalação de Ambiente Base
**Subatividades:**
1. [ ] Instalar Python 3.12 usando pyenv ou sistema (arquivo: sistema operacional)
2. [ ] Instalar uv via curl ou pip (arquivo: `scripts/setup.sh`)
3. [ ] Criar `pyproject.toml` com dependências especificadas (arquivo: `pyproject.toml`)
4. [ ] Executar `uv venv --python 3.12` para criar virtual environment (arquivo: `.venv/`)
5. [ ] Ativar virtual environment e executar `uv pip install -e .` (teste manual)

### Atividade Macro 2: Configuração de Credenciais
**Subatividades:**
1. [ ] Criar arquivo `src/config.py` com carregamento de variáveis de ambiente (arquivo: `src/config.py`)
2. [ ] Criar `.env.example` com template de `OPENAI_API_KEY=your_key_here` (arquivo: `.env.example`)
3. [ ] Copiar `.env.example` para `.env` e adicionar API key real (arquivo: `.env` - local)
4. [ ] Validar carregamento com `python -c "from src.config import OPENAI_API_KEY; print('OK')"` (teste manual)

### Atividade Macro 3: Validação Agno Framework
**Subatividades:**
1. [ ] Criar célula notebook "0. Setup Agno" (arquivo: `notebooks/main_pipeline.ipynb`)
2. [ ] Importar e criar agente Agno com modelo GPT-4o (código Python)
3. [ ] Executar prompt "Explain what a technical standard is in one sentence" (teste manual)
4. [ ] Verificar resposta estruturada e tempo <10s (teste manual)
5. [ ] Documentar resultado e versão do Agno funcionando (markdown cell)

---

## Critérios de Testes

### Teste 1: Validação de Instalação de Dependências
**Entrada:** Terminal com Python 3.12 instalado
**Ação:** Executar `bash scripts/setup.sh` e depois `source .venv/bin/activate && python -c "import pymupdf, pdfplumber, pandas, agno, openai; print('All imports successful')"`
**Saída Esperada:** Mensagem "All imports successful" sem erros ou warnings

### Teste 2: Validação de API Key OpenAI
**Entrada:** Arquivo `.env` com `OPENAI_API_KEY=sk-...` válida
**Ação:** Executar célula notebook com código:
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response.choices[0].message.content)
```
**Saída Esperada:** Resposta do GPT-4o (ex: "Hello! How can I assist you today?") em <5 segundos

### Teste 3: Validação Agno Hello World
**Entrada:** Ambiente configurado com Agno instalado
**Ação:** Executar célula notebook:
```python
from agno import Agent
agent = Agent(model="gpt-4o", instructions="You are a helpful assistant.")
response = agent.run("What is 2+2?")
print(response)
```
**Saída Esperada:** Agente retorna resposta válida "4" ou explicação matemática em <10 segundos

---

## Riscos e Mitigações

- **Risco 1:** Agno incompatível com Python 3.12 → **Mitigação:** Testar instalação no Dia 1; downgrade para Python 3.11 se necessário (30 min)
- **Risco 2:** uv falha em compilar dependências C (PyMuPDF) → **Mitigação:** Usar pip tradicional como fallback; instalar wheels pré-compilados
- **Risco 3:** OpenAI API key inválida ou expirada → **Mitigação:** Validar key com curl antes de iniciar notebook; regenerar se necessário
- **Risco 4:** Agno Framework instável (bugs críticos) → **Mitigação:** Checkpoint Dia 1: se bugs >30% das tentativas, planejar uso direto de OpenAI SDK

---

## Métricas de Sucesso

- Tempo de setup completo: ≤10 minutos (cold start em máquina limpa)
- Taxa de sucesso de instalação: 100% em Linux (ambiente primário)
- Todas as bibliotecas essenciais importáveis: 5/5 (PyMuPDF, pdfplumber, pandas, agno, openai)
- Agno hello world funcional: Sim (resposta válida do LLM)
- Custo de validação: <$0.01 (apenas testes de API)
