# 🏗️ ARQUITETURA DA API

## 📊 Fluxo de Dados

```
┌─────────────┐
│   Cliente   │ (Web/Mobile/Desktop)
│  (Browser)  │
└─────┬───────┘
      │
      │ HTTP POST /cardapio/gerar
      │ (arquivo TXT + config)
      ▼
┌─────────────────────────────────────┐
│         FastAPI (Python)            │
│  ┌───────────────────────────────┐  │
│  │  Endpoints REST               │  │
│  │  - POST /cardapio/gerar       │  │
│  │  - GET  /cardapio/status/{id} │  │
│  │  - GET  /cardapio/download    │  │
│  └───────────────────────────────┘  │
│              │                       │
│              ▼                       │
│  ┌───────────────────────────────┐  │
│  │  Background Tasks             │  │
│  │  (Processamento Assíncrono)   │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               │ parse_txt()
               ▼
┌──────────────────────────────────────┐
│   build_cardapio_dinamico.py         │
│   ┌──────────────────────────────┐   │
│   │  Parser de TXT               │   │
│   │  - Extrai restaurante        │   │
│   │  - Extrai categorias         │   │
│   │  - Extrai itens/preços       │   │
│   │  - Define modelo (A/B)       │   │
│   └──────────────────────────────┘   │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   CorelDRAW COM Automation           │
│   ┌──────────────────────────────┐   │
│   │  win32com.client             │   │
│   │  - Abre template CDR         │   │
│   │  - Cria título               │   │
│   │  - Cria caixas de texto      │   │
│   │  - Aplica formatação         │   │
│   │  - Exporta PDF/PNG           │   │
│   └──────────────────────────────┘   │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Outputs Directory                  │
│   /outputs/{job_id}/                 │
│   ├── cardapio_output.cdr            │
│   ├── cardapio_output.pdf            │
│   ├── cardapio_output.png            │
│   ├── parsed.json                    │
│   └── auditoria.csv                  │
└──────────────┬───────────────────────┘
               │
               │ GET /cardapio/download
               ▼
         ┌──────────┐
         │ Cliente  │
         │ (Files)  │
         └──────────┘
```

## 🔄 Ciclo de Vida de uma Requisição

### 1️⃣ Upload (Cliente → API)
```
Cliente --[TXT file]--> FastAPI
```
- Valida arquivo .txt
- Gera UUID único (job_id)
- Salva em `/temp/{job_id}_input.txt`
- Cria registro no cache de jobs
- Retorna job_id ao cliente

### 2️⃣ Processamento (API → CorelDRAW)
```
FastAPI --[background task]--> Parser ---> CorelDRAW
```
**Etapas:**
1. Parse do TXT
   - Extrai nome do restaurante
   - Identifica categorias (entre `*asteriscos*`)
   - Extrai itens e preços
   - Calcula total de itens
   - Define modelo (A ≤30 itens, B >30 itens)

2. Auditoria
   - Gera `parsed.json`
   - Gera `auditoria.csv`

3. CorelDRAW Automation
   - Abre template (tplA.cdr ou tplB.cdr)
   - Remove textos existentes
   - Cria título centralizado (Arial 24pt bold)
   - Cria caixas de texto para conteúdo
   - Aplica formatação (fonte, tabs, negrito)
   - Preenche conteúdo

4. Exportação
   - Salva .cdr
   - Exporta .pdf
   - Exporta .png (300 DPI)

### 3️⃣ Polling (Cliente → API)
```
Cliente --[GET /status]--> API --[job status]--> Cliente
```
**Estados:**
- `pending`: Aguardando
- `processing`: Processando
- `completed`: Concluído
- `failed`: Falhou

### 4️⃣ Download (Cliente ← API)
```
Cliente <--[files]-- API
```
Cliente baixa arquivos via:
```
GET /cardapio/download/{job_id}/{file_type}
```

## 🗂️ Estrutura de Pastas

