@echo off
echo ============================================
echo INICIAR API NA PORTA 80 - CLOUDFLARE
echo ============================================
echo.

echo Verificando se script esta rodando como Administrador...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR
    echo.
    echo Clique com botao direito no arquivo e selecione:
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Rodando como Administrador
echo.

echo Verificando se porta 80 esta liberada no firewall...
netsh advfirewall firewall show rule name="Printa API - HTTP" >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Porta 80 nao esta liberada no firewall
    echo Liberando porta 80...
    netsh advfirewall firewall add rule name="Printa API - HTTP" dir=in action=allow protocol=TCP localport=80
    echo [OK] Porta 80 liberada
) else (
    echo [OK] Porta 80 ja esta liberada no firewall
)
echo.

echo Mudando para diretorio do projeto...
cd /d "%~dp0"
echo Diretorio atual: %CD%
echo.

echo Parando processos Python que podem estar usando a porta...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo.

echo ============================================
echo INICIANDO API NA PORTA 80
echo ============================================
echo.
echo URL Local: http://localhost/ping
echo URL Cloudflare: https://windows-printa.lucrativa.app/ping
echo.
echo Pressione Ctrl+C para parar
echo ============================================
echo.

python api_cardapio.py --port 80

echo.
echo ============================================
echo API PAROU
echo ============================================
pause
