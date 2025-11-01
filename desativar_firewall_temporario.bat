@echo off
echo ============================================
echo DESATIVAR FIREWALL TEMPORARIAMENTE - TESTE
echo ============================================
echo.
echo ATENCAO: Isso vai DESATIVAR o firewall do Windows
echo Apenas para TESTE de conectividade
echo.
echo Pressione Ctrl+C para CANCELAR
pause
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

echo Desativando firewall em todos os perfis...
netsh advfirewall set allprofiles state off
echo.

if %errorlevel% equ 0 (
    echo [OK] Firewall DESATIVADO
    echo.
    echo ============================================
    echo AGORA TESTE:
    echo ============================================
    echo 1. curl http://localhost/ping
    echo 2. curl http://190.102.40.94/ping
    echo 3. https://windows-printa.lucrativa.app/ping
    echo.
    echo ============================================
    echo IMPORTANTE: Execute reativar_firewall.bat depois!
    echo ============================================
) else (
    echo [ERRO] Falha ao desativar firewall
)

pause
