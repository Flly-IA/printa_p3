@echo off
echo ============================================
echo INFORMACOES DE REDE
echo ============================================
echo.
echo IP da maquina:
ipconfig | findstr /i "IPv4"
echo.
echo ============================================
echo Porta da API: 8000
echo URL local: http://localhost:8000
echo.
echo Para acessar externamente, use:
echo http://SEU_IP:8000
echo ============================================
pause
