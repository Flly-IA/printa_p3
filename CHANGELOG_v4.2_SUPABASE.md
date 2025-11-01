# Changelog - Versão 4.2 - Integração Supabase

## 🚀 Novidade Principal: Integração Completa com Supabase

A versão 4.2 adiciona integração automática com Supabase para todos os arquivos CDR gerados pelo endpoint `/cardapio/formatar`.

---

## 🎯 O Que Mudou?

### ✅ Upload Automático para Supabase

Quando você usa o endpoint `/cardapio/formatar`, o sistema agora:

1. **Gera o arquivo CDR** normalmente
2. **Faz upload automático** para o bucket `corel` no Supabase
3. **Obtém a URL pública** do arquivo
4. **Atualiza a tabela `Printa`** com o link público na coluna `link_arquivo_output`
5. **Retorna a URL** no status do job

### 📊 Fluxo Completo

```
POST /cardapio/formatar
  ↓
Gerar CDR localmente
  ↓
Upload para Supabase bucket "corel"
  ↓
Obter URL pública
  ↓
UPDATE Printa SET link_arquivo_output = <url> WHERE id = <job_id>
  ↓
Retornar status com supabase_url
```

---

## 🔧 Configuração

### Credenciais Supabase

As credenciais estão configuradas diretamente no código:

```python
SUPABASE_URL = "https://weshxwjwrtsypnqyqkbz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_BUCKET = "corel"
```

### Tabela Printa

A tabela deve ter:
- **Coluna `id`**: VARCHAR/TEXT - chave primária (usado como job_id)
- **Coluna `link_arquivo_output`**: VARCHAR/TEXT - onde a URL pública será salva

---

## 📋 Exemplo de Uso

### 1. Enviar Requisição

```bash
POST http://localhost:8000/cardapio/formatar
Content-Type: application/json

{
  "id": "lula-bar-001",
  "text": "RELATÓRIO DE PREÇOS Lula Bar\n\n*Cervejas 600ml*\nBrahma Chopp (600ml) - R$ 11,00",
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

### 2. Verificar Status

```bash
GET http://localhost:8000/cardapio/status/lula-bar-001
```

**Resposta (quando concluído)**:
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

### 3. Acessar Arquivo no Supabase

A URL pública pode ser usada diretamente para:
- Download do arquivo
- Compartilhamento
- Integração com outros sistemas

```
https://weshxwjwrtsypnqyqkbz.supabase.co/storage/v1/object/public/corel/lula-bar-001.cdr
```

---

## 🔍 Logs Durante Processamento

Agora você verá logs adicionais:

```
[lula-bar-001] ✅ CDR exportado com sucesso
[lula-bar-001] 🚀 Iniciando integração com Supabase...
[lula-bar-001] 📤 Fazendo upload para Supabase bucket 'corel'...
[lula-bar-001] ✅ Upload concluído!
[lula-bar-001] 🔗 URL pública: https://...
[lula-bar-001] 📝 Atualizando tabela Printa...
[lula-bar-001] ✅ Tabela Printa atualizada com sucesso!
[lula-bar-001] ✅ Integração Supabase completa!
```

---

## 🆕 Novas Funções Adicionadas

### `upload_cdr_to_supabase(file_path, job_id)`

Faz upload do arquivo CDR para o bucket Supabase.

**Parâmetros**:
- `file_path` (Path): Caminho do arquivo CDR local
- `job_id` (str): ID do job (usado como nome do arquivo)

**Retorna**: URL pública ou `None` se falhar

**Recursos**:
- Upload com `upsert=true` (substitui se já existe)
- Content-Type: `application/x-coreldraw`
- Retorna URL pública automaticamente

### `update_printa_table(job_id, public_url)`

Atualiza a tabela Printa com o link público.

**Parâmetros**:
- `job_id` (str): ID usado para localizar o registro
- `public_url` (str): URL pública do arquivo CDR

**Retorna**: `True` se sucesso, `False` se falhar

**Query SQL equivalente**:
```sql
UPDATE Printa
SET link_arquivo_output = 'https://...'
WHERE id = 'lula-bar-001'
```

---

## 📊 Modelo JobStatus Atualizado

Novo campo adicionado:

```python
class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str
    files: Optional[dict] = None
    supabase_url: Optional[str] = None  # ← NOVO!
    created_at: str
    completed_at: Optional[str] = None
