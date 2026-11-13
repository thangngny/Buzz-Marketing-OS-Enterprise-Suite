#!/usr/bin/env python3
"""
Buzz Self-Healing Watchdog Engine
Tự động giám sát, phát hiện tiến trình Buzz Desktop / Agent bị tắt/crash và phục hồi ngay lập tức.
Tự động dọn dẹp các tiến trình con MCP/Python rò rỉ bộ nhớ (leak/zombies) để ngăn chặn lỗi OOM (Out Of Memory).
Chạy định kỳ qua Windows Task Scheduler.
"""
import os
import sys
import time
import subprocess
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOG_FILE = r"C:\Users\Admin\.buzz\watchdog.log"
BUZZ_EXE_DIR = r"D:\Buzz"
BUZZ_DESKTOP_EXE = r"D:\Buzz\buzz-desktop.exe"
AUTO_RESUME_SCRIPT = r"C:\Users\Admin\.buzz\tools\auto_resume_tasks.py"
PYTHON_EXE = sys.executable

TARGET_AGENT_COUNT = 23

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def is_process_running(process_name):
    try:
        output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {process_name}" /FO CSV /NH', shell=True).decode('utf-8', errors='ignore')
        return process_name.lower() in output.lower()
    except Exception:
        return False

def count_processes(process_name):
    try:
        output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {process_name}" /FO CSV /NH', shell=True).decode('utf-8', errors='ignore')
        lines = [l for l in output.strip().splitlines() if process_name.lower() in l.lower()]
        return len(lines)
    except Exception:
        return 0

def cleanup_zombies(force_all=False):
    """
    Dọn dẹp các tiến trình MCP Server Python, Codex, Node và Chrome Headless bị mồ côi (zombie)
    gây cạn kiệt RAM và Virtual Memory (Commit limit).
    """
    try:
        ps_script = """
        $allProcs = Get-CimInstance Win32_Process
        $procMap = @{}
        foreach ($p in $allProcs) { $procMap[$p.ProcessId] = $p }

        function Get-RootAncestor($procId) {
            $curr = $procId
            while ($procMap.ContainsKey($curr)) {
                $parent = $procMap[$curr].ParentProcessId
                if (-not $procMap.ContainsKey($parent)) { return $procMap[$curr] }
                $curr = $parent
            }
            return $null
        }

        $safeRoots = @("buzz-desktop.exe", "agy.exe", "explorer.exe")
        $targetNames = @("node.exe", "codex.exe", "codex-acp.exe", "chrome-headless-shell.exe")

        $reaped = 0
        foreach ($p in $allProcs) {
            if ($targetNames -contains $p.Name) {
                $shouldKill = $false
                if (-not $procMap.ContainsKey($p.ParentProcessId)) {
                    $shouldKill = $true
                } else {
                    $root = Get-RootAncestor $p.ProcessId
                    if ($root -and ($safeRoots -notcontains $root.Name)) {
                        $shouldKill = $true
                    }
                }

                if ($shouldKill) {
                    try {
                        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
                        $reaped++
                    } catch {}
                }
            }
        }

        # MCP Server Python cleanup
        $mcpProcs = $allProcs | Where-Object {
            ($_.Name -eq 'python.exe' -or $_.Name -eq 'python3.11.exe') -and
            ($_.CommandLine -like '*mcp_server*' -or $_.CommandLine -like '*server.py*' -or $_.CommandLine -like '*windows-control-mcp*' -or $_.CommandLine -like '*x-video-intelligence*' -or $_.CommandLine -like '*x-context-intelligence*')
        }
        if ($mcpProcs.Count -gt 15 -or $args[0] -eq 'True') {
            $mcpProcs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
            $reaped += $mcpProcs.Count
        }

        if ($reaped -gt 0) {
            Write-Host "Reaped $reaped orphaned/zombie processes (Node/Codex/Chrome/MCP)"
        }
        """
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script, str(force_all)], capture_output=True, text=True)
        if res.stdout.strip():
            log(f"🧹 {res.stdout.strip()}")
    except Exception as e:
        log(f"Lỗi khi dọn dẹp zombies: {e}")

