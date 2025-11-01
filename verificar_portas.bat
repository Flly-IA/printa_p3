@echo off
echo ============================================
echo VERIFICAR PORTAS 80 E 8000
echo ============================================
echo.

echo [1] Verificando o que esta rodando na porta 80...
netstat -ano | findstr :80
echo.

echo [2] Verificando o que esta rodando na porta 8000...
netstat -ano | findstr :8000
echo.

echo [3] Testando acesso local na porta 80...
curl http://localhost:80/ping
echo.

echo [4] Testando acesso local na porta 8000...
curl http://localhost:8000/ping
echo.

echo ============================================
echo ANALISE:
echo ============================================
echo Se porta 8000 funciona mas 80 nao:
echo   - API ainda esta na porta 8000
echo   - Precisa parar e reiniciar na porta 80
echo.
echo Se porta 80 mostra "Connection refused":
echo   - Porta 80 pode estar em uso por outro programa
echo   - Ou API nao conseguiu iniciar na porta 80
echo ============================================
pause
