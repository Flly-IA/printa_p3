# 🚀 Configurar Domínio com ngrok

## Passo 1: Criar Conta (Gratuito)

1. Acesse: https://ngrok.com/
2. Clique em "Sign up" (pode usar Google/GitHub)
3. Após login, pegue seu **authtoken**

## Passo 2: Baixar ngrok

1. Acesse: https://ngrok.com/download
2. Baixe a versão para Windows
3. Extraia o `ngrok.exe` para: `C:\cardapio_api\`

## Passo 3: Configurar Token

No CMD, execute:
```cmd
cd C:\cardapio_api
ngrok config add-authtoken SEU_TOKEN_AQUI
```

## Passo 4: Iniciar Túnel

```cmd
ngrok http 8000
```

Você verá algo como:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

✅ **Pronto!** Sua API está acessível em: `https://abc123.ngrok-free.app`

## 🎯 Usar no n8n

No n8n, use a URL do ngrok:
```
https://abc123.ngrok-free.app/cardapio/gerar
```

## 💎 Domínio Personalizado (Plano Pago)

Com o plano pago do ngrok ($8/mês), você pode:
```cmd
ngrok http 8000 --domain=api-cardapio.seu-dominio.com
```

## ⚠️ IMPORTANTE

- A URL gratuita muda toda vez que você reinicia o ngrok
- O túnel só funciona enquanto o ngrok estiver rodando
- Para produção, considere as outras opções abaixo

## 🔒 Adicionar Autenticação Básica (Opcional)

```cmd
ngrok http 8000 --basic-auth="usuario:senha"
```

Agora quem acessar precisa fornecer usuário e senha!