```

---

## 🔐 Segurança

### Tratamento de Erros

A integração Supabase é **não-bloqueante**:
- Se o upload falhar, o processamento continua
- Os arquivos locais ainda são gerados
- Logs de erro são registrados
- O job é marcado como `completed` de qualquer forma

**Avisos nos logs**:
```
[job_id] ⚠️ Falha no upload para Supabase
[job_id] ⚠️ Upload feito, mas falha ao atualizar tabela
```

### Upsert Automático

Se um arquivo com o mesmo nome já existe no bucket, ele é substituído automaticamente (`upsert: true`).

---

## 🧪 Testando a Integração

### Script Python Atualizado

O `exemplo_formatar.py` foi atualizado para mostrar a URL do Supabase:

```bash
python exemplo_formatar.py
```

**Saída esperada**:
```
✅ Processamento concluído!

🌐 SUPABASE:
   URL Pública: https://weshxwjwrtsypnqyqkbz.supabase.co/storage/v1/object/public/corel/lula-bar-001.cdr

📦 Arquivos gerados:
      - CDR: cardapio_lula-bar-001.cdr
        Download: http://localhost:8000/cardapio/download/lula-bar-001/cdr
      - PDF: cardapio.pdf
        Download: http://localhost:8000/cardapio/download/lula-bar-001/pdf
      ...
```

---

## 📝 Integração com n8n

### Nó HTTP Request para Formatar

**Method**: POST
**URL**: `http://localhost:8000/cardapio/formatar`

**Body**:
```json
{
  "id": "{{ $json.id_registro }}",
  "text": "{{ $json.conteudo_cardapio }}",
  "font": "Arial",
  "font_size": 10.0
}
```

### Monitorar Status

Loop até status = "completed"

### Usar URL do Supabase

Quando completar, extrair o campo `supabase_url`:

```json
{
  "supabase_url": "{{ $json.supabase_url }}"
}
```

Esta URL pode ser:
- Enviada por email
- Salva em outro banco
- Usada para download direto
- Compartilhada com clientes

---

## 🐛 Possíveis Erros

### Erro: "Bucket not found"

**Causa**: O bucket `corel` não existe no Supabase

**Solução**:
1. Acessar Supabase Dashboard
2. Storage → New Bucket
3. Nome: `corel`
4. Public: Yes

### Erro: "Table 'Printa' doesn't exist"

**Causa**: Tabela não existe no banco

**Solução**:
```sql
CREATE TABLE Printa (
  id VARCHAR PRIMARY KEY,
  link_arquivo_output VARCHAR
);
```

### Erro: "Permission denied"

**Causa**: Chave de API sem permissões

**Solução**: Verificar se está usando a `service_role` key ou `anon` key com as permissões corretas.

---

## 📦 Arquivos Modificados

### Modificados
- `api_cardapio.py` - API atualizada para v4.2
- `exemplo_formatar.py` - Script de teste atualizado

### Novos
- `CHANGELOG_v4.2_SUPABASE.md` - Este arquivo

---

## 🎯 Compatibilidade

- ✅ **Retrocompatível** com v4.1
- ✅ Endpoint `/cardapio/gerar` continua funcionando
- ✅ Sem breaking changes
- ⚠️ Nova dependência: `supabase-py` (já instalada)

---

## 🚦 Status de Implementação

- ✅ Upload para bucket Supabase
- ✅ Obtenção de URL pública
- ✅ Atualização da tabela Printa
- ✅ Tratamento de erros
- ✅ Logs detalhados
- ✅ Documentação atualizada
- ✅ Script de exemplo atualizado

---

## 💡 Próximos Passos (Sugestões v4.3)

- [ ] Webhook para notificar quando upload completo
- [ ] Upload do PDF também (opcional)
- [ ] Configuração via variáveis de ambiente
- [ ] Retry automático em caso de falha
- [ ] Metricas de upload (tempo, tamanho)

---

**Data de Release**: 31 de Outubro de 2025
**Versão**: 4.2
**Feature Principal**: Integração Completa com Supabase
