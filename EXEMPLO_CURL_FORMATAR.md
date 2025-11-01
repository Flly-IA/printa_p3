# Exemplos de Uso do Endpoint /cardapio/formatar

## Visão Geral

O endpoint `/cardapio/formatar` permite enviar o conteúdo do cardápio diretamente como texto JSON, sem precisar criar um arquivo `.txt`.

**URL**: `POST /cardapio/formatar`

**Parâmetros**:
- `id` (string, obrigatório): Identificador único do cardápio
- `text` (string, obrigatório): Conteúdo do cardápio em formato texto
- `font` (string, opcional): Nome da fonte (padrão: "Arial")
- `font_size` (float, opcional): Tamanho da fonte em pontos (padrão: 10.0)

---

## Exemplo 1: Requisição cURL (Windows)

```bash
curl -X POST "http://localhost:8000/cardapio/formatar" ^
  -H "Content-Type: application/json" ^
  -d "{\"id\":\"lula-bar-001\",\"text\":\"RELATÓRIO DE PREÇOS Lula Bar\n\n*Cervejas 600ml*\nBrahma Chopp (600ml) - R$ 11,00\nCorona (600ml) - R$ 17,00\nStella Artois (600ml) - R$ 14,00\",\"font\":\"Arial\",\"font_size\":10.0}"
```

## Exemplo 2: Requisição cURL (Linux/Mac)

```bash
curl -X POST "http://localhost:8000/cardapio/formatar" \
  -H "Content-Type: application/json" \
  -d '{"id":"lula-bar-001","text":"RELATÓRIO DE PREÇOS Lula Bar\n\n*Cervejas 600ml*\nBrahma Chopp (600ml) - R$ 11,00\nCorona (600ml) - R$ 17,00\nStella Artois (600ml) - R$ 14,00","font":"Arial","font_size":10.0}'
```

## Exemplo 3: PowerShell

```powershell
$body = @{
    id = "lula-bar-001"
    text = @"
RELATÓRIO DE PREÇOS Lula Bar

*Cervejas 600ml*
Brahma Chopp (600ml) - R$ 11,00
Corona (600ml) - R$ 17,00
Stella Artois (600ml) - R$ 14,00
Original (600ml) - R$ 13,00
Spaten (600ml) - R$ 13,00

*Cervejas Long Neck*
Corona (long Neck) - R$ 10,00
Stella Pure Gold (long Neck) - R$ 9,00
"@
    font = "Arial"
    font_size = 10.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/cardapio/formatar" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

## Exemplo 4: Python (usando requests)

```python
import requests

payload = {
    "id": "lula-bar-001",
    "text": """RELATÓRIO DE PREÇOS Lula Bar

*Cervejas 600ml*
Brahma Chopp (600ml) - R$ 11,00
Corona (600ml) - R$ 17,00
Stella Artois (600ml) - R$ 14,00
Original (600ml) - R$ 13,00
Spaten (600ml) - R$ 13,00

*Cervejas Long Neck*
Corona (long Neck) - R$ 10,00
Stella Pure Gold (long Neck) - R$ 9,00
""",
    "font": "Arial",
    "font_size": 10.0
}

response = requests.post(
    "http://localhost:8000/cardapio/formatar",
    json=payload
)

print(response.json())
```

## Exemplo 5: JavaScript (Fetch API)

```javascript
const payload = {
  id: "lula-bar-001",
  text: `RELATÓRIO DE PREÇOS Lula Bar

*Cervejas 600ml*
Brahma Chopp (600ml) - R$ 11,00
Corona (600ml) - R$ 17,00
Stella Artois (600ml) - R$ 14,00`,
  font: "Arial",
  font_size: 10.0
};

