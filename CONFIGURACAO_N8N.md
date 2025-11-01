# Configuração da API para Acesso Externo (n8n)

## 📋 Passo a Passo

### 1. Descobrir o IP da Máquina Virtual

1. Execute o arquivo: `get_network_info.bat`
2. Anote o IP mostrado (ex: `192.168.1.100`)

### 2. Abrir Porta no Firewall

1. **Clique com botão direito** em `abrir_firewall.bat`
2. Selecione **"Executar como administrador"**
3. Aguarde a confirmação

### 3. Testar a API Localmente

Abra o navegador na VM e acesse:
- http://localhost:8000 - Página inicial
- http://localhost:8000/ping - Teste de conectividade
- http://localhost:8000/docs - Documentação interativa

### 4. Testar de Outra Máquina

De outra máquina na mesma rede, acesse:
- http://IP_DA_VM:8000/ping

Substitua `IP_DA_VM` pelo IP que você anotou no passo 1.

---

## 🔌 Configuração no n8n

### Endpoint: Teste de Conectividade

**URL:** `http://IP_DA_VM:8000/ping`
**Método:** GET
**Resposta esperada:**
```json
{
  "status": "ok",
  "message": "API está respondendo",
  "timestamp": "2025-10-31T...",
  "server": {
    "hostname": "...",
    "local_ip": "...",
    "port": 8000
  }
}
```

### Endpoint: Gerar Cardápio

**URL:** `http://IP_DA_VM:8000/cardapio/gerar`
**Método:** POST
**Headers:**
```
Content-Type: multipart/form-data
```
**Body (form-data):**
- `file`: (arquivo .txt com o cardápio)
- `font`: Arial (opcional)
- `font_size`: 10 (opcional)

**Query Parameters (opcional):**
- `?font=Arial&font_size=10`

**Resposta:**
```json
{
  "job_id": "uuid-do-job",
  "status": "pending",
  "message": "Processamento iniciado",
  "status_url": "/cardapio/status/{job_id}"
}
```

### Endpoint: Verificar Status

**URL:** `http://IP_DA_VM:8000/cardapio/status/{job_id}`
**Método:** GET

**Resposta (processando):**
```json
{
  "job_id": "...",
  "status": "processing",
  "message": "...",
  "files": null,
  "created_at": "...",
  "completed_at": null
}
```

**Resposta (concluído):**
```json
{
  "job_id": "...",
  "status": "completed",
  "message": "Cardápio processado com sucesso!",
  "files": {
    "cdr": "cardapio_xxx.cdr",
    "pdf": "cardapio.pdf",
    "json": "parsed.json",
    "csv": "auditoria.csv"
  },
  "created_at": "...",
  "completed_at": "..."
}
```

### Endpoint: Download de Arquivo

**URL:** `http://IP_DA_VM:8000/cardapio/download/{job_id}/{file_type}`
**Método:** GET
**file_type:** `cdr`, `pdf`, `json`, ou `csv`

**Retorna:** O arquivo para download

---

## 🔄 Exemplo de Workflow no n8n

### 1. Testar Conectividade
```
HTTP Request Node
├─ Method: GET
├─ URL: http://IP_DA_VM:8000/ping
└─ Authentication: None
```

### 2. Upload do Arquivo
```
HTTP Request Node
├─ Method: POST
├─ URL: http://IP_DA_VM:8000/cardapio/gerar?font=Arial&font_size=10
├─ Body Content Type: Multipart Form Data
├─ Body Parameters:
│  └─ file: [Binary Data]
└─ Response: Save to {{ $json.job_id }}
```

### 3. Aguardar Processamento (Loop)
```
Wait Node (30 segundos)
↓
HTTP Request Node
├─ Method: GET
├─ URL: http://IP_DA_VM:8000/cardapio/status/{{ $json.job_id }}
└─ Verificar: status == "completed"
```

### 4. Download do PDF
```
HTTP Request Node
├─ Method: GET
├─ URL: http://IP_DA_VM:8000/cardapio/download/{{ $json.job_id }}/pdf
└─ Response Format: File
```

---

## 🛠️ Troubleshooting

### Erro: "Connection Refused"
- ✅ Verifique se a API está rodando (`python api_cardapio.py`)
- ✅ Verifique o IP correto da VM
- ✅ Verifique se a porta 8000 foi aberta no firewall

### Erro: "Timeout"
- ✅ Verifique se a VM está na mesma rede do n8n
- ✅ Verifique configurações de rede da VM (modo Bridge em vez de NAT)
- ✅ Tente desabilitar temporariamente o firewall para testar

### VM em Modo NAT (VirtualBox/VMware)
Se a VM estiver em modo NAT, configure port forwarding:
- **VirtualBox:** Settings > Network > Advanced > Port Forwarding
  - Host Port: 8000
  - Guest Port: 8000
- **VMware:** Virtual Network Editor > NAT Settings > Port Forwarding
  - Host Port: 8000
  - VM IP: (IP da VM)
  - VM Port: 8000

Depois acesse usando o IP do host: `http://IP_DO_HOST:8000`

---

## 📚 Documentação Completa

Acesse a documentação interativa em:
- http://IP_DA_VM:8000/docs (Swagger UI)
- http://IP_DA_VM:8000/redoc (ReDoc)

---

## ✅ Checklist Rápido

- [ ] Executei `get_network_info.bat` e anotei o IP
- [ ] Executei `abrir_firewall.bat` como administrador
- [ ] Testei `http://localhost:8000/ping` na VM
- [ ] Testei `http://IP_DA_VM:8000/ping` de outra máquina
- [ ] Configurei o n8n com o IP correto
- [ ] Testei o upload de um arquivo de teste
