@echo off
chcp 65001 >nul
echo ================================================================================
echo    BUZZ MARKETING OS - TRIỂN KHAI 23 AGENTS LÊN COMMUNITY RELAY
echo ================================================================================
echo.

set /p RELAY_URL="Nhập Relay URL (Để trống để lấy mặc định): "
set /p INVITE_CODE="Nhập Mã mời Community (Invite Code nếu có): "

set CMD=python deploy_official_agents.py
if not "%RELAY_URL%"=="" set CMD=%CMD% --relay "%RELAY_URL%"
if not "%INVITE_CODE%"=="" set CMD=%CMD% --invite "%INVITE_CODE%"

echo.
echo [*] Đang khởi chạy tiến trình triển khai...
%CMD%

echo.
pause