fetch("http://localhost:8000/cardapio/formatar", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Erro:", error));
```

---

## Resposta Esperada

```json
{
  "job_id": "lula-bar-001",
  "status": "pending",
  "message": "Processamento iniciado. Use /cardapio/status/{job_id} para acompanhar.",
  "status_url": "/cardapio/status/lula-bar-001"
}
```

---

## Verificar Status do Processamento

Após enviar a requisição, use o `job_id` retornado para verificar o status:

```bash
curl http://localhost:8000/cardapio/status/lula-bar-001
```

**Resposta quando completo (v4.2 - com Supabase)**:
```json
{
  "job_id": "lula-bar-001",
  "status": "completed",
  "message": "Cardápio processado com sucesso!",
  "files": {
    "cdr": "cardapio_lula-bar-001.cdr",
    "pdf": "cardapio.pdf",
    "json": "parsed.json",
    "csv": "auditoria.csv",
    "supabase_url": "https://weshxwjwrtsypnqyqkbz.supabase.co/storage/v1/object/public/corel/lula-bar-001.cdr"
  },
  "supabase_url": "https://weshxwjwrtsypnqyqkbz.supabase.co/storage/v1/object/public/corel/lula-bar-001.cdr",
  "created_at": "2025-10-31T10:30:00",
  "completed_at": "2025-10-31T10:30:15"
}
```

**Nota**: O campo `supabase_url` contém a URL pública do arquivo CDR armazenado no Supabase. Esta URL pode ser usada para download direto ou compartilhamento.

---

## Baixar Arquivos Gerados

Quando o status for `completed`, baixe os arquivos:

```bash
# CDR
curl -O http://localhost:8000/cardapio/download/lula-bar-001/cdr

# PDF
curl -O http://localhost:8000/cardapio/download/lula-bar-001/pdf

# JSON (dados parseados)
curl -O http://localhost:8000/cardapio/download/lula-bar-001/json

# CSV (auditoria)
curl -O http://localhost:8000/cardapio/download/lula-bar-001/csv
```

---

## Integração com n8n

### Nó HTTP Request

**Method**: POST
**URL**: `http://localhost:8000/cardapio/formatar`

**Body (JSON)**:
```json
{
  "id": "{{ $json.cardapio_id }}",
  "text": "{{ $json.conteudo_cardapio }}",
  "font": "Arial",
  "font_size": 10.0
}
```

**Headers**:
- `Content-Type`: `application/json`

### Monitorar Status (Loop)

1. Aguardar 2 segundos
2. Fazer GET para `/cardapio/status/{{ $json.job_id }}`
3. Verificar se `status === "completed"`
4. Se não, repetir

### Baixar Arquivos

Quando status for `completed`, fazer GET para:
- `/cardapio/download/{{ $json.job_id }}/pdf`
- `/cardapio/download/{{ $json.job_id }}/cdr`

---

## Formato do Texto Aceito

O texto deve seguir o formato usado pelo sistema:

```
RELATÓRIO DE PREÇOS [Nome do Restaurante]

*Categoria 1*
Item 1 (descrição) - R$ preço
Item 2 (descrição) - R$ preço

*Categoria 2*
Item 3 (descrição) - R$ preço
```

**Regras**:
- Primeira linha: Título com nome do restaurante
- Linha em branco após o título
- Categorias entre asteriscos: `*Nome da Categoria*`
- Itens: `Nome (descrição) - R$ preço`
- Linha em branco entre categorias

---

## Erros Comuns

### 400 - Bad Request
```json
{
  "detail": "O campo 'text' não pode estar vazio"
}
```
**Solução**: Verificar que o campo `text` não está vazio.

### 409 - Conflict
```json
{
  "detail": "Job com ID 'lula-bar-001' já está em processamento"
}
```
**Solução**: Usar um ID diferente ou aguardar o processamento anterior terminar.

### 404 - Not Found
```json
{
  "detail": "Job não encontrado"
}
```
**Solução**: Verificar se o `job_id` está correto.

---

## 🌐 Integração Supabase (v4.2)

### O Que Acontece Automaticamente

Quando você usa o endpoint `/cardapio/formatar`, o sistema:

1. **Gera o arquivo CDR** localmente
2. **Faz upload automático** para o bucket Supabase `corel`
3. **Obtém a URL pública** do arquivo
4. **Atualiza a tabela `Printa`** (coluna `link_arquivo_output`)
5. **Retorna a URL** no campo `supabase_url`

### Acessar o Arquivo no Supabase

A URL pública retornada pode ser usada para:
- Download direto do arquivo CDR
- Compartilhamento com terceiros
- Integração com outros sistemas

**Exemplo de URL**:
```
https://weshxwjwrtsypnqyqkbz.supabase.co/storage/v1/object/public/corel/lula-bar-001.cdr
```

### Verificar na Tabela Printa

Após o processamento, você pode verificar no Supabase:

```sql
SELECT id, link_arquivo_output
FROM Printa
WHERE id = 'lula-bar-001';
```

**Resultado**:
```
| id           | link_arquivo_output                                          |
|--------------|--------------------------------------------------------------|
| lula-bar-001 | https://weshxwjwrtsypnqyqkbz.supabase.co/storage/v1/object... |
```

---

## Teste Completo

Use o script Python fornecido para testar:

```bash
python exemplo_formatar.py
```

Este script irá:
1. Enviar o texto para formatação
2. Monitorar o status automaticamente
3. Mostrar os arquivos gerados
4. **Exibir a URL pública do Supabase**
5. Permitir baixar os arquivos
