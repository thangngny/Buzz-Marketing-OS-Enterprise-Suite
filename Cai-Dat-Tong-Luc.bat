@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Triển Khai Toàn Diện Buzz Marketing OS Full Enterprise
cls

echo ================================================================================
echo           HỆ ĐIỀU HÀNH MARKETING AI (BUZZ MARKETING OS FULL ENTERPRISE)
echo ================================================================================
echo.

set PYTHON_CMD=

:: Kiểm tra python từ môi trường ảo nếu có
if exist "%USERPROFILE%\marketing-ai-system\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\marketing-ai-system\.venv\Scripts\python.exe"
    goto RUN
)
if exist "C:\Users\Admin\marketing-ai-system\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=C:\Users\Admin\marketing-ai-system\.venv\Scripts\python.exe"
    goto RUN
)

:: Kiểm tra python từ PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto RUN
)

:: Kiểm tra py launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto RUN
)

echo [LỖI] Chưa tìm thấy Python trên máy tính này!
echo Vui lòng cài đặt Python 3.10+ (tích chọn 'Add Python to PATH') trước khi chạy.
echo Tải tại: https://www.python.org/downloads/
echo.
pause
exit /b 1

:RUN
"%PYTHON_CMD%" "%~dp0master_deploy.py"
pause
