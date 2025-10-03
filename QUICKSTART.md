# FastCheckAI - Guia Rápido de Uso

## 🚀 Teste Rápido da Pipeline

### Passo 1: Prepare seus PDFs

Coloque seus arquivos PDF na pasta `data/inputs/`:

```bash
cp /caminho/seu_pdf_antigo.pdf data/inputs/documento_v1.pdf
cp /caminho/seu_pdf_novo.pdf data/inputs/documento_v2.pdf
```

### Passo 2: Execute a comparação

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Comparação básica (relatório Markdown)
python scripts/compare_pdfs.py data/inputs/documento_v1.pdf data/inputs/documento_v2.pdf
```

### Passo 3: Visualize o relatório

```bash
# Ver relatório no terminal
cat data/outputs/comparison_report_*.md

# Ou abrir com editor
code data/outputs/comparison_report_*.md
```

---

## 📝 Exemplos de Uso

### Comparação Básica
```bash
python scripts/compare_pdfs.py data/inputs/doc_v1.pdf data/inputs/doc_v2.pdf
```

**Saída:**
- Relatório em `data/outputs/comparison_report_TIMESTAMP.md`
- Estatísticas no console
- Tempo de processamento

### Especificar Nome do Relatório
```bash
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --output relatorio_janeiro_2025.md
```

### Gerar Relatório HTML
```bash
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --format html
```

### Modo Rápido (sem LLM)
```bash
# Pula análise semântica - apenas diff textual
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --fast
```

### Desabilitar OCR (PDFs nativos)
```bash
# Mais rápido para PDFs que já têm texto extraível
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --no-ocr
```

### Usar Modelo Mais Barato
```bash
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --model gpt-4o-mini
```

### Customizar Diretório de Saída
```bash
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --output-dir ~/Documentos/relatorios
```

---

## 🎯 Casos de Uso Comuns

### Caso 1: PDFs Nativos (com texto)
```bash
# Máxima velocidade
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --no-ocr --fast
```

### Caso 2: PDFs Escaneados
```bash
# OCR habilitado + análise completa
python scripts/compare_pdfs.py scan1.pdf scan2.pdf
```

### Caso 3: Análise Detalhada
```bash
# Modelo GPT-4o + OCR + relatório HTML
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --format html --model gpt-4o
```

### Caso 4: Teste Rápido
```bash
# Sem OCR, sem LLM, só diff textual
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --no-ocr --fast
```

---

## 📊 Entendendo a Saída

### Console Output
```
🚀 Iniciando comparação de PDFs...
   PDF 1: documento_v1.pdf
   PDF 2: documento_v2.pdf
   Formato: markdown
   OCR: Habilitado
   Análise Semântica: Habilitada

============================================================
✅ COMPARAÇÃO CONCLUÍDA COM SUCESSO!
============================================================

📊 Estatísticas:
   Total de mudanças: 47
   Adições: 12
   Remoções: 8
   Modificações: 27

⚠️  Severidade:
   🔴 CRITICAL: 3
   🟡 MEDIUM: 15
   🟢 LOW: 29

⏱️  Tempo de processamento: 45.32s
📄 Relatório salvo em: data/outputs/comparison_report_20251003_110530.md
```

### Estrutura do Relatório Markdown

```markdown
# Relatório de Comparação de Documentos

## Sumário Executivo
- Total de mudanças: 47
- Mudanças críticas: 3
- Tempo de processamento: 45.32s

## Mudanças Críticas (Top 5)
1. Seção 4.2.1 - Requisito de temperatura alterado de 500°C para 550°C
2. Seção 7.1 - Termo "mandatory" removido de procedimento de teste
...

## Estatísticas Detalhadas
- Adições: 12
- Remoções: 8
- Modificações: 27

## Lista Completa de Mudanças
### Seção 1.1 - Escopo
**Tipo:** Modificação | **Severidade:** LOW
...
```

---

## ⚙️ Opções Avançadas

### Ver Ajuda Completa
```bash
python scripts/compare_pdfs.py --help
```

### Formatos de Saída Disponíveis

| Formato | Extensão | Melhor Para |
|---------|----------|-------------|
| `markdown` | `.md` | Leitura humana, versionamento Git |
| `html` | `.html` | Visualização no browser |
| `json` | `.json` | Integração com outras ferramentas |

### Modelos LLM Disponíveis

| Modelo | Velocidade | Qualidade | Custo |
|--------|-----------|-----------|-------|
| `gpt-4o` | Médio | Alta | ~$0.01/página |
| `gpt-4o-mini` | Rápido | Boa | ~$0.001/página |

---

## 🐛 Troubleshooting

### Erro: "API Key não encontrada"
```bash
# Verifique seu .env
cat .env | grep OPENAI_API_KEY

# Se vazio, adicione sua chave
echo "OPENAI_API_KEY=sk-sua-chave-aqui" >> .env
```

### Erro: "PDF corrompido"
```bash
# Tente sem OCR
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --no-ocr
```

### Comparação muito lenta
```bash
# Use modo rápido
python scripts/compare_pdfs.py doc1.pdf doc2.pdf --fast --no-ocr
```

### Texto extraído com caracteres estranhos
```bash
# Force OCR
python scripts/compare_pdfs.py doc1.pdf doc2.pdf
# OCR está habilitado por padrão
```

---

## 📚 Mais Informações

- **Debug detalhado:** Use `notebooks/pipeline.ipynb`
- **Exemplos de código:** Veja `examples/pipeline_usage.py`
- **Testes:** Execute `python scripts/test_pipeline_api.py`
- **Documentação completa:** Leia `README.md`

---

## ⏱️ Tempo Estimado de Processamento

| Cenário | Tempo Estimado |
|---------|----------------|
| 2 PDFs nativos (20 pgs) + sem LLM | ~30 segundos |
| 2 PDFs nativos (20 pgs) + com LLM | ~2-3 minutos |
| 2 PDFs escaneados (20 pgs) + OCR + LLM | ~5-8 minutos |

**Dica:** Use `--fast` e `--no-ocr` para testes rápidos, depois rode completo para análise final.
