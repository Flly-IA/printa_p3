@echo off
echo ============================================
echo ABRINDO PORTA 8000 NO FIREWALL DO WINDOWS
echo ============================================
echo.
echo Este script requer privilegios de administrador!
echo.

REM Remover regras antigas (se existirem)
netsh advfirewall firewall delete rule name="API Cardapio - Porta 8000" >nul 2>&1

REM Adicionar regra de entrada (permitir conexões externas)
netsh advfirewall firewall add rule name="API Cardapio - Porta 8000" dir=in action=allow protocol=TCP localport=8000

echo.
echo ============================================
echo REGRA DE FIREWALL CRIADA COM SUCESSO!
echo ============================================
echo.
echo A porta 8000 agora aceita conexoes externas.
echo.
echo Para testar, acesse de outra maquina:
echo http://IP_DA_VM:8000
echo.
pause
