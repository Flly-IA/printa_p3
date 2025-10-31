# 🍽️ API Cardápio Dinâmico - v1.0

**API REST para geração automática de cardápios em PDF/PNG/CDR usando CorelDRAW**

---

## 🚀 Começar em 3 Passos

1. **Instalar:**
   ```bash
   deploy_windows.bat
   ```

2. **Criar templates:**
   ```bash
   python create_templates.py
   move tplA.cdr templates\
   move tplB.cdr templates\
   ```

3. **Iniciar:**
   ```bash
   start_api.bat
   ```

Acesse: http://localhost:8000/docs

---

## 📚 Documentação

- **[INDICE.md](INDICE.md)** ← COMECE AQUI - Índice completo
- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Setup em 5 minutos
- **[README_API.md](README_API.md)** - Documentação completa
- **[EXEMPLOS_INTEGRACAO.md](EXEMPLOS_INTEGRACAO.md)** - Código em 10+ linguagens
- **[ARQUITETURA.md](ARQUITETURA.md)** - Como funciona
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Resolver problemas

---

## 📁 Arquivos Principais

```
📦 cardapio-api/
├── 📄 INDICE.md                    ⭐ COMECE AQUI
├── 🐍 api_cardapio.py              → API FastAPI
├── 🐍 build_cardapio_dinamico.py   → Motor de processamento (seu código)
├── 🐍 start_api.py                 → Inicializar API
├── 🐍 test_api_client.py           → Cliente de teste
├── 🌐 web_client.html              → Interface web
├── 📦 requirements_api.txt         → Dependências
└── 🪟 deploy_windows.bat           → Deploy automático
```

---

## ✅ Requisitos

- **Windows** (10/11 ou Server)
- **Python 3.8+**
- **CorelDRAW** instalado e licenciado

---

## 🎯 Uso Rápido

### Via Interface Web
1. Abra `web_client.html` no navegador
2. Faça upload do arquivo TXT
3. Baixe PDF/PNG/CDR

### Via cURL
```bash
curl -X POST "http://localhost:8000/cardapio/gerar" \
  -F "file=@teste_input.txt"
```

### Via Python
```python
import requests

with open('teste_input.txt', 'rb') as f:
    r = requests.post('http://localhost:8000/cardapio/gerar', 
                      files={'file': f})
print(r.json())
```

---

## 📋 Formato do Arquivo

```txt
RELATÓRIO DE PREÇOS Nome do Restaurante

*Categoria 1*
Item 1 - R$ 10,00
Item 2 - R$ 15,00

*Categoria 2*
Item 3 - R$ 20,00
```

---

## 🆘 Problemas?

Veja **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

Problemas comuns:
- CorelDRAW não inicializa → Execute como Admin
- Templates não encontrados → `python create_templates.py`
- Porta ocupada → Mude porta em `start_api.py`

---

## 🌐 Deploy em Produção

Azure / AWS / DigitalOcean:
1. Criar VM Windows Server
2. Instalar Python + CorelDRAW
3. Executar `deploy_windows.bat`
4. Configurar firewall (porta 8000)
5. Usar como serviço Windows (NSSM)

Detalhes: **[README_API.md](README_API.md)**

---

## 📞 Suporte

- 📖 Documentação completa: **[INDICE.md](INDICE.md)**
- 🐛 Bugs: GitHub Issues
- 💬 Dúvidas: suporte@exemplo.com

---

## 📄 Licença

MIT License

---

**Feito com ❤️ - Boa sorte! 🚀**
