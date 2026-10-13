# 🤖 AGENT DEPLOYMENT DIRECTIVE: BUZZ MARKETING OS FULL ENTERPRISE

> **DÀNH CHO CODING AGENT TRÊN MÁY TÍNH ĐÍCH (Target Machine)**  
> Bản chỉ thị này được biên soạn chuẩn theo cấu trúc định hướng cho Agent (Antigravity, Claude Code, OpenAI Codex, Cursor, Roo Code...).  
> Khi người dùng yêu cầu: *"Đọc kỹ rồi thực thi full cho tôi"*, hãy tuân theo quy trình chuẩn hóa dưới đây để hoàn tất việc cài đặt hệ thống tự động 100%.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ điều hành Buzz Marketing OS Full Enterprise gồm **3 TẦNG KẾT HỢP**:

```
+----------------------------------------------------------------------------------+
|                             BUZZ DESKTOP APPLICATION                             |
+----------------------------------------------------------------------------------+
        |                                       |                               |
        v                                       v                               v
+-----------------------+     +-------------------------------+     +--------------------+
|        TẦNG 1         |     |            TẦNG 2             |     |       TẦNG 3       |
|  COMMUNITY & ROSTER   |     |     CODEX ACCOUNT ROTATOR     |     |   MARKETING HUB    |
| (Nostr Relay Engine)  |     |   (Load Balancing & Quotas)   |     |    (MCP Server)    |
+-----------------------+     +-------------------------------+     +--------------------+
| * 28 Phòng ban chuẩn  |     | * Multi-account pool (3 accs) |     | * FastMCP Server   |
| * 25 Agent chuyên gia |     | * Auto-failover & cooldown    |     | * Zoho CRM, Meta   |
| * SOP & Prompt chuẩn  |     | * ACP Protocol JSON-RPC       |     | * TikTok, YouTube  |
| * 700+ memberships    |     | * Thư mục ~/.codex/profiles/  |     | * Google Drive     |
+-----------------------+     +-------------------------------+     +--------------------+
```

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PRE-FLIGHT CHECKS)

Trước khi thực thi, hãy kiểm tra máy đích có các công cụ sau:
1. **Python 3.10+**: Kiểm tra bằng `python --version`. Nếu máy Windows trỏ vào Windows Store alias, hãy tìm python thật trong `%LOCALAPPDATA%\Programs\Python` hoặc thông qua virtualenv.
2. **Node.js 18+**: Kiểm tra bằng `node -v` và `npm -v`.
3. **Git**: Kiểm tra bằng `git --version`.
4. **Buzz Desktop App**: Đã cài đặt, kiểm tra xem thư mục `%APPDATA%\xyz.block.buzz.app` có tồn tại.

---

## 3. QUY TRÌNH THỰC THI TOÀN DIỆN (EXECUTION WORKFLOW)

### CÁCH 1: Thực thi Tự Động Toàn Phần (Khuyên dùng cho Agent)

Nếu người dùng đã cung cấp **Link Community** và **Mã khóa riêng tư (nsec)**, Agent hãy chạy lệnh:

```bash
python master_deploy.py --all --community-url "<COMMUNITY_URL>" --nsec "<OWNER_NSEC>"
```

### CÁCH 2: Thực thi Chi Tiết Từng Tầng (Step-by-Step)

Nếu muốn kiểm soát từng tầng hoặc xử lý ngoại lệ:

