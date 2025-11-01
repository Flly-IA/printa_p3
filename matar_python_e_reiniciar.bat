@echo off
echo ============================================
echo MATAR TODOS OS PROCESSOS PYTHON E REINICIAR
echo ============================================
echo.

echo Verificando se script esta rodando como Administrador...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR
    pause
    exit /b 1
)

echo [OK] Rodando como Administrador
echo.

echo [1] Verificando processos Python rodando...
echo.
tasklist | findstr python.exe
echo.

echo [2] Matando TODOS os processos Python...
taskkill /F /IM python.exe /T
timeout /t 2 /nobreak >nul
echo.

echo [3] Verificando se porta 80 esta livre...
netstat -ano | findstr :80
echo.

echo [4] Verificando se porta 8000 esta livre...
netstat -ano | findstr :8000
echo.

echo ============================================
echo PORTAS LIMPAS!
echo ============================================
echo.
echo Mudando para diretorio do projeto...
cd /d "%~dp0"
echo Diretorio: %CD%
echo.

echo ============================================
echo INICIANDO API NA PORTA 80
echo ============================================
echo.
echo URL Local: http://localhost/ping
echo URL IP: http://190.102.40.94/ping
echo URL Cloudflare: https://windows-printa.lucrativa.app/ping
echo.
echo Pressione Ctrl+C para parar
echo ============================================
echo.

python api_cardapio.py --port 80
