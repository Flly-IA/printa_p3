# ☁️ Configurar Domínio com Cloudflare Tunnel (Gratuito e Permanente)

## Vantagens
- ✅ 100% Gratuito
- ✅ Domínio personalizado
- ✅ HTTPS automático
- ✅ Túnel permanente (não precisa reiniciar)
- ✅ Mais seguro que ngrok

## Passo 1: Ter um Domínio

Você precisa ter um domínio (pode ser gratuito):
- Gratuito: Freenom, DuckDNS, No-IP
- Pago: Registro.br, GoDaddy, Namecheap

## Passo 2: Criar Conta Cloudflare

1. Acesse: https://dash.cloudflare.com/sign-up
2. Crie uma conta gratuita
3. Adicione seu domínio no Cloudflare
4. Configure os nameservers (o Cloudflare vai te guiar)

## Passo 3: Instalar cloudflared

1. Baixe: https://github.com/cloudflare/cloudflared/releases
2. Baixe o arquivo `cloudflared-windows-amd64.exe`
3. Renomeie para `cloudflared.exe`
4. Coloque em: `C:\cardapio_api\`

## Passo 4: Login no Cloudflare

No CMD:
```cmd
cd C:\cardapio_api
cloudflared tunnel login
```

Isso vai abrir o navegador para você autorizar.

## Passo 5: Criar Túnel

```cmd
cloudflared tunnel create cardapio-api
```

Anote o **Tunnel ID** que aparecer.

## Passo 6: Configurar Túnel

Crie um arquivo `config.yml`:

```yaml
tunnel: TUNNEL_ID_AQUI
credentials-file: C:\cardapio_api\.cloudflared\TUNNEL_ID.json

ingress:
  - hostname: api.seu-dominio.com
    service: http://localhost:8000
  - service: http_status:404
```

## Passo 7: Configurar DNS

```cmd
cloudflared tunnel route dns cardapio-api api.seu-dominio.com
```

## Passo 8: Iniciar Túnel

```cmd
cloudflared tunnel run cardapio-api
```

✅ **Pronto!** Sua API está em: `https://api.seu-dominio.com`

## 🔄 Rodar Automaticamente (Windows Service)

```cmd
cloudflared service install
cloudflared service start
```

Agora o túnel inicia automaticamente com o Windows!

## 🎯 Usar no n8n

```
https://api.seu-dominio.com/cardapio/gerar
```
