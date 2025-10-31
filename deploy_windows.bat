@echo off
REM deploy_windows.bat
REM Script de deploy para Windows Server/Desktop

echo ========================================
echo   DEPLOY API CARDAPIO DINAMICO
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ de https://python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] pip nao encontrado!
    pause
    exit /b 1
)

echo [OK] pip encontrado
echo.

REM Instalar dependências
echo [1/5] Instalando dependencias...
pip install -r requirements_api.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Verificar pasta templates
echo [2/5] Verificando templates...
if not exist "templates\" (
    echo [AVISO] Pasta templates nao encontrada. Criando...
    mkdir templates
)

if not exist "templates\tplA.cdr" (
    echo [AVISO] Template A nao encontrado!
    echo Execute: python create_templates.py
    echo Depois mova os arquivos para a pasta templates\
)

if not exist "templates\tplB.cdr" (
    echo [AVISO] Template B nao encontrado!
    echo Execute: python create_templates.py
    echo Depois mova os arquivos para a pasta templates\
)

if exist "templates\tplA.cdr" (
    echo [OK] Template A encontrado
)

if exist "templates\tplB.cdr" (
    echo [OK] Template B encontrado
)
echo.

REM Criar pastas necessárias
echo [3/5] Criando estrutura de pastas...
if not exist "outputs\" mkdir outputs
if not exist "temp\" mkdir temp
echo [OK] Pastas criadas
echo.

REM Verificar CorelDRAW
echo [4/5] Verificando CorelDRAW...
python -c "import win32com.client; win32com.client.Dispatch('CorelDRAW.Application')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] CorelDRAW COM disponivel
) else (
    echo [AVISO] CorelDRAW pode nao estar acessivel via COM
    echo Certifique-se de que o CorelDRAW esta instalado
)
echo.

REM Criar atalho para iniciar API
echo [5/5] Criando atalhos...
echo @echo off > start_api.bat
echo cd /d %%~dp0 >> start_api.bat
echo python start_api.py >> start_api.bat
echo [OK] Atalho criado: start_api.bat
echo.

echo ========================================
echo   DEPLOY CONCLUIDO!
echo ========================================
echo.
echo Proximos passos:
echo   1. Execute: start_api.bat
echo   2. Acesse: http://localhost:8000/docs
echo   3. Teste: python test_api_client.py
echo.
echo Para criar templates:
echo   python create_templates.py
echo   move tplA.cdr templates\
echo   move tplB.cdr templates\
echo.

pause
