# 🚀 GUIA DE INÍCIO RÁPIDO

## ⚡ Setup Rápido (5 minutos)

### 1. Descompactar arquivos
```bash
unzip cardapio_api_completo.zip
cd cardapio-api
```

### 2. Instalar (Windows)
```batch
deploy_windows.bat
```

### 3. Criar templates CorelDRAW
```bash
python create_templates.py
```
Mova `tplA.cdr` e `tplB.cdr` para a pasta `templates/`

### 4. Iniciar API
```batch
start_api.bat
```

### 5. Testar
- **Swagger**: http://localhost:8000/docs
- **Cliente Web**: Abra `web_client.html` no navegador
- **Cliente Python**: `python test_api_client.py`

---

## 📋 Checklist Rápido

- [ ] Python 3.8+ instalado
- [ ] CorelDRAW instalado e licenciado
- [ ] Dependências instaladas (`pip install -r requirements_api.txt`)
- [ ] Templates criados na pasta `templates/`
- [ ] API rodando (`python start_api.py`)

---

## 🔧 Uso Básico

### Via Web (Interface HTML)
1. Abra `web_client.html` no navegador
2. Selecione seu arquivo TXT
3. Escolha fonte e tamanho
4. Clique em "Gerar Cardápio"
5. Aguarde e baixe os arquivos

### Via cURL
```bash
curl -X POST "http://localhost:8000/cardapio/gerar" \
  -F "file=@teste_input.txt" \
  -F "font=Arial" \
  -F "font_size=10.0"
```

### Via Python
```python
import requests

with open('teste_input.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/cardapio/gerar',
        files={'file': f},
        data={'font': 'Arial', 'font_size': 10.0}
    )

job_id = response.json()['job_id']
print(f"Job ID: {job_id}")
```

---

## 🌐 Deploy em Produção

### Opção 1: Azure VM Windows
1. Criar VM Windows Server 2019/2022
2. Instalar Python + CorelDRAW
3. Clonar repositório
4. Executar `deploy_windows.bat`
5. Configurar como serviço Windows (use NSSM)
6. Abrir porta 8000 no firewall

### Opção 2: AWS EC2 Windows
Mesmo processo da Azure

### Opção 3: VPS Windows (Contabo, OVH)
Mesmo processo, mais barato

---

## 🆘 Problemas Comuns

### "CorelDRAW COM indisponível"
- Certifique-se de que o CorelDRAW está instalado
- Execute o CorelDRAW manualmente uma vez
- Verifique a licença

### "ModuleNotFoundError: No module named 'win32com'"
```bash
pip install pywin32
```

### "Templates não encontrados"
```bash
python create_templates.py
mkdir templates
move tplA.cdr templates\
move tplB.cdr templates\
```

### Porta 8000 já em uso
Altere a porta em `start_api.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📞 Suporte

- 📖 Documentação completa: `README_API.md`
- 🐛 Issues: GitHub
- 💬 Dúvidas: abra uma issue

---

## ✅ Resultado Esperado

Após seguir este guia, você terá:
- ✅ API rodando em `http://localhost:8000`
- ✅ Interface web funcional
- ✅ Geração automática de cardápios em PDF/PNG/CDR
- ✅ Sistema pronto para produção

**Tempo total: ~5-10 minutos**

---

**Boa sorte! 🎉**
