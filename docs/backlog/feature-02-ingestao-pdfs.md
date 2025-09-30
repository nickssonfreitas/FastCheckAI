# Feature 2: Ingestão de PDFs

**Prioridade:** P0 (Essential)
**Sprint:** Semana 1, Dias 1-2
**Estimativa:** 5 story points
**Dependências:** Feature 1 (Setup e Configuração)

## Objetivo

Implementar módulo robusto de carregamento e validação de PDFs que aceite 2 arquivos via path local, valide tamanho (≤25MB), detecte tipo (nativo vs escaneado) e prepare objetos PDF para extração, garantindo tratamento de erros legível em caso de PDFs inválidos.

## User Stories

### US-004: Carregamento de PDFs via Path Local
**Como** desenvolvedor
**Eu quero** carregar 2 PDFs via caminho absoluto no filesystem
**Para que** eu possa iniciar pipeline de comparação com documentos técnicos ASTM

**Critérios de Aceite:**
- [ ] Função `load_pdf(path: str)` criada em `src/pdf_loader.py`
- [ ] Aceita paths absolutos e relativos (resolve automaticamente)
- [ ] Retorna objeto PDF estruturado (PyMuPDF Document)
- [ ] Exibe mensagem de confirmação "PDF carregado: [nome_arquivo] (X páginas)"
- [ ] Funciona com PDFs ASTM 2015 e 2016 reais

**Definição de Pronto:**
- [ ] Código implementado em `src/pdf_loader.py`
- [ ] Testes manuais executados com 2 PDFs válidos
- [ ] Documentado no notebook (célula "1. Carregamento de PDFs")

**Estimativa:** 2 story points

---

### US-005: Validação de Tamanho de PDF
**Como** desenvolvedor
**Eu quero** validar que PDFs não excedam 25MB antes de processar
**Para que** eu evite crashes de memória ou processamento excessivamente lento

**Critérios de Aceite:**
- [ ] Verificação de tamanho implementada antes de abrir PDF
- [ ] PDFs >25MB rejeitados com erro: "PDF excede 25MB: [path] ([tamanho]MB)"
- [ ] PDFs ≤25MB processados normalmente
- [ ] Tamanho calculado em MB com 1 casa decimal (ex: 24.3MB)
- [ ] Mensagem de log exibida: "Validando tamanho de PDF: [nome_arquivo]"

**Definição de Pronto:**
- [ ] Código implementado em `src/pdf_loader.py` (função `validate_pdf_size`)
- [ ] Testes manuais executados (PDF válido e PDF >25MB simulado)
- [ ] Documentado no notebook

**Estimativa:** 1 story point

---

### US-006: Detecção Automática de Tipo de PDF
**Como** desenvolvedor
**Eu quero** detectar automaticamente se PDF é nativo (texto selecionável) ou escaneado (requer OCR)
**Para que** a estratégia correta de extração seja aplicada sem configuração manual

**Critérios de Aceite:**
- [ ] Função `detect_pdf_type(pdf_doc)` implementada
- [ ] Retorna flag booleana `is_native: bool` e `requires_ocr: bool`
- [ ] Heurística: se página 1 tem <50 caracteres extraíveis, marca como escaneado
- [ ] Log exibido: "PDF [nome]: Nativo (extração direta)" ou "PDF [nome]: Escaneado (OCR necessário)"
- [ ] Testado com PDF nativo (ASTM digital) e PDF escaneado (simulado)

**Definição de Pronto:**
- [ ] Código implementado em `src/pdf_loader.py`
- [ ] Testes manuais executados (PDFs nativos e escaneados)
- [ ] Documentado no notebook

**Estimativa:** 2 story points

---

### US-007: Tratamento de Erros de PDF Inválido
**Como** desenvolvedor
**Eu quero** receber mensagens de erro claras quando PDF está corrompido ou ilegível
**Para que** eu possa corrigir problema sem interpretar stacktraces complexos

**Critérios de Aceite:**
- [ ] Try/except implementado em `load_pdf()` capturando exceções PyMuPDF
- [ ] Erro exibido: "ERRO ao carregar PDF: [path] está corrompido ou protegido por senha"
- [ ] Pipeline não crasheia (execução interrompida de forma controlada)
- [ ] Log de erro registrado com timestamp
- [ ] Testado com PDF corrompido (arquivo .pdf vazio ou binário inválido)

**Definição de Pronto:**
- [ ] Código implementado em `src/pdf_loader.py`
- [ ] Testes manuais executados (PDF corrompido simulado)
- [ ] Documentado no notebook

**Estimativa:** 1 story point

---

## Atividades Técnicas

### Atividade Macro 1: Implementação de Carregamento Básico
**Subatividades:**
1. [ ] Criar arquivo `src/pdf_loader.py` com imports (PyMuPDF, pathlib, logging) (arquivo: `src/pdf_loader.py`)
2. [ ] Implementar função `load_pdf(path: str) -> fitz.Document` (arquivo: `src/pdf_loader.py`)
3. [ ] Adicionar resolução de paths relativos com `Path(path).resolve()` (arquivo: `src/pdf_loader.py`)
4. [ ] Retornar objeto `fitz.open(path)` com validação (arquivo: `src/pdf_loader.py`)
5. [ ] Testar com PDFs ASTM em `data/inputs/` (teste manual)

