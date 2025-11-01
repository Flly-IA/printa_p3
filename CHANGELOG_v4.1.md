# Changelog - Versão 4.1

## 🚀 Novidades

### Novo Endpoint: `/cardapio/formatar` (POST)

Agora você pode enviar o conteúdo do cardápio diretamente via JSON, sem precisar criar um arquivo `.txt`!

**Antes (v4.0)**:
1. Criar arquivo `.txt`
2. Fazer upload via `/cardapio/gerar`

**Agora (v4.1)**:
1. Enviar texto direto via JSON para `/cardapio/formatar`

---

## 📝 Parâmetros do Novo Endpoint

```json
{
  "id": "identificador-unico",
  "text": "conteúdo do cardápio aqui",
  "font": "Arial",          // opcional, padrão: Arial
  "font_size": 10.0         // opcional, padrão: 10.0
}
```

### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | string | ✅ Sim | Identificador único do cardápio (será usado como job_id) |
| `text` | string | ✅ Sim | Conteúdo completo do cardápio em formato texto |
| `font` | string | ❌ Não | Fonte a ser usada (padrão: "Arial") |
| `font_size` | float | ❌ Não | Tamanho da fonte em pontos (padrão: 10.0) |

---

## 💡 Casos de Uso

### 1. Integração com n8n
Perfeito para automações onde o cardápio é gerado dinamicamente:
- Scraping de preços de fornecedores
- Geração automática a partir de banco de dados
- Integração com sistemas de gestão

### 2. APIs e Webhooks
Receber dados de outras APIs e gerar cardápios automaticamente.

### 3. Processamento em Lote
Processar múltiplos cardápios sem criar arquivos temporários.

---

## 🔄 Fluxo de Trabalho

```
1. POST /cardapio/formatar
   ├─ Recebe: { id, text, font?, font_size? }
   └─ Retorna: { job_id, status, status_url }

2. GET /cardapio/status/{job_id}
   ├─ Status: pending → processing → completed
   └─ Retorna: { status, files, ... }

3. GET /cardapio/download/{job_id}/{file_type}
   ├─ file_type: cdr, pdf, json, csv
   └─ Retorna: arquivo para download
```

---

## 📋 Exemplo Completo

### Enviar para Formatação

**Requisição**:
```bash
POST http://localhost:8000/cardapio/formatar
Content-Type: application/json

{
  "id": "lula-bar-001",
  "text": "RELATÓRIO DE PREÇOS Lula Bar\n\n*Cervejas 600ml*\nBrahma Chopp (600ml) - R$ 11,00\nCorona (600ml) - R$ 17,00",
  "font": "Arial",
  "font_size": 10.0
}
```

**Resposta**:
```json
{
  "job_id": "lula-bar-001",
  "status": "pending",
  "message": "Processamento iniciado. Use /cardapio/status/{job_id} para acompanhar.",
  "status_url": "/cardapio/status/lula-bar-001"
}
```

### Verificar Status

**Requisição**:
```bash
GET http://localhost:8000/cardapio/status/lula-bar-001
```

**Resposta (em processamento)**:
```json
{
  "job_id": "lula-bar-001",
  "status": "processing",
  "message": "Processamento iniciado",
  "files": null,
  "created_at": "2025-10-31T10:30:00",
  "completed_at": null
}
```

**Resposta (completo)**:
```json
{
  "job_id": "lula-bar-001",
  "status": "completed",
  "message": "Cardápio processado com sucesso!",
  "files": {
    "cdr": "cardapio_lula-bar-001.cdr",
    "pdf": "cardapio.pdf",
    "json": "parsed.json",
    "csv": "auditoria.csv"
  },
  "created_at": "2025-10-31T10:30:00",
  "completed_at": "2025-10-31T10:30:15"
}
```

### Baixar Arquivos

```bash
GET http://localhost:8000/cardapio/download/lula-bar-001/pdf
GET http://localhost:8000/cardapio/download/lula-bar-001/cdr
GET http://localhost:8000/cardapio/download/lula-bar-001/json
GET http://localhost:8000/cardapio/download/lula-bar-001/csv
```

---

## 🆚 Comparação: Endpoint Antigo vs Novo

| Aspecto | `/cardapio/gerar` (v4.0) | `/cardapio/formatar` (v4.1) |
|---------|------------------------|---------------------------|
| **Input** | Upload de arquivo `.txt` | JSON com texto direto |
| **job_id** | UUID gerado automaticamente | ID customizado pelo usuário |
| **Uso** | Upload manual | Integração automatizada |
| **Vantagem** | Simples para uso manual | Ideal para APIs/automação |

### Quando Usar Cada Um?

**Use `/cardapio/gerar`**:
- Quando tiver um arquivo `.txt` pronto
- Upload manual via interface/Postman
- Testes rápidos com arquivos existentes

**Use `/cardapio/formatar`**:
- Integrações com n8n, webhooks, APIs
- Quando o conteúdo é gerado dinamicamente
- Quando precisa controlar o `job_id`
- Processamento em lote

---

## 🔧 Melhorias Técnicas

### Código
- ✅ Novo modelo Pydantic `FormatRequest`
- ✅ Função `process_cardapio_from_text()` para processar texto direto
- ✅ Validação de ID duplicado (retorna 409 Conflict se em processamento)
- ✅ Permite reprocessar jobs completados

### Documentação
- ✅ Endpoint `/` atualizado com novo endpoint
- ✅ Arquivo `exemplo_formatar.py` para testes
- ✅ Arquivo `EXEMPLO_CURL_FORMATAR.md` com exemplos completos
- ✅ Este changelog para documentar mudanças

---

## 📦 Arquivos Novos/Modificados

### Modificados
- `api_cardapio.py` - Versão atualizada para 4.1

### Novos
- `exemplo_formatar.py` - Script Python para testar o novo endpoint
- `EXEMPLO_CURL_FORMATAR.md` - Documentação completa com exemplos
- `CHANGELOG_v4.1.md` - Este arquivo

---

## 🧪 Como Testar

### Método 1: Script Python
```bash
python exemplo_formatar.py
```

### Método 2: cURL (Windows)
```bash
curl -X POST "http://localhost:8000/cardapio/formatar" ^
  -H "Content-Type: application/json" ^
  -d "{\"id\":\"teste-001\",\"text\":\"RELATÓRIO DE PREÇOS Teste\n\n*Bebidas*\nCoca Cola - R$ 5,00\"}"
```

### Método 3: Postman / Insomnia
1. Método: POST
2. URL: `http://localhost:8000/cardapio/formatar`
3. Headers: `Content-Type: application/json`
4. Body (JSON):
```json
{
  "id": "teste-001",
  "text": "RELATÓRIO DE PREÇOS Teste\n\n*Bebidas*\nCoca Cola - R$ 5,00"
}
```

---

## 🐛 Correções de Bugs

Nenhuma correção de bugs nesta versão - apenas novos recursos.

---

## 📊 Compatibilidade

- ✅ Totalmente compatível com v4.0
- ✅ Todos os endpoints antigos continuam funcionando
- ✅ Nenhuma breaking change

---

## 🎯 Próximos Passos

Sugestões para v4.2:
- [ ] Webhook para notificar quando processamento completar
- [ ] Suporte a múltiplos cardápios em uma única requisição
- [ ] Cache de templates para melhor performance
- [ ] Fila de processamento com prioridade
- [ ] API de preview sem gerar arquivos

---

## 💬 Feedback

Encontrou algum problema ou tem sugestões? Abra uma issue!

**Data de Release**: 31 de Outubro de 2025
**Versão**: 4.1