def start_buzz_desktop():
    log("⚠️ Đang khởi động lại Buzz Desktop và toàn bộ Agent...")
    try:
        import ctypes
        from ctypes import wintypes
        class STARTUPINFO(ctypes.Structure):
            _fields_ = [
                ('cb', wintypes.DWORD), ('lpReserved', wintypes.LPWSTR), ('lpDesktop', wintypes.LPWSTR),
                ('lpTitle', wintypes.LPWSTR), ('dwX', wintypes.DWORD), ('dwY', wintypes.DWORD),
                ('dwXSize', wintypes.DWORD), ('dwYSize', wintypes.DWORD), ('dwXCountChars', wintypes.DWORD),
                ('dwYCountChars', wintypes.DWORD), ('dwFillAttribute', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                ('wShowWindow', wintypes.WORD), ('cbReserved2', wintypes.WORD), ('lpReserved2', ctypes.c_char_p),
                ('hStdInput', wintypes.HANDLE), ('hStdOutput', wintypes.HANDLE), ('hStdError', wintypes.HANDLE),
            ]
        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [('hProcess', wintypes.HANDLE), ('hThread', wintypes.HANDLE), ('dwProcessId', wintypes.DWORD), ('dwThreadId', wintypes.DWORD)]

        si = STARTUPINFO()
        si.cb = ctypes.sizeof(STARTUPINFO)
        si.lpDesktop = 'WinSta0\\Default'
        si.dwFlags = 1
        si.wShowWindow = 3
        pi = PROCESS_INFORMATION()
        flags = 0x01000000 # CREATE_BREAKAWAY_FROM_JOB
        cmd = f'"{BUZZ_DESKTOP_EXE}"'
        ok = ctypes.windll.kernel32.CreateProcessW(None, cmd, None, None, False, flags, None, BUZZ_EXE_DIR, ctypes.byref(si), ctypes.byref(pi))
        if not ok:
            ok = ctypes.windll.kernel32.CreateProcessW(None, cmd, None, None, False, 0, None, BUZZ_EXE_DIR, ctypes.byref(si), ctypes.byref(pi))
        
        log(f"✅ Đã khởi động Buzz Desktop thành công (PID: {pi.dwProcessId}).")
        ctypes.windll.kernel32.CloseHandle(pi.hProcess)
        ctypes.windll.kernel32.CloseHandle(pi.hThread)

        # Chờ 15s để ứng dụng kết nối Relay và load các Agent
        time.sleep(15)
        
        # Tự động chạy auto-resume engine
        if os.path.exists(AUTO_RESUME_SCRIPT):
            log("🔄 Đang chạy engine quét và phục hồi task dở dang...")
            subprocess.run([PYTHON_EXE, AUTO_RESUME_SCRIPT], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            log("✅ Phục hồi task dở dang hoàn tất.")
        return True
    except Exception as e:
        log(f"❌ Lỗi khi khởi động Buzz Desktop: {e}")
        return False

def check_and_heal():
    desktop_running = is_process_running("buzz-desktop.exe")
    acp_count = count_processes("buzz-acp.exe")
    
    # Kiểm tra rò rỉ tiến trình con
    cleanup_zombies(force_all=False)
    
    if not desktop_running:
        log("⚠️ PHÁT HIỆN BUZZ DESKTOP KHÔNG CHẠY!")
        cleanup_zombies(force_all=True)
        start_buzz_desktop()
    elif acp_count < TARGET_AGENT_COUNT:
        log(f"⚠️ PHÁT HIỆN THIẾU AGENT (Chỉ có {acp_count}/{TARGET_AGENT_COUNT} Agent live)! Đang tái khởi động Buzz Desktop...")
        try:
            subprocess.run("taskkill /F /IM buzz-desktop.exe", shell=True, capture_output=True)
            subprocess.run("taskkill /F /IM buzz-acp.exe", shell=True, capture_output=True)
            cleanup_zombies(force_all=True)
            time.sleep(2)
        except Exception as ex:
            log(f"Lỗi khi kill stale processes: {ex}")
        start_buzz_desktop()
    else:
        log(f"💚 Buzz Desktop đang hoạt động bình thường (Agents live: {acp_count}/{TARGET_AGENT_COUNT}).")
        
        # Best Practice 1: Kiểm tra ngưỡng RAM và tự động tối ưu nếu xuống dưới 1.5 GB
        try:
            ps_mem = "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"
            res_mem = subprocess.run(["powershell", "-NoProfile", "-Command", ps_mem], capture_output=True, text=True)
            free_kb = int(res_mem.stdout.strip() or 0)
            if free_kb < 1500000: # < 1.5 GB
                log(f"⚠️ RAM khả dụng đang thấp ({round(free_kb/1024, 1)} MB). Đang tự động kích hoạt RAM Guardian...")
                guardian_script = r"C:\Users\Admin\.buzz\tools\ram_guardian.ps1"
                if os.path.exists(guardian_script):
                    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", guardian_script], capture_output=True)
                    log("✅ Đã giải phóng RAM thành công.")
        except Exception as e_mem:
            log(f"Lỗi kiểm tra RAM: {e_mem}")

        # Best Practice 2: Quét và tự động phục hồi các tin nhắn / nhiệm vụ dở dang
        if os.path.exists(AUTO_RESUME_SCRIPT):
            try:
                subprocess.run([PYTHON_EXE, AUTO_RESUME_SCRIPT], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            except Exception as e_res:
                log(f"Lỗi chạy auto_resume: {e_res}")

def check_zalo_bridge():
    try:
        ps_cmd = 'Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*zalo_buzz_bridge.js*" } | Measure-Object | Select-Object -ExpandProperty Count'
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        count = int(res.stdout.strip() or 0)
        cred_file = r"C:\Users\Admin\.buzz\credentials\zalo_bot_credentials.json"
        bridge_script = r"C:\Users\Admin\.buzz\services\zalo-bot\zalo_buzz_bridge.js"
        if count == 0 and os.path.exists(cred_file) and os.path.exists(bridge_script):
            log("⚠️ Phát hiện Zalo-Buzz Bridge chưa chạy. Đang tự động khởi động...")
            subprocess.Popen(["node", bridge_script], creationflags=0x08000000)
        elif count > 0:
            log("🤖 Zalo-Buzz Bridge Daemon đang hoạt động bình thường.")
    except Exception as e:
        log(f"Lỗi khi kiểm tra Zalo Bridge: {e}")

if __name__ == "__main__":
    check_and_heal()
    check_zalo_bridge()
