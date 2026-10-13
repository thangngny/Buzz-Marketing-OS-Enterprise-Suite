@echo off
chcp 65001 >nul
title CAI DAT 23 AGENT VAO BUZZ DESKTOP
color 0B

echo ======================================================================
echo    BUZZ MARKETING AI OS - CAI DAT 23 CHUYEN GIA VAO BUZZ DESKTOP
echo ======================================================================
echo.
echo Script se tu dong dong bo 23 Agent va Team vao Buzz Desktop.
echo Khong lo loi file import hay sai format UI.
echo.

python setup_managed_agents.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Khong tim thay Python mac dinh, dang thu bang Python cua he thong...
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" setup_managed_agents.py
)

echo.
echo Nhan phim bat ky de thoat...
pause >nul
