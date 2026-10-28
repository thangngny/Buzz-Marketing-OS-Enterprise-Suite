# 🤖 AGENT DEPLOYMENT DIRECTIVE: BUZZ MARKETING OS FULL ENTERPRISE

> **DÀNH CHO CODING AGENT TRÊN MÁY TÍNH ĐÍCH (Target Machine)**  
> Bản chỉ thị này được biên soạn chuẩn theo cấu trúc định hướng cho Agent (Antigravity, Claude Code, OpenAI Codex, Cursor, Roo Code...).  
> Khi người dùng yêu cầu: *"Đọc kỹ rồi thực thi full cho tôi"*, hãy tuân theo quy trình chuẩn hóa dưới đây để hoàn tất việc cài đặt hệ thống tự động 100%.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ điều hành Buzz Marketing OS Full Enterprise gồm **3 TẦNG KẾT HỢP (DYNAMIC & PATH-AGNOSTIC)**:

```
+----------------------------------------------------------------------------------+
|                             BUZZ DESKTOP APPLICATION                             |
+----------------------------------------------------------------------------------+
        |                                       |                               |
        v                                       v                               v
+-----------------------+     +-------------------------------+     +--------------------+
|        TẦNG 1         |     |            TẦNG 2             |     |       TẦNG 3       |
|  COMMUNITY & ROSTER   |     |     CODEX ACCOUNT ROTATOR     |     |   MARKETING HUB    |
| (Nostr Relay Engine)  |     |   (Dynamic Multi-Account)     |     |    (MCP Server)    |
+-----------------------+     +-------------------------------+     +--------------------+
| * 28 Phòng ban chuẩn  |     | * Dynamic Pool (1-N accounts) |     | * FastMCP Server   |
| * 25 Agent chuyên gia |     | * Auto-failover & cooldown    |     | * Zoho CRM, Meta   |
| * respond_to: anyone  |     | * Tier routing (light/heavy)  |     | * TikTok, YouTube  |
| * Kind 10100 (Anyone) |     | * ACP Protocol JSON-RPC       |     | * LinkedIn Multi-  |
| * bypass-permissions  |     | * Thư mục ~/.codex/profiles/  |     |   Tier Controller  |
+-----------------------+     +-------------------------------+     +--------------------+
                                                |
                                                v
                               +---------------------------------+
                               |             TẦNG 4              |
                               |      BUZZ CUSTOM HARNESSES      |
                               | (codex-harness + marketing-hub) |
                               +---------------------------------+
```

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PRE-FLIGHT CHECKS)

Trước khi thực thi, hãy kiểm tra máy đích có các công cụ sau:
1. **Python 3.10+**: Kiểm tra bằng `python --version` (hoặc `py`, `python3`).
2. **Node.js 18+**: Kiểm tra bằng `node -v` và `npm -v`.
3. **Git**: Kiểm tra bằng `git --version`.
4. **Buzz Desktop App**: Đã cài đặt, thư mục `%APPDATA%\xyz.block.buzz.app` (hoặc macOS/Linux config) đã có sẵn hoặc sẽ khởi tạo khi chạy Buzz Desktop.

---

## 3. NGUYÊN TẮC LINH HOẠT CỦA BỘ XOAY TÀI KHOẢN (CODEX ROTATOR ENGINE)

1. **Khám phá tài khoản động (Dynamic Account Discovery)**:
   - Hệ thống **KHÔNG CỐ ĐỊNH** 3 tài khoản. Bất kỳ thư mục nào trong `~/.codex/profiles/` chứa tệp `auth.json` hợp lệ sẽ tự động được đưa vào danh sách xoay tua (Round-Robin).
   - Tên profile hỗ trợ mọi định dạng: `acc1`, `account-1`, `lina.ho`, `mkt-team`, `sales-01`... (không còn bị hạn chế bởi ký tự gạch nối `-`).
