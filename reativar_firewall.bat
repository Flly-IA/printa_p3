@echo off
echo ============================================
echo REATIVAR FIREWALL DO WINDOWS
echo ============================================
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

echo Reativando firewall em todos os perfis...
netsh advfirewall set allprofiles state on
echo.

if %errorlevel% equ 0 (
    echo [OK] Firewall REATIVADO
    echo.
    echo Agora vamos adicionar a regra correta para porta 80...
    echo.

    echo Removendo regras antigas...
    netsh advfirewall firewall delete rule name="Printa API - HTTP" >nul 2>&1
    echo.

    echo Criando regra para porta 80...
    netsh advfirewall firewall add rule name="Printa API - HTTP" dir=in action=allow protocol=TCP localport=80

    if %errorlevel% equ 0 (
        echo [OK] Regra criada com sucesso
    ) else (
        echo [ERRO] Falha ao criar regra
    )
) else (
    echo [ERRO] Falha ao reativar firewall
)

echo.
pause
