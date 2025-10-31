# 🍽️ API Cardápio Dinâmico

API FastAPI para geração automática de cardápios em PDF/PNG/CDR usando CorelDRAW.

## 📋 Requisitos

### Sistema
- **Windows** (10/11 ou Windows Server)
- **CorelDRAW** instalado e licenciado (testado com versões X7, 2018, 2019, 2020, 2021)
- **Python 3.8+**

### Dependências Python
```bash
pip install -r requirements_api.txt
```

## 🚀 Instalação

### 1. Clonar ou baixar o projeto
```bash
git clone <seu-repositorio>
cd cardapio-api
```

### 2. Instalar dependências
```bash
pip install -r requirements_api.txt
```

### 3. Criar templates CorelDRAW
```bash
python create_templates.py
```

Isso criará `tplA.cdr` e `tplB.cdr` no diretório raiz.

### 4. Organizar templates
Crie a pasta `templates` e mova os arquivos:
```bash
mkdir templates
move tplA.cdr templates\
move tplB.cdr templates\
```

## ▶️ Executar a API

### Opção 1: Script de inicialização (recomendado)
```bash
python start_api.py
```

### Opção 2: Uvicorn direto
```bash
uvicorn api_cardapio:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em: `http://localhost:8000`

## 📖 Documentação

Após iniciar a API, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints

### 1. Health Check
```bash
GET /health
```

Verifica se a API e CorelDRAW estão funcionando.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T10:00:00",
  "corel_draw": "available",
  "templates": {
    "tplA": true,
    "tplB": true
  }
}
```

### 2. Gerar Cardápio
```bash
POST /cardapio/gerar
```

**Parâmetros:**
- `file` (form-data): Arquivo TXT com relatório de preços
- `font` (opcional): Nome da fonte (padrão: Arial)
- `font_size` (opcional): Tamanho da fonte em pt (padrão: 10.0)

**Exemplo com cURL:**
```bash
curl -X POST "http://localhost:8000/cardapio/gerar" \
  -F "file=@teste_input.txt" \
  -F "font=Arial" \
  -F "font_size=10.0"
```

**Resposta:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "message": "Processamento iniciado",
  "status_url": "/cardapio/status/123e4567-e89b-12d3-a456-426614174000"
}
```

### 3. Verificar Status
```bash
GET /cardapio/status/{job_id}
```

**Resposta:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "message": "Cardápio gerado com sucesso",
  "files": {
    "cdr": "cardapio_output.cdr",
    "pdf": "cardapio_output.pdf",
    "png": "cardapio_output.png",
    "json": "parsed.json",
    "csv": "auditoria.csv"
  },
  "created_at": "2025-10-30T10:00:00",
  "completed_at": "2025-10-30T10:00:45"
}
```

**Status possíveis:**
- `pending`: Aguardando processamento
- `processing`: Em processamento
- `completed`: Concluído com sucesso
- `failed`: Falha no processamento

### 4. Download de Arquivo
```bash
GET /cardapio/download/{job_id}/{file_type}
```

**file_type:** `pdf`, `png`, `cdr`, `json`, `csv`

**Exemplo:**
```bash
curl -O "http://localhost:8000/cardapio/download/123e4567.../pdf"
```

### 5. Listar Jobs
```bash
GET /cardapio/listar
```

**Resposta:**
```json
{
  "total": 5,
  "jobs": [...]
}
```

### 6. Limpar Job
```bash
DELETE /cardapio/limpar/{job_id}
```

Remove arquivos e dados do job.

## 🧪 Testar a API

Use o cliente de exemplo:
```bash
python test_api_client.py
```

Isso irá:
1. Verificar health da API
2. Fazer upload do `teste_input.txt`
3. Aguardar processamento
4. Baixar todos os arquivos gerados
5. Listar jobs

## 📂 Estrutura de Pastas

```
cardapio-api/
├── api_cardapio.py           # API FastAPI
├── build_cardapio_dinamico.py # Módulo de processamento
├── create_templates.py        # Criador de templates
├── start_api.py              # Script de inicialização
├── test_api_client.py        # Cliente de teste
├── requirements_api.txt       # Dependências
├── templates/                 # Templates CDR
│   ├── tplA.cdr
│   └── tplB.cdr
├── outputs/                   # Saídas (criado automaticamente)
│   └── {job_id}/
│       ├── cardapio_output.cdr
│       ├── cardapio_output.pdf
│       ├── cardapio_output.png
│       ├── parsed.json
│       └── auditoria.csv
└── temp/                      # Arquivos temporários
```

## 🔧 Formato do Arquivo de Entrada

```txt
RELATÓRIO DE PREÇOS Nome do Restaurante

