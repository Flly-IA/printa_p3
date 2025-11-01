@echo off
echo ============================================
echo VERIFICAR STATUS DO FIREWALL - PORTA 80
echo ============================================
echo.

echo Verificando regras do firewall...
echo.

echo [1] Verificando regra "Printa API - HTTP"...
netsh advfirewall firewall show rule name="Printa API - HTTP" verbose
echo.

echo ============================================
echo [2] Verificando todas as regras da porta 80...
netsh advfirewall firewall show rule name=all | findstr /i "80"
echo.

echo ============================================
echo [3] Verificando status geral do firewall...
netsh advfirewall show allprofiles
echo.

echo ============================================
echo [4] Verificando quais processos estao usando porta 80...
netstat -ano | findstr :80
echo.

echo ============================================
pause