```
cardapio-api/
│
├── api_cardapio.py              # 🎯 API FastAPI principal
├── build_cardapio_dinamico.py   # ⚙️ Motor de processamento
├── create_templates.py          # 🎨 Criador de templates
├── start_api.py                 # 🚀 Script de inicialização
├── test_api_client.py           # 🧪 Cliente de teste
├── web_client.html              # 🌐 Interface web
├── requirements_api.txt         # 📦 Dependências
├── deploy_windows.bat           # 🪟 Deploy Windows
│
├── templates/                   # 📋 Templates CorelDRAW
│   ├── tplA.cdr                 # Template 1 coluna
│   └── tplB.cdr                 # Template 2 colunas
│
├── outputs/                     # 📤 Arquivos gerados
│   └── {job_id}/
│       ├── cardapio_output.cdr
│       ├── cardapio_output.pdf
│       ├── cardapio_output.png
│       ├── parsed.json
│       └── auditoria.csv
│
└── temp/                        # 🗃️ Arquivos temporários
    └── {job_id}_input.txt
```

## 🔌 API Endpoints

### 1. Health Check
```http
GET /health
```
**Resposta:** Status da API e CorelDRAW

### 2. Gerar Cardápio
```http
POST /cardapio/gerar
Content-Type: multipart/form-data

file: <arquivo.txt>
font: Arial
font_size: 10.0
```
**Resposta:** `{job_id, status, message}`

### 3. Status do Job
```http
GET /cardapio/status/{job_id}
```
**Resposta:** `{status, message, files, timestamps}`

### 4. Download
```http
GET /cardapio/download/{job_id}/{file_type}
```
**file_type:** pdf | png | cdr | json | csv

### 5. Listar Jobs
```http
GET /cardapio/listar
```
**Resposta:** Lista de todos os jobs

### 6. Limpar Job
```http
DELETE /cardapio/limpar/{job_id}
```
**Ação:** Remove arquivos e cache

## 🔐 Segurança (Produção)

### Adicionar Autenticação
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.post("/cardapio/gerar")
async def gerar(credentials: HTTPBasicCredentials = Depends(security)):
    # Validar credenciais
    ...
```

### HTTPS via Nginx
```nginx
server {
    listen 443 ssl;
    server_name seu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/cardapio/gerar")
@limiter.limit("10/minute")
async def gerar(...):
    ...
```

## 📈 Escalabilidade

### Opção 1: Múltiplos Workers
```bash
uvicorn api_cardapio:app --workers 4 --host 0.0.0.0 --port 8000
```

### Opção 2: Fila Redis (Celery)
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def process_cardapio(job_id, input_path, config):
    ...
```

### Opção 3: Load Balancer
```
       ┌─────────┐
       │ Nginx   │
       │ (LB)    │
       └────┬────┘
            │
    ┌───────┼───────┐
    │       │       │
 ┌──▼──┐ ┌─▼──┐ ┌─▼──┐
 │API 1│ │API│ │API│
 │:8000│ │:800│ │:800│
 └─────┘ └────┘ └────┘
```

## 🎯 Casos de Uso

### 1. Restaurante Individual
- Upload manual via interface web
- 1-5 cardápios por dia
- Servidor local ou cloud simples

### 2. Rede de Restaurantes
- Integração com sistema central
- API calls automatizados
- Servidor dedicado Windows

### 3. Plataforma SaaS
- Multi-tenant
- Autenticação por usuário
- Fila de processamento
- Storage S3/Azure Blob

## 🚀 Performance

### Tempos Médios
- Upload: < 1s
- Parsing: < 2s
- CorelDRAW: 10-30s (depende da complexidade)
- Export PDF/PNG: 5-15s
- **Total: 20-50s por cardápio**

### Otimizações
1. **Cache de templates** pré-carregados
2. **Reutilizar instância** do CorelDRAW
3. **Processamento paralelo** (múltiplos CorelDRAW)
4. **Compressão** de imagens PNG

---

**Arquitetura robusta e escalável! 💪**
