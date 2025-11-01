# 🦆 Configurar Domínio Gratuito com DuckDNS

## Vantagens
- ✅ 100% Gratuito
- ✅ Domínio personalizado (ex: minha-api.duckdns.org)
- ✅ IP dinâmico não é problema
- ⚠️ Ainda precisa abrir portas no roteador

## Passo 1: Criar Conta

1. Acesse: https://www.duckdns.org/
2. Faça login com Google/GitHub
3. Crie um subdomínio (ex: `cardapio-api`)
4. Resultado: `cardapio-api.duckdns.org`

## Passo 2: Anotar Token

No painel do DuckDNS, copie seu **token** (string grande)

## Passo 3: Atualizar IP Automaticamente

Crie um script `atualizar_duckdns.bat`:

```batch
@echo off
curl "https://www.duckdns.org/update?domains=SEU_SUBDOMINIO&token=SEU_TOKEN&ip="
timeout /t 300 /nobreak
goto :loop
```

Substitua:
- `SEU_SUBDOMINIO` = cardapio-api (sem .duckdns.org)
- `SEU_TOKEN` = seu token do DuckDNS

## Passo 4: Rodar o Script

Execute o script. Ele vai atualizar seu IP a cada 5 minutos.

Para rodar automaticamente no boot:
1. Pressione `Win + R`
2. Digite: `shell:startup`
3. Copie o script para esta pasta

## Passo 5: Port Forwarding no Roteador

1. Acesse o painel do seu roteador (geralmente 192.168.1.1)
2. Procure por "Port Forwarding" ou "Encaminhamento de Portas"
3. Adicione:
   - Porta Externa: 8000
   - IP Interno: (IP da VM que você descobriu)
   - Porta Interna: 8000
   - Protocolo: TCP

## Passo 6: Testar

De fora da sua rede (usando dados móveis ou outro local):
```
http://cardapio-api.duckdns.org:8000/ping
```

## 🔒 Adicionar HTTPS (Opcional)

Você pode usar Let's Encrypt com Certbot, mas é mais complexo no Windows.

Alternativa: Use Cloudflare Tunnel em vez de DuckDNS (HTTPS automático).

## ⚠️ Limitações

- Requer abrir portas no roteador (nem sempre é possível)
- Sem HTTPS automático
- Menos seguro que Cloudflare Tunnel
- Pode não funcionar em redes corporativas

## 💡 Recomendação

Se você quer domínio gratuito + HTTPS, use **Cloudflare Tunnel** em vez de DuckDNS.
