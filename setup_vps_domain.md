# 🖥️ Configurar Domínio em VPS (Produção)

## Quando Usar
- ✅ Para produção profissional
- ✅ Controle total
- ✅ Performance melhor
- ❌ Requer conhecimento técnico
- ❌ Custo mensal (~$5-20/mês)

## Opção A: Migrar para VPS Linux

### Passo 1: Contratar VPS

Opções populares:
- **DigitalOcean** ($6/mês): https://digitalocean.com
- **Vultr** ($5/mês): https://vultr.com
- **Linode** ($5/mês): https://linode.com
- **AWS Lightsail** ($3.50/mês): https://aws.amazon.com/lightsail

### Passo 2: Configurar Servidor

```bash
# Instalar dependências
apt update
apt install -y python3 python3-pip nginx certbot

# Copiar sua API para o servidor
# Instalar dependências Python
pip3 install -r requirements.txt

# Configurar Nginx como proxy reverso
nano /etc/nginx/sites-available/api-cardapio
```

### Passo 3: Configurar Nginx

```nginx
server {
    listen 80;
    server_name api.seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Passo 4: Ativar HTTPS

```bash
certbot --nginx -d api.seu-dominio.com
```

### Passo 5: Configurar DNS

No painel do seu domínio:
```
Tipo: A
Nome: api
Valor: IP_DO_SEU_VPS
```

✅ **Pronto!** `https://api.seu-dominio.com`

## Opção B: Reverse Proxy Local (Não Recomendado)

Se você quer manter na VM local mas ter domínio:

1. Configure Port Forwarding no roteador (porta 80 e 443)
2. Aponte o domínio para seu IP público
3. Configure um reverse proxy (nginx/caddy)

⚠️ **Problemas:**
- Seu IP público pode mudar
- Segurança menor
- Performance depende da sua internet
