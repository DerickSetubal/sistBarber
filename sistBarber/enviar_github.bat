@echo off
chcp 65001 > nul
title Enviando sistBarber para o GitHub

cd /d "%~dp0"
set PATH=C:\Program Files\Git\cmd;C:\Program Files\Git\bin;C:\Program Files\Git\ucrt64\bin;%PATH%

echo ============================================================
echo   💈 ENVIANDO PROJETO SISTBARBER PARA O GITHUB 💈
echo ============================================================
echo.

echo [1/2] Verificando status do Git...
git status
echo.
echo [2/2] Enviando branch main para https://github.com/DerickSetubal/sistBarber.git ...
echo Se abrir a janela do navegador, clique em "Authorize" para confirmar seu login.
echo.
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================================
    echo   ✅ ENVIADO COM SUCESSO PARA O GITHUB!
    echo   https://github.com/DerickSetubal/sistBarber
    echo ============================================================
) else (
    echo.
    echo [!] Ocorreu uma pendência. Se foi solicitado login, faça a autorização.
)

echo.
pause