2. **Quản lý & Thêm mới tài khoản**:
   - Sử dụng lệnh: `node 02-Codex-Rotator/account-manager.js` hoặc chạy file `02-Codex-Rotator/Quan-Ly-Tai-Khoan.bat`.
   - Chọn `[A]` (Wizard liên hoàn) để đăng nhập tự động qua trình duyệt hoặc `[+]` để thêm tài khoản mới.
3. **Cơ chế Cooldown & Failover**:
   - Khi một tài khoản gặp Rate Limit 429 hoặc cạn token, hệ thống tự động cách ly tài khoản đó trong 30-60 phút và chuyển sang tài khoản kế tiếp trong pool mà không làm gián đoạn tác vụ người dùng.

---

## 4. QUY TRÌNH THỰC THI TOÀN DIỆN (EXECUTION WORKFLOW)

### CÁCH 1: Thực thi Tự Động Toàn Phần (Khuyên dùng cho Coding Agent)

Nếu người dùng đã cung cấp **Link Community** và **Mã khóa riêng tư (nsec)**:

```bash
python master_deploy.py --all --community-url "<COMMUNITY_URL>" --nsec "<OWNER_NSEC>"
```

Script sẽ tự động chạy liên hoàn:
1. **Tầng 2**: Cấu hình bộ xoay tài khoản Codex vào `~/.codex` và nạp harness.
2. **Tầng 3**: Dựng Marketing Hub MCP, cài đặt môi trường ảo `.venv`, tích hợp dịch vụ xuất bản LinkedIn đa tầng.
3. **Tầng 4**: Đăng ký các Harness `codex-harness.json` và `marketing-hub.json` vào Buzz Desktop.
4. **Tầng 1**: 
   - Đồng bộ 25 Chuyên gia AI (bao gồm Grokbot và Muse) vào `managed-agents.json` với chính sách `respond_to: anyone` và `start_on_app_launch: true`.
   - Mở toàn quyền thực thi `unlock_full_permissions.py` và ký phát sóng Nostr Kind 10100 lên Community Relay.
   - Bơm 28 phòng ban chuẩn vào Relay và đưa 25 bot vào túc trực.
5. **Nghiệm thu**: Tự động chạy `verify_system.py` (11/11 PASS) và `test_e2e_full.py` (6/6 PASS).

---

### CÁCH 2: Thực thi Chi Tiết Từng Tầng (Step-by-Step)

#### Bước 1: Triển khai Tầng 2 - Bộ Xoay Tài Khoản (Codex Rotator)
```bash
python 02-Codex-Rotator/setup_rotator.py
```

#### Bước 2: Triển khai Tầng 3 - Marketing System Hub (MCP Tools)
```bash
python 03-Marketing-Hub/setup_hub.py
```

#### Bước 3: Triển khai Tầng 4 - Custom Harnesses cho Buzz Desktop
```bash
python 04-Buzz-Harnesses/install_harnesses.py
```

#### Bước 4: Triển khai Tầng 1 - Đồng bộ Agent & Bơm Khung Community
```bash
# 1. Cài đặt Agent vào managed-agents.json với quyền anyone
python 01-Community-OS/setup_managed_agents.py --relay "<COMMUNITY_URL>"

# 2. Mở toàn quyền tương tác & phát sóng Kind 10100 lên Relay
python 01-Community-OS/unlock_full_permissions.py --relay "<COMMUNITY_URL>"

# 3. Xây dựng kênh và phân quyền bot trên Community Relay
python 01-Community-OS/inject_framework.py --url "<COMMUNITY_URL>" --nsec "<OWNER_NSEC>"
```

#### Bước 5: Kiểm Tra Chuẩn Đoán & Nghiệm Thu E2E
```bash
python verify_system.py
python test_e2e_full.py
```
* Tiêu chuẩn bàn giao hoàn hảo: **11/11 tiêu chí verify PASS** và **6/6 bài test E2E PASS**.
