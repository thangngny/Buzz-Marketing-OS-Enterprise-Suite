@echo off
chcp 65001 >nul
title Cài Đặt Khung Phòng Ban & Agent (Tầng 1)
cls

echo ================================================================================
echo           CÀI ĐẶT KHUNG PHÒNG BAN & AGENT MARKETING (TẦNG 1)
echo ================================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [LỖI] Máy tính chưa cài đặt Python! Vui lòng cài Python 3.10+ trước.
    pause
    exit /b 1
)

python inject_framework.py
pause
