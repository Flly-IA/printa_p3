# 🔧 TROUBLESHOOTING COMPLETO

Soluções para problemas comuns e diagnóstico de erros.

---

## 🚨 Problemas Comuns

### 1. CorelDRAW não inicializa

#### Erro: "CorelDRAW COM indisponível"

**Causas possíveis:**
- CorelDRAW não instalado
- Licença expirada
- Permissões insuficientes
- DLLs não registradas

**Soluções:**

✅ **Verificar instalação**
```bash
# Verificar se está instalado
dir "C:\Program Files\Corel"
```

✅ **Executar manualmente**
```bash
# Abrir CorelDRAW uma vez para ativar licença
"C:\Program Files\Corel\CorelDRAW Graphics Suite 2021\Programs64\CorelDRW.exe"
```

✅ **Registrar DLLs**
```bash
cd "C:\Program Files\Corel\CorelDRAW Graphics Suite 2021\Programs64"
regsvr32 CorelDRW.exe /s
```

✅ **Executar como Administrador**
```bash
# Clicar com botão direito em start_api.bat
# "Executar como administrador"
```

✅ **Verificar versões disponíveis**
```python
import win32com.client

# Tentar versões diferentes
for version in [24, 25, 26]:
    try:
        app = win32com.client.Dispatch(f"CorelDRAW.Application.{version}")
        print(f"✅ Versão {version} disponível")
        app.Quit()
    except:
        print(f"❌ Versão {version} não disponível")
```

---

### 2. Módulo não encontrado

#### Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução:**
```bash
pip install -r requirements_api.txt
```

#### Erro: "ModuleNotFoundError: No module named 'win32com'"

**Solução:**
```bash
pip install pywin32
# OU
pip install pywin32==306
```

Se ainda falhar:
```bash
python -m pip install --upgrade pywin32
python Scripts\pywin32_postinstall.py -install
```

---

### 3. Templates não encontrados

#### Erro: "Templates CDR não encontrados"

**Solução:**
```bash
# 1. Criar templates
python create_templates.py

# 2. Criar pasta templates
mkdir templates

# 3. Mover arquivos
move tplA.cdr templates\
move tplB.cdr templates\

# 4. Verificar
dir templates\
```

**Estrutura esperada:**
```
cardapio-api/
├── templates/
│   ├── tplA.cdr  ✅
│   └── tplB.cdr  ✅
```

---

### 4. Porta já em uso

#### Erro: "OSError: [Errno 98] Address already in use"

**Verificar processos:**
```bash
# Windows
netstat -ano | findstr :8000

# Matar processo
taskkill /PID <PID> /F
```

**Usar outra porta:**
```python
# Em start_api.py, alterar:
uvicorn.run(app, host="0.0.0.0", port=8001)  # <-- Mudar porta
```

---

### 5. Erro ao processar arquivo

#### Erro: "Erro ao salvar arquivo: [WinError 123]"

**Causa:** Caminho inválido ou caracteres especiais

**Solução:**
```python
# Usar Path.absolute() e converter para string
from pathlib import Path

path = Path("arquivo.cdr").absolute()
path_str = str(path).replace('/', '\\')  # Windows precisa de \
```

#### Erro: "Arquivo não encontrado: teste_input.txt"

**Solução:**
```bash
# Verificar caminho relativo
python -c "import os; print(os.getcwd())"

# Ou usar caminho absoluto
python api_cardapio.py --input "C:\Users\...\teste_input.txt"
```

---

### 6. Timeout no processamento

#### Erro: "Timeout excedido"

**Causas:**
- Cardápio muito grande
- CorelDRAW travado
- Recursos insuficientes

**Soluções:**

✅ **Aumentar timeout**
```python
# Em test_api_client.py
def wait_for_completion(job_id, timeout=600):  # 10 minutos
    ...
```

✅ **Verificar recursos**
```bash
# Windows - Gerenciador de Tarefas
# Verificar uso de CPU/RAM
```

✅ **Reiniciar CorelDRAW**
```bash
taskkill /IM CorelDRW.exe /F
```

---

