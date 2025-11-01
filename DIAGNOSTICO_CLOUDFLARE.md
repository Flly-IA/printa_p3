# DIAGNÓSTICO DO PROBLEMA

## Erro Identificado
```
WARNING: Invalid HTTP request received.
```

## Causa
Você está tentando acessar: `https://windows-printa.lucrativa.app:8000/ping`

O problema é que **não se pode especificar porta customizada quando usa proxy do Cloudflare**.

## SOLUÇÃO CORRETA

### 1. Acesse SEM a porta:
```
https://windows-printa.lucrativa.app/ping
```

### 2. Configuração do Port Forwarding (Roteador)
O roteador precisa ter:
- Porta Externa: **80** → Porta Interna: **8000**
- Porta Externa: **443** → Porta Interna: **8000** (se quiser HTTPS direto)

### 3. Configuração Cloudflare

#### DNS:
- Type: A
- Name: windows-printa
- IPv4: 190.102.40.94
- Proxy status: **ATIVADO** (nuvem laranja 🟠)
- TTL: Auto

#### SSL/TLS:
**Escolha UMA das opções:**

**OPÇÃO A - Flexible (Mais Fácil)**
- SSL/TLS > Overview > Encryption mode: **Flexible**
- ❌ Não precisa de certificado SSL na sua VM
- ⚠️ Conexão entre Cloudflare e sua VM é HTTP (não criptografada)
- Port Forwarding: 80 → 8000

**OPÇÃO B - Full (Mais Seguro)**
- SSL/TLS > Overview > Encryption mode: **Full**
- ✅ Precisa de certificado SSL self-signed na VM
- ✅ Conexão entre Cloudflare e sua VM é HTTPS
- Port Forwarding: 443 → 8000
- Requer configurar uvicorn com SSL

## Como Testar

1. **Sem porta na URL:**
   ```
   https://windows-printa.lucrativa.app/ping
   ```

2. **Se não funcionar, teste sem proxy:**
   - Cloudflare > DNS > Desative o proxy (nuvem cinza)
   - Teste: `http://windows-printa.lucrativa.app:8000/ping`
   - Se funcionar assim, o problema é na configuração do proxy

3. **Verifique port forwarding:**
   - Acesse roteador (192.168.1.1)
   - Confirme regra: 80 → [IP LOCAL]:8000

## Comandos de Diagnóstico

Execute para verificar:
```bash
# Verificar se API está rodando
curl http://localhost:8000/ping

# Testar do IP local
curl http://190.102.40.94:8000/ping

# Testar DNS
nslookup windows-printa.lucrativa.app
```
