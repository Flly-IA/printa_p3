@echo off
echo ============================================
echo ABRINDO PORTA 80 NO FIREWALL DO WINDOWS
echo ============================================
echo.

echo Verificando se script esta rodando como Administrador...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR
    echo Clique com botao direito e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo [OK] Rodando como Administrador
echo.

echo Removendo regras antigas (se existirem)...
netsh advfirewall firewall delete rule name="Printa API - HTTP" >nul 2>&1
netsh advfirewall firewall delete rule name="Printa API - Port 8000" >nul 2>&1
echo.

echo Criando regra para porta 80 (HTTP)...
netsh advfirewall firewall add rule name="Printa API - HTTP" dir=in action=allow protocol=TCP localport=80
if %errorlevel% equ 0 (
    echo [OK] Porta 80 liberada no firewall
) else (
    echo [ERRO] Falha ao liberar porta 80
)
echo.

echo Criando regra para porta 8000 (API local)...
netsh advfirewall firewall add rule name="Printa API - Port 8000" dir=in action=allow protocol=TCP localport=8000
if %errorlevel% equ 0 (
    echo [OK] Porta 8000 liberada no firewall
) else (
    echo [ERRO] Falha ao liberar porta 8000
)
echo.

echo Verificando regras criadas...
netsh advfirewall firewall show rule name="Printa API - HTTP"
echo.
netsh advfirewall firewall show rule name="Printa API - Port 8000"
echo.

echo ============================================
echo PORTAS LIBERADAS NO FIREWALL!
echo ============================================
echo.
echo PROXIMOS PASSOS:
echo 1. Configure Port Forwarding no ROTEADOR
echo 2. Execute: CONFIGURAR_PORT_FORWARDING.bat
echo ============================================
pause
