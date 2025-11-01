# 🔧 Solução: Acesso Externo à API não Funciona

## 🔍 Diagnóstico

O IP `190.102.40.94` é um **IP público da internet**, não o IP local da sua VM na rede.

Para acessar a API de outra máquina (como o n8n), você precisa do **IP local da rede privada** (192.168.x.x ou 10.x.x.x).

---

## ✅ PASSO 1: Executar Diagnóstico Completo

Execute: `diagnostico_rede.bat`

Procure por IPs que comecem com:
- `192.168.x.x` ✅
- `10.x.x.x` ✅
- `172.16.x.x` até `172.31.x.x` ✅

**Ignore** IPs que comecem com:
- `190.x.x.x` ❌ (IP público)
- `127.0.0.1` ❌ (localhost)
- `169.254.x.x` ❌ (IP automático sem DHCP)

---

## ✅ PASSO 2: Verificar Modo de Rede da VM

### Se você usa **VirtualBox:**

1. Feche a VM
2. Abra o VirtualBox
3. Selecione a VM > Configurações > Rede
4. **Modo Recomendado:** "Placa em modo Bridge"
   - Isso faz a VM aparecer como um computador separado na rede
   - Ela receberá um IP próprio do roteador

**OU** se quiser manter NAT:

1. Configure Port Forwarding:
   - VirtualBox > VM > Configurações > Rede > Avançado > Encaminhamento de Portas
   - Clique em "+" para adicionar:
     - Nome: API
     - Protocolo: TCP
     - IP do Hospedeiro: (deixe vazio)
     - Porta do Hospedeiro: 8000
     - IP do Convidado: (deixe vazio)
     - Porta do Convidado: 8000

2. Acesse usando o IP do HOST (seu computador principal): `http://IP_DO_HOST:8000`

### Se você usa **VMware:**

1. Abra VMware
2. Selecione a VM > Edit Settings > Network Adapter
3. **Modo Recomendado:** "Bridged: Connected directly to the physical network"

**OU** se quiser manter NAT:

1. Edit > Virtual Network Editor (pode precisar de admin)
2. Selecione VMnet8 (NAT)
3. NAT Settings
4. Port Forwarding > Add:
   - Host Port: 8000
   - Virtual Machine IP: (IP da VM que você anotou)
   - Virtual Machine Port: 8000

---

## ✅ PASSO 3: Reabrir Firewall (Importante!)

Depois de mudar a configuração de rede, execute novamente como admin:

```
abrir_firewall.bat
```

---

## ✅ PASSO 4: Reiniciar a API

1. Pare a API (Ctrl+C no terminal)
2. Reinicie: `python api_cardapio.py`
3. Verifique os logs se mostra: `Uvicorn running on http://0.0.0.0:8000`

---

## ✅ PASSO 5: Testar

### Na VM:
```
http://localhost:8000/ping
```

### De outra máquina na mesma rede:
```
http://192.168.x.x:8000/ping
```
*(Use o IP local que você descobriu no diagnóstico)*

---

## 🎯 Cenários Comuns

### Cenário 1: n8n na MESMA rede local
- Configure a VM em modo **Bridge**
- Use o IP local da VM: `http://192.168.x.x:8000`

### Cenário 2: n8n na NUVEM (fora da rede)
Você tem 3 opções:

#### Opção A: VPN
- Configure uma VPN entre a rede local e o n8n
- Use o IP local da VM através da VPN

#### Opção B: Túnel Reverso (ngrok, localtunnel)
Na VM, instale ngrok:
```bash
# Baixe ngrok de: https://ngrok.com/download
ngrok http 8000
```
Use a URL pública gerada (ex: `https://abc123.ngrok.io`)

#### Opção C: Expor Publicamente (NÃO RECOMENDADO sem autenticação)
1. Configure Port Forwarding no roteador:
   - Porta Externa: 8000
   - IP Interno: (IP da VM)
   - Porta Interna: 8000
2. Use o IP público do roteador: `http://SEU_IP_PUBLICO:8000`
3. **ATENÇÃO:** Adicione autenticação à API primeiro!

### Cenário 3: n8n rodando na MESMA VM
- Use simplesmente: `http://localhost:8000`

---

## 🧪 Script de Teste

Crie um arquivo `test_api.py` na VM:

```python
import requests

# Teste 1: Localhost
try:
    r = requests.get("http://localhost:8000/ping", timeout=5)
    print(f"✅ Localhost: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"❌ Localhost: {e}")

# Teste 2: IP local (substitua pelo seu IP)
try:
    r = requests.get("http://192.168.1.100:8000/ping", timeout=5)
    print(f"✅ IP Local: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"❌ IP Local: {e}")
```

---

## 📋 Checklist de Troubleshooting

- [ ] Executei `diagnostico_rede.bat` e anotei o IP local (192.168.x.x)
- [ ] A API está rodando (`python api_cardapio.py`)
- [ ] `http://localhost:8000/ping` funciona na VM
- [ ] Configurei a VM em modo Bridge (ou configurei Port Forwarding)
- [ ] Executei `abrir_firewall.bat` como administrador
- [ ] Testei de outra máquina com o IP correto
- [ ] Verifiquei que n8n e VM estão na mesma rede

---

## 🆘 Ainda não funciona?

Me envie o resultado completo de:
1. `diagnostico_rede.bat`
2. Qual VM você usa? (VirtualBox, VMware, Hyper-V)
3. Onde o n8n está rodando? (mesma rede, nuvem, mesma VM)
