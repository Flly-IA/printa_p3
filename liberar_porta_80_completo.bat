@echo off
echo ============================================
echo LIBERAR PORTA 80 - VERSAO COMPLETA
echo ============================================
echo.

echo Verificando se script esta rodando como Administrador...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR
    echo.
    echo Clique com botao direito e selecione:
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Rodando como Administrador
echo.

echo ============================================
echo PASSO 1: Remover regras antigas
echo ============================================
netsh advfirewall firewall delete rule name="Printa API - HTTP"
netsh advfirewall firewall delete rule name="Printa API - Port 8000"
netsh advfirewall firewall delete rule name=all protocol=TCP localport=80
echo.

echo ============================================
echo PASSO 2: Criar regra INBOUND (Entrada)
echo ============================================
netsh advfirewall firewall add rule name="Printa API - HTTP" dir=in action=allow protocol=TCP localport=80 enable=yes profile=any
if %errorlevel% equ 0 (
    echo [OK] Regra INBOUND criada
) else (
    echo [ERRO] Falha ao criar regra INBOUND
)
echo.

echo ============================================
echo PASSO 3: Criar regra OUTBOUND (Saida) - opcional
echo ============================================
netsh advfirewall firewall add rule name="Printa API - HTTP OUT" dir=out action=allow protocol=TCP localport=80 enable=yes profile=any
if %errorlevel% equ 0 (
    echo [OK] Regra OUTBOUND criada
) else (
    echo [ERRO] Falha ao criar regra OUTBOUND
)
echo.

echo ============================================
echo PASSO 4: Verificar regras criadas
echo ============================================
netsh advfirewall firewall show rule name="Printa API - HTTP"
echo.

echo ============================================
echo PASSO 5: Testar porta 80
echo ============================================
echo Testando se algo esta rodando na porta 80...
netstat -ano | findstr :80
echo.

echo ============================================
echo CONCLUIDO!
echo ============================================
echo.
echo Proximos passos:
echo 1. Certifique-se que a API esta rodando: iniciar_api_porta_80.bat
echo 2. Teste local: curl http://localhost/ping
echo 3. Teste IP: curl http://190.102.40.94/ping
echo.
pause
