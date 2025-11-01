@echo off
echo ============================================
echo TESTE DE ACESSO DIRETO - SEM CLOUDFLARE
echo ============================================
echo.

echo 1. Testando localhost na porta 80...
curl -v http://localhost/ping
echo.
echo ============================================
echo.

echo 2. Testando IP publico direto na porta 80...
echo URL: http://190.102.40.94/ping
curl -v http://190.102.40.94/ping
echo.
echo ============================================
echo.

echo 3. Testando dominio COM proxy Cloudflare...
echo URL: https://windows-printa.lucrativa.app/ping
curl -v https://windows-printa.lucrativa.app/ping
echo.
echo ============================================
echo.

echo RESULTADOS:
echo ============================================
echo Se localhost funcionou: API esta OK
echo Se IP direto funcionou: Firewall esta OK
echo Se dominio nao funcionou: Problema no Cloudflare
echo.
echo PROXIMAS ACOES:
echo - Verificar SSL/TLS no Cloudflare (deve ser Flexible)
echo - Verificar se proxy esta ATIVADO (nuvem laranja)
echo - Aguardar propagacao DNS (pode levar alguns minutos)
echo ============================================
pause
