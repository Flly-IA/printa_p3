@echo off
echo ============================================
echo DESCOBRIR IP LOCAL DA VM
echo ============================================
echo.

echo Procurando endereco IP local...
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo IP encontrado: !IP!
)

echo.
echo ============================================
echo IMPORTANTE:
echo ============================================
echo.
echo Use o IP que comece com:
echo   - 192.168.x.x  (mais comum)
echo   - 10.x.x.x
echo   - 172.16.x.x ate 172.31.x.x
echo.
echo NAO use:
echo   - 127.0.0.1 (localhost)
echo   - 169.254.x.x (erro de DHCP)
echo.
echo ============================================
echo CONFIGURACAO PORT FORWARDING:
echo ============================================
echo.
echo No painel do roteador (192.168.1.1):
echo.
echo   Porta Externa: 80
echo   IP Interno: [IP LOCAL acima]
echo   Porta Interna: 8000
echo   Protocolo: TCP
echo.
echo ============================================

ipconfig

echo.
pause