### 7. Fontes não encontradas

#### Erro: "Font 'MinhaFonte' not found"

**Solução:**
```bash
# 1. Verificar fontes instaladas no Windows
control fonts

# 2. Usar fontes do sistema
# Arial, Times New Roman, Calibri, Verdana
```

**Listar fontes disponíveis:**
```python
import matplotlib.font_manager
fonts = matplotlib.font_manager.findSystemFonts()
for font in fonts:
    print(font)
```

---

### 8. Erros de permissão

#### Erro: "PermissionError: [WinError 5] Acesso negado"

**Soluções:**

✅ **Executar como Admin**
```bash
# Botão direito → "Executar como administrador"
```

✅ **Liberar pasta**
```bash
# Propriedades → Segurança → Editar
# Adicionar permissões completas para seu usuário
```

✅ **Desabilitar antivírus temporariamente**
```bash
# Alguns antivírus bloqueiam automação COM
```

---

### 9. Erro ao exportar PDF/PNG

#### Erro: "Export failed"

**Causas:**
- Caminho inválido
- Espaço em disco insuficiente
- Codecs faltando

**Soluções:**

✅ **Verificar espaço em disco**
```bash
wmic logicaldisk get size,freespace,caption
```

✅ **Usar caminho absoluto**
```python
output_path = Path("C:/temp/output.pdf").absolute()
doc.PublishToPDF(str(output_path).replace('/', '\\'))
```

✅ **Instalar codecs**
```bash
# Baixar K-Lite Codec Pack
# https://codecguide.com/download_kl.htm
```

---

### 10. API não responde

#### Problema: Servidor não inicia

**Diagnóstico:**
```bash
# 1. Verificar logs
python start_api.py

# 2. Verificar processo
tasklist | findstr python

# 3. Verificar porta
netstat -ano | findstr :8000
```

**Soluções:**

✅ **Verificar erros de sintaxe**
```bash
python -m py_compile api_cardapio.py
```

✅ **Reinstalar dependências**
```bash
pip uninstall -y -r requirements_api.txt
pip install -r requirements_api.txt
```

✅ **Usar modo debug**
```python
# Em start_api.py
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, debug=True)
```

---

## 🔍 Diagnóstico Sistemático

### Checklist de Diagnóstico

Execute este script para diagnóstico completo:

```python
# diagnostic.py
import sys
import platform
from pathlib import Path

def diagnosticar():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO SISTEMA")
    print("=" * 60)
    print()
    
    # Sistema
    print("1️⃣ Sistema Operacional")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Versão: {platform.version()}")
    print(f"   Arquitetura: {platform.machine()}")
    print()
    
    # Python
    print("2️⃣ Python")
    print(f"   Versão: {sys.version}")
    print(f"   Executável: {sys.executable}")
    print()
    
    # Módulos
    print("3️⃣ Módulos Python")
    modulos = ['fastapi', 'uvicorn', 'pydantic', 'win32com']
    for modulo in modulos:
        try:
            __import__(modulo)
            print(f"   ✅ {modulo}")
        except ImportError:
            print(f"   ❌ {modulo} - NÃO INSTALADO")
    print()
    
    # CorelDRAW
    print("4️⃣ CorelDRAW")
    try:
        import win32com.client
        app = win32com.client.Dispatch("CorelDRAW.Application")
        print(f"   ✅ CorelDRAW disponível")
        print(f"   Versão: {app.Version}")
        app.Quit()
    except Exception as e:
        print(f"   ❌ CorelDRAW não disponível: {e}")
    print()
    
    # Templates
    print("5️⃣ Templates")
    templates_dir = Path("templates")
    if templates_dir.exists():
        tplA = templates_dir / "tplA.cdr"
        tplB = templates_dir / "tplB.cdr"
        
        print(f"   {'✅' if tplA.exists() else '❌'} tplA.cdr")
        print(f"   {'✅' if tplB.exists() else '❌'} tplB.cdr")
    else:
        print(f"   ❌ Pasta templates não encontrada")
    print()
    
    # Pastas
    print("6️⃣ Estrutura de Pastas")
    pastas = ['templates', 'outputs', 'temp']
    for pasta in pastas:
        p = Path(pasta)
        print(f"   {'✅' if p.exists() else '❌'} {pasta}/")
    print()
    
    # Arquivo de entrada
    print("7️⃣ Arquivo de Teste")
    teste = Path("teste_input.txt")
    if teste.exists():
        print(f"   ✅ teste_input.txt ({teste.stat().st_size} bytes)")
    else:
        print(f"   ❌ teste_input.txt não encontrado")
    print()
    
    print("=" * 60)
    print("FIM DO DIAGNÓSTICO")
    print("=" * 60)

if __name__ == "__main__":
    diagnosticar()
```

