@echo off
chcp 65001 >nul
title Quản Lý Tài Khoản Codex & Xoay Tua
cls

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [LỖI] Chưa tìm thấy Node.js trong hệ thống! Vui lòng cài đặt Node.js trước.
    pause
    exit /b 1
)

node "%~dp0account-manager.js"
pause
