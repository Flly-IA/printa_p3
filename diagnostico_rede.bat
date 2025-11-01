@echo off
chcp 65001 > nul
echo ============================================
echo DIAGNÓSTICO COMPLETO DE REDE
echo ============================================
echo.

echo 1. TODOS OS ENDEREÇOS IP:
echo ----------------------------------------
ipconfig | findstr /i "IPv4 Ethernet Wi-Fi Adaptador"
echo.

echo 2. INFORMAÇÕES DETALHADAS:
echo ----------------------------------------
ipconfig /all | findstr /i "IPv4 Gateway Máscara"
echo.

echo 3. TESTANDO SE A API ESTÁ RESPONDENDO LOCALMENTE:
echo ----------------------------------------
curl -s http://localhost:8000/ping > nul 2>&1
if %errorlevel% == 0 (
    echo ✅ API está respondendo no localhost:8000
    curl -s http://localhost:8000/ping
) else (
    echo ❌ API NÃO está respondendo no localhost:8000
    echo    Verifique se você executou: python api_cardapio.py
)
echo.

echo 4. PORTAS ABERTAS:
echo ----------------------------------------
netstat -ano | findstr ":8000"
echo.

echo 5. REGRAS DE FIREWALL PARA PORTA 8000:
echo ----------------------------------------
netsh advfirewall firewall show rule name="API Cardapio - Porta 8000"
echo.

echo ============================================
echo RESUMO:
echo ============================================
echo.
echo Se você viu IPs como 192.168.x.x ou 10.x.x.x acima,
echo use um DESSES para acessar externamente, não o 190.x.x.x
echo.
echo Exemplo: http://192.168.1.100:8000/docs
echo.
echo ============================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
