@echo off
echo ============================================
echo SETUP CLOUDFLARE - windows-printa.lucrativa.app
echo ============================================
echo.

echo 1. VERIFICANDO SE A API ESTA RODANDO...
curl -s http://localhost:8000/ping > nul 2>&1
if %errorlevel% == 0 (
    echo [OK] API esta rodando localmente
) else (
    echo [ERRO] API NAO esta rodando!
    echo Execute: python api_cardapio.py
    pause
    exit /b 1
)

echo.
echo 2. IP DA VM:
ipconfig | findstr "IPv4" | findstr /v "127.0.0.1"

echo.
echo ============================================
echo PROXIMOS PASSOS:
echo ============================================
echo.
echo 1. CONFIGURAR PORT FORWARDING NO ROTEADOR:
echo    - Acesse o painel do roteador (192.168.1.1)
echo    - Port Forwarding:
echo      * Porta Externa: 80
echo      * IP Interno: [IP mostrado acima]
echo      * Porta Interna: 8000
echo      * Protocolo: TCP
echo.
echo 2. CONFIGURAR CLOUDFLARE:
echo    - Acesse: https://dash.cloudflare.com
echo    - SSL/TLS ^> Overview ^> Modo: Flexible
echo    - DNS ^> Proxy: ATIVADO (nuvem laranja)
echo.
echo 3. TESTAR:
echo    https://windows-printa.lucrativa.app/ping
echo.
echo ============================================
pause