*Categoria 1*
Item 1 - R$ 10,00
Item 2 - R$ 15,00

*Categoria 2*
Item 3 - R$ 20,00
Item 4 - R$ 25,00
```

**Regras:**
- Categorias entre `*asteriscos*`
- Itens no formato: `Nome - R$ Preço`
- Nome do restaurante após "RELATÓRIO DE PREÇOS"
- Modelo A (1 coluna): até 30 itens
- Modelo B (2 colunas): mais de 30 itens

## 🌐 Deploy em Servidor Windows

### Azure VM / AWS EC2 / DigitalOcean

1. **Criar VM Windows Server**
   - Windows Server 2019/2022
   - Mínimo: 2 vCPU, 4GB RAM

2. **Instalar Python**
   ```powershell
   # Baixar do python.org ou usar Chocolatey
   choco install python
   ```

3. **Instalar CorelDRAW**
   - Instalar versão completa
   - Ativar licença

4. **Clonar projeto**
   ```powershell
   git clone <repo>
   cd cardapio-api
   pip install -r requirements_api.txt
   ```

5. **Configurar como Serviço Windows**

   Criar `run_api.bat`:
   ```batch
   @echo off
   cd /d %~dp0
   python start_api.py
   ```

   Usar **NSSM** para criar serviço:
   ```powershell
   # Baixar NSSM
   choco install nssm

   # Criar serviço
   nssm install CardapioAPI "C:\caminho\para\run_api.bat"
   nssm set CardapioAPI AppDirectory "C:\caminho\para\cardapio-api"
   nssm start CardapioAPI
   ```

6. **Configurar Firewall**
   ```powershell
   New-NetFirewallRule -DisplayName "CardapioAPI" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
   ```

7. **Acessar remotamente**
   ```
   http://SEU_IP_PUBLICO:8000
   ```

### Nginx Reverse Proxy (Opcional)

Instalar Nginx no Windows e configurar:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Segurança

### Autenticação (Recomendada para produção)

Adicionar autenticação básica na API:

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.post("/cardapio/gerar")
async def gerar_cardapio(
    credentials: HTTPBasicCredentials = Depends(security),
    ...
):
    # Validar credenciais
    if credentials.username != "admin" or credentials.password != "senha":
        raise HTTPException(status_code=401, detail="Não autorizado")
    ...
```

### HTTPS

Use **Certbot** ou certificado SSL no Nginx.

## 📊 Monitoramento

### Logs

A API usa logging padrão do Python. Para salvar em arquivo:

```python
# No início de api_cardapio.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
```

### Métricas

Considere adicionar:
- **Prometheus** + **Grafana**
- **Sentry** para erros

## 🐛 Troubleshooting

### CorelDRAW não inicializa
- Verificar se está instalado
- Executar CorelDRAW manualmente uma vez
- Verificar licença ativa

### Erro "CorelDRAW COM indisponível"
```bash
# Registrar DLLs manualmente
cd "C:\Program Files\Corel\CorelDRAW Graphics Suite X8\Programs64"
regsvr32 CorelDRW.Application.dll
```

### Timeout no processamento
- Aumentar timeout no `wait_for_completion()`
- Verificar recursos do servidor (RAM, CPU)

### Fontes não encontradas
- Instalar fontes no Windows
- Usar fontes do sistema (Arial, Times New Roman)

## 📝 TODO

- [ ] Adicionar autenticação JWT
- [ ] Suporte a múltiplos templates personalizados
- [ ] Webhook para notificar conclusão
- [ ] Cache de templates compilados
- [ ] Fila Redis para processamento distribuído
- [ ] Dashboard admin

## 📄 Licença

MIT License

## 🤝 Contribuindo

Pull requests são bem-vindos!

## 📧 Suporte

Para dúvidas e suporte, abra uma issue no GitHub.

---

**Desenvolvido com ❤️ usando FastAPI + CorelDRAW COM**
