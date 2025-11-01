# 🔌 Configurar Port Forwarding para windows-printa.lucrativa.app

## Situação Atual
- ✅ Domínio: `windows-printa.lucrativa.app`
- ✅ IP Público: `190.102.40.94`
- ✅ Cloudflare: Ativo
- ❌ Port Forwarding: Não configurado

## 🎯 O Que Fazer

### Opção A: Porta 8000 Direta (Mais Simples)

#### 1. Configurar Port Forwarding no Roteador

Acesse o painel do seu roteador (geralmente `192.168.1.1` ou `192.168.0.1`):

**Configuração:**
```
Nome: API Cardapio
Porta Externa: 8000
IP Interno: (IP da VM - ex: 192.168.1.100)
Porta Interna: 8000
Protocolo: TCP
```

#### 2. Configurar Cloudflare

No painel do Cloudflare:
1. Vá em **DNS**
2. Clique no registro que aponta para `190.102.40.94`
3. **DESABILITE** o proxy (nuvem laranja → cinza)
   - Isso é necessário para portas não-padrão (8000)

#### 3. Testar

```
http://windows-printa.lucrativa.app:8000/ping
```

**⚠️ PROBLEMA:** Sem HTTPS e porta :8000 visível na URL

---

### Opção B: Porta 443 (HTTPS) - Recomendado

Para usar `https://windows-printa.lucrativa.app` (sem :8000):

#### 1. Configurar Port Forwarding

**Opção 1: Redirecionar 443 → 8000**
```
Porta Externa: 443
IP Interno: (IP da VM)
Porta Interna: 8000
Protocolo: TCP
```

**Opção 2: Usar porta padrão (80/443)**

Mude a API para rodar na porta 80 ou 443:

No arquivo `api_cardapio.py`, última linha:
```python
uvicorn.run(app, host="0.0.0.0", port=80)  # ou 443 para HTTPS
```

⚠️ **Porta 80/443 no Windows requer privilégios de administrador**

#### 2. Configurar HTTPS na API

Você tem 2 opções:

**Opção 1: Deixar Cloudflare fazer o HTTPS (Mais Fácil)**
1. No Cloudflare, **ATIVE** o proxy (nuvem laranja)
2. Configure SSL/TLS para "Flexible"
3. Port Forwarding: `443 → 8000` ou `80 → 8000`

Cloudflare vai:
- Cliente → HTTPS (porta 443) → Cloudflare
- Cloudflare → HTTP (porta 8000) → Sua API

**Opção 2: HTTPS na API (Mais Seguro)**

Gere certificado SSL:
```cmd
# Usando Certbot (requer porta 80 aberta)
certbot certonly --standalone -d windows-printa.lucrativa.app
```

Configure uvicorn com SSL:
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="path/to/privkey.pem",
    ssl_certfile="path/to/fullchain.pem"
)
```

Port Forwarding: `443 → 443`

---

## 🚀 RECOMENDAÇÃO: Usar Cloudflare Proxy (Opção B.1)

### Passo 1: Port Forwarding
```
Porta Externa: 80
IP Interno: 192.168.x.x (IP da VM)
Porta Interna: 8000
Protocolo: TCP
```

### Passo 2: Cloudflare
1. **SSL/TLS** → **Overview** → Modo: **Flexible**
2. **DNS** → Certifique-se que o proxy está **ATIVO** (nuvem laranja)

### Passo 3: Testar
```
https://windows-printa.lucrativa.app/ping
```

✅ **Pronto!** Cloudflare cuida do HTTPS para você!

---

## 🔍 Troubleshooting

### Erro: "Connection Refused"
- [ ] Firewall da VM está aberto? (Execute `abrir_firewall.bat`)
- [ ] Port Forwarding configurado corretamente?
- [ ] API está rodando?

### Erro: "Bad Gateway" (502)
- [ ] A API está realmente rodando na porta 8000?
- [ ] O IP interno está correto no port forwarding?

### Erro: "SSL Error"
- [ ] No Cloudflare: SSL/TLS → Modo: **Flexible**

---

## 📝 Checklist

- [ ] Port Forwarding configurado no roteador
- [ ] Firewall da VM liberado (porta 8000)
- [ ] API rodando: `python api_cardapio.py`
- [ ] Cloudflare SSL/TLS em "Flexible"
- [ ] Testado: `https://windows-printa.lucrativa.app/ping`

---

## 🆘 Precisa de Ajuda?

Me envie:
1. Qual modelo do seu roteador?
2. Print da configuração do Cloudflare (DNS + SSL/TLS)
3. Resultado do teste: `curl -I https://windows-printa.lucrativa.app/ping`
