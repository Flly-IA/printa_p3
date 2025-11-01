@echo off
echo ============================================
echo TESTE DE CONECTIVIDADE - CLOUDFLARE
echo ============================================
echo.

echo 1. Testando API local...
curl -s http://localhost:8000/ping
if %errorlevel% equ 0 (
    echo [OK] API local respondendo
) else (
    echo [ERRO] API local nao respondendo
)
echo.

echo 2. Testando acesso externo (SEM porta)...
echo URL: https://windows-printa.lucrativa.app/ping
curl -s https://windows-printa.lucrativa.app/ping
echo.

echo 3. Testando DNS...
nslookup windows-printa.lucrativa.app
echo.

echo ============================================
echo PROXIMOS PASSOS:
echo ============================================
echo 1. Se API local OK mas externo falhou:
echo    - Verifique port forwarding no roteador
echo    - Porta 80 -^> [IP LOCAL]:8000
echo.
echo 2. Se "Invalid HTTP request":
echo    - NAO use :8000 na URL
echo    - Acesse: https://windows-printa.lucrativa.app/ping
echo.
echo 3. Cloudflare SSL/TLS:
echo    - Mode: Flexible
echo    - Proxy: ATIVADO (nuvem laranja)
echo ============================================
pause