### Atividade Macro 2: Validação de Tamanho
**Subatividades:**
1. [ ] Implementar `validate_pdf_size(path: str, max_mb: int = 25) -> bool` (arquivo: `src/pdf_loader.py`)
2. [ ] Calcular tamanho com `os.path.getsize(path) / (1024 * 1024)` (arquivo: `src/pdf_loader.py`)
3. [ ] Lançar `ValueError` se tamanho exceder limite (arquivo: `src/pdf_loader.py`)
4. [ ] Integrar validação no início de `load_pdf()` (arquivo: `src/pdf_loader.py`)
5. [ ] Testar com arquivo >25MB (criar PDF dummy ou arquivo binário) (teste manual)

### Atividade Macro 3: Detecção de Tipo de PDF
**Subatividades:**
1. [ ] Implementar `detect_pdf_type(pdf_doc: fitz.Document) -> dict` (arquivo: `src/pdf_loader.py`)
2. [ ] Extrair texto da página 1 com `pdf_doc[0].get_text()` (arquivo: `src/pdf_loader.py`)
3. [ ] Contar caracteres e aplicar threshold (50 chars) (arquivo: `src/pdf_loader.py`)
4. [ ] Retornar dict `{"is_native": bool, "requires_ocr": bool, "char_count": int}` (arquivo: `src/pdf_loader.py`)
5. [ ] Logar resultado da detecção (arquivo: `src/pdf_loader.py`)

### Atividade Macro 4: Tratamento de Erros
**Subatividades:**
1. [ ] Envolver `fitz.open()` em try/except capturando `RuntimeError` e `FileNotFoundError` (arquivo: `src/pdf_loader.py`)
2. [ ] Criar mensagens de erro customizadas por tipo de exceção (arquivo: `src/pdf_loader.py`)
3. [ ] Logar erro com `logging.error()` e timestamp (arquivo: `src/pdf_loader.py`)
4. [ ] Re-lançar exceção ou retornar `None` (decisão: re-lançar para debugging) (arquivo: `src/pdf_loader.py`)
5. [ ] Testar com PDF corrompido (criar arquivo .pdf com conteúdo binário inválido) (teste manual)

---

## Critérios de Testes

### Teste 1: Carregamento de PDFs Válidos
**Entrada:** Paths para `data/inputs/astm_2015.pdf` e `data/inputs/astm_2016.pdf`
**Ação:** Executar célula notebook:
```python
from src.pdf_loader import load_pdf
pdf_a = load_pdf("data/inputs/astm_2015.pdf")
pdf_b = load_pdf("data/inputs/astm_2016.pdf")
print(f"PDF A: {pdf_a.page_count} páginas")
print(f"PDF B: {pdf_b.page_count} páginas")
```
**Saída Esperada:** Mensagens de confirmação + contagem de páginas correta (ex: "PDF A: 20 páginas, PDF B: 22 páginas")

### Teste 2: Validação de Tamanho Excedido
**Entrada:** Path para arquivo PDF >25MB (criar arquivo dummy com `dd if=/dev/zero of=large.pdf bs=1M count=30`)
**Ação:** Executar `load_pdf("large.pdf")`
**Saída Esperada:** Exceção lançada com mensagem "PDF excede 25MB: large.pdf (30.0MB)" e execução interrompida

### Teste 3: Detecção de PDF Nativo vs Escaneado
**Entrada:** PDF nativo (ASTM 2015) e PDF escaneado simulado (imagem JPG convertida para PDF)
**Ação:** Executar:
```python
from src.pdf_loader import load_pdf, detect_pdf_type
pdf_native = load_pdf("data/inputs/astm_2015.pdf")
pdf_scanned = load_pdf("data/inputs/scanned_sample.pdf")
print(detect_pdf_type(pdf_native))
print(detect_pdf_type(pdf_scanned))
```
**Saída Esperada:**
- Nativo: `{"is_native": True, "requires_ocr": False, "char_count": 2500}`
- Escaneado: `{"is_native": False, "requires_ocr": True, "char_count": 15}`

### Teste 4: Tratamento de PDF Corrompido
**Entrada:** Arquivo corrompido (criar com `echo "invalid" > corrupted.pdf`)
**Ação:** Executar `load_pdf("corrupted.pdf")`
**Saída Esperada:** Mensagem de erro clara: "ERRO ao carregar PDF: corrupted.pdf está corrompido ou ilegível" sem stacktrace cru

---

## Riscos e Mitigações

- **Risco 1:** PyMuPDF falha ao abrir PDFs com proteção de senha → **Mitigação:** Adicionar detecção de PDFs criptografados e mensagem específica "PDF protegido por senha"
- **Risco 2:** Detecção de tipo falha em PDFs híbridos (parte texto, parte imagem) → **Mitigação:** Analisar 3 primeiras páginas em vez de apenas página 1; usar média de caracteres
- **Risco 3:** Paths com caracteres especiais ou espaços causam erro → **Mitigação:** Usar `Path().resolve()` que normaliza paths; adicionar testes com paths complexos
- **Risco 4:** PDFs ASTM reais não disponíveis no Dia 1 → **Mitigação:** Usar PDFs técnicos alternativos (ISO, IEEE) para desenvolvimento inicial; substituir quando ASTM disponíveis

---

## Métricas de Sucesso

- Taxa de sucesso de carregamento: 100% para PDFs válidos ≤25MB
- Detecção de tipo: ≥95% de acurácia (validado com 10 PDFs conhecidos: 5 nativos, 5 escaneados)
- Tempo de carregamento: <5 segundos para PDFs 25MB
- Mensagens de erro: 100% legíveis (sem stacktraces crus exibidos ao usuário)
- Validação de tamanho: 100% de rejeição para PDFs >25MB