**Executar:**
```bash
python diagnostic.py
```

---

## 📊 Logs e Debugging

### Habilitar logs detalhados

```python
# No início de api_cardapio.py
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Ou INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_debug.log"),
        logging.StreamHandler()
    ]
)
```

### Logs do CorelDRAW

```python
def process_cardapio_com_logs(job_id, input_path, config):
    logger.info(f"[{job_id}] Iniciando processamento")
    
    try:
        logger.debug(f"[{job_id}] Abrindo template...")
        doc = corel.OpenDocument(tpl)
        logger.debug(f"[{job_id}] Template aberto: {doc.Name}")
        
        logger.debug(f"[{job_id}] Página: {page.SizeWidth}x{page.SizeHeight}")
        
        # ... resto do código
        
    except Exception as e:
        logger.error(f"[{job_id}] ERRO: {str(e)}", exc_info=True)
        raise
```

---

## 🧪 Testes Unitários

### Testar componentes individualmente

```python
# test_components.py
def test_parse_txt():
    from build_cardapio_dinamico import parse_txt
    from pathlib import Path
    
    result = parse_txt(Path("teste_input.txt"))
    
    assert result['restaurant'] == "Bar Parada obrigatoria"
    assert result['model'] in ['A', 'B']
    assert len(result['categories']) > 0
    print("✅ parse_txt OK")

def test_corel_com():
    import win32com.client
    
    app = win32com.client.Dispatch("CorelDRAW.Application")
    app.Visible = False
    print(f"✅ CorelDRAW {app.Version} OK")
    app.Quit()

def test_api_health():
    import requests
    
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    print("✅ API Health OK")

if __name__ == "__main__":
    test_parse_txt()
    test_corel_com()
    test_api_health()
```

---

## 🔄 Reset Completo

Se nada funcionar, faça um reset:

```bash
# 1. Parar todos os processos
taskkill /IM python.exe /F
taskkill /IM CorelDRW.exe /F

# 2. Limpar cache
rmdir /s /q outputs
rmdir /s /q temp
rmdir /s /q __pycache__

# 3. Recriar pastas
mkdir outputs
mkdir temp

# 4. Reinstalar dependências
pip uninstall -r requirements_api.txt -y
pip install -r requirements_api.txt

# 5. Recriar templates
python create_templates.py

# 6. Testar
python start_api.py
```

---

## 📞 Suporte Avançado

### Coletar informações para suporte

```bash
# Gerar relatório completo
python diagnostic.py > relatorio.txt 2>&1
python -m pip list >> relatorio.txt

# Anexar logs
type api_debug.log >> relatorio.txt
```

### Contato

- 🐛 Issues no GitHub
- 📧 Email de suporte
- 💬 Fórum da comunidade

---

## ✅ Checklist de Verificação

Antes de reportar um problema, verifique:

- [ ] Python 3.8+ instalado
- [ ] Todas as dependências instaladas
- [ ] CorelDRAW instalado e licenciado
- [ ] Templates na pasta `templates/`
- [ ] Pastas `outputs/` e `temp/` existem
- [ ] Porta 8000 disponível
- [ ] Executando como Administrador (se necessário)
- [ ] Antivírus não bloqueando
- [ ] Espaço em disco suficiente (> 1GB)
- [ ] Arquivo de entrada no formato correto

---

**Se o problema persistir após todas as tentativas, abra uma issue detalhada! 🆘**