#### Bước 1: Triển khai Tầng 2 - Bộ Xoay Tài Khoản (Codex Rotator)
```bash
python 02-Codex-Rotator/setup_rotator.py
```
* **Nhiệm vụ tự động hoàn thành:**
  * Khởi tạo `~/.codex/scripts` và `~/.codex/profiles`.
  * Sao chép `codex-rotator.js` và `codex-acp-rotator.js` (bản dynamic path).
  * Chuẩn bị thư viện `@agentclientprotocol/codex-acp` trong `%APPDATA%\Buzz\node-tools`.
  * Đăng ký Harness `codex-harness.json` vào `%APPDATA%\xyz.block.buzz.app\custom_harnesses\`.

#### Bước 2: Triển khai Tầng 3 - Marketing System Hub (MCP Tools)
```bash
python 03-Marketing-Hub/setup_hub.py
```
* **Nhiệm vụ tự động hoàn thành:**
  * Clone mã nguồn từ `https://github.com/thangngny/marketing-ai-system.git` về `~/marketing-ai-system`.
  * Tạo môi trường ảo `.venv` và cài đặt dependencies (`fastmcp`, `pydantic`, `httpx`...).
  * Khởi tạo `.env` từ `.env.example` (chế độ an toàn `mock/dry-run`).
  * Đăng ký Harness `marketing-hub.json` vào Buzz Desktop.

#### Bước 3: Triển khai Tầng 1 - Bơm Khung 28 Kênh & 25 Agent
```bash
python 01-Community-OS/inject_framework.py --url "<COMMUNITY_URL>" --nsec "<OWNER_NSEC>"
```
* **Nhiệm vụ tự động hoàn thành:**
  * Kết nối WebSocket WSS vào Relay của Community.
  * Ký Nostr Kind 40 tạo 28 phòng ban chuẩn hóa.
  * Ký Nostr Kind 0 khởi tạo 25 nhân sự AI chuẩn tên chuyên nghiệp.
  * Ký Nostr Kind 9021 đưa toàn bộ 25 bot vào 28 phòng ban (700+ quan hệ thành viên).

#### Bước 4: Chạy Bộ Kiểm Tra Chuẩn Đoán (Verification)
```bash
python verify_system.py
```
* Agent đọc kết quả: Nếu tất cả 10 mục đều hiển thị `✅ [PASS]`, toàn bộ hệ điều hành đã được tích hợp hoàn hảo.

---

## 4. HƯỚNG DẪN NGƯỜI DÙNG THỰC THI CÁC BƯỚC GIAO DIỆN (UI STEPS)

Sau khi hoàn thành phần lệnh chạy ngầm, Agent hãy hướng dẫn người dùng thực hiện 2 thao tác trên giao diện:

### A. Nhập Team Snapshot vào Buzz Desktop (10 giây)
1. Mở ứng dụng **Buzz Desktop**.
2. Chọn menu **Teams** (hoặc biểu tượng Tổ chức) -> Chọn **Import Team Snapshot**.
3. Chọn tệp: `01-Community-OS/Marketing-OS-Full.team.json`.
4. Bấm **Import**: Toàn bộ danh tính, avatar, SOP và phân quyền của 25 Agent sẽ xuất hiện trên ứng dụng.

### B. Đăng nhập tài khoản ChatGPT / Codex (Nếu dùng nhiều tài khoản xoay tua)
1. Chạy file: `02-Codex-Rotator/Quan-Ly-Tai-Khoan.bat` (hoặc `node 02-Codex-Rotator/account-manager.js`).
2. Chọn `[1]` để đăng nhập tài khoản 1, `[2]` tài khoản 2, hoặc `[A]` để chạy trình hướng dẫn liên hoàn.
3. Trình duyệt tự động mở `https://auth.openai.com/codex/device` -> Người dùng nhập mã xác thực -> Hoàn tất lưu token vĩnh viễn vào profile riêng.

---

## 5. THỰC THI KHI NGƯỜI DÙNG YÊU CẦU KẾT NỐI API THỰC TẾ (LIVE MUTATIONS)
* Mặc định hệ thống hoạt động ở chế độ `MARKETING_ENVIRONMENT=mock` (an toàn, lập chiến lược và tạo bài viết bình thường).
* Nếu người dùng muốn bot tự động đăng bài Facebook, up video TikTok thật:
  * Hướng dẫn họ mở tệp: `~/marketing-ai-system/.env`.
  * Xem tài liệu hướng dẫn: `03-Marketing-Hub/CONNECTOR_GUIDE.md`.
  * Điền Token Fanpage, Zoho CRM, hoặc TikTok API.
