# 🤖 AGENTS.md — HƯỚNG DẪN DÀNH CHO AI CODING AGENT

> **DÀNH CHO TẤT CẢ CÁC AI CODING AGENTS (Cursor, Claude Code, Antigravity, Copilot, Codex, Roo Code...)**  
> Khi bạn clone repository này về một máy tính bất kỳ (Windows/macOS/Linux), hãy đọc tài liệu này đầu tiên. Tài liệu này cung cấp đầy đủ bức tranh kiến trúc, nguyên tắc tự động hóa và quy trình chuẩn **Audit-First & Self-Healing** để bạn thiết lập và bàn giao toàn bộ hệ thống mà không cần người dùng can thiệp thủ công.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (3-LAYER ENTERPRISE ARCHITECTURE)

Hệ thống **Buzz Marketing OS Full Enterprise** là hệ điều hành Marketing tự hành 100% gồm 3 tầng liên kết chặt chẽ:

```
+--------------------------------------------------------------------------------------------------+
|                                     BUZZ DESKTOP APPLICATION                                     |
|                               (Nostr Protocol Community Interface)                               |
+--------------------------------------------------------------------------------------------------+
          |                                        |                                      |
          v                                        v                                      v
+------------------------+      +------------------------------------+      +----------------------+
|        TẦNG 1          |      |               TẦNG 2               |      |        TẦNG 3        |
|      COMMUNITY OS      |      |       CODEX ACCOUNT ROTATOR        |      |    MARKETING HUB     |
| (Nostr Relay Engine)   |      |     (Load-Balancer & Failover)     |      |  (MCP Tools Server)  |
+------------------------+      +------------------------------------+      +----------------------+
| * 28 Phòng ban chuẩn   |      | * Dynamic Multi-Account Pool       |      | * FastMCP Protocol   |
| * 23 Chuyên gia AI     |      | * Auto-Failover & Cooldown (1h)    |      | * 37 Công cụ tự động |
| * Kind 0 Profile       |      | * Tier Routing (Light/Heavy)       |      | * Zoho, Meta, TikTok |
| * Kind 10100 (Anyone)  |      | * Cấu hình: ~/.codex/profiles/     |      | * Chế độ Mock & Live |
| * Template & Managed   |      | * Bypass-permissions mode          |      | * Virtualenv Python  |
+------------------------+      +------------------------------------+      +----------------------+
                                                   |
                                                   v
                                 +------------------------------------+
                                 |               TẦNG 4               |
                                 |       BUZZ CUSTOM HARNESSES        |
                                 | (codex-harness + marketing-hub)    |
                                 +------------------------------------+
```

---

## 2. NGUYÊN TẮC VÀNG CHO AI CODING AGENT (AUDIT-FIRST WORKFLOW)

Khi nhận được yêu cầu cài đặt hoặc kiểm tra hệ thống trên bất kỳ máy tính nào, **AI Agent BẮT BUỘC tuân theo chu trình 4 bước**:

```
[BƯỚC 1: AUDIT] --------> [BƯỚC 2: CÀI ĐẶT / TỰ SỬA] --------> [BƯỚC 3: XÁC THỰC] --------> [BƯỚC 4: E2E TEST]
verify_system.py           master_deploy.py --all              verify_system.py            test_e2e_full.py
(Tìm gì thiếu?)           (Chỉ cài đặt phần thiếu)           (Xác nhận 10/10 PASS)       (Nghiệm thu 6/6 PASS)
```

### Chi tiết từng bước:

### BƯỚC 1: Chuẩn Đoán & Kiểm Tra Hiện Trạng (Audit Pre-flight)
Chạy lệnh kiểm tra 10 chỉ số sẵn sàng:
```bash
python verify_system.py
```
*(Nếu `python` chưa có trong PATH, hãy thử dùng `py`, `%USERPROFILE%\marketing-ai-system\.venv\Scripts\python.exe`, hoặc `uv run python`)*.

Script sẽ quét và in ra trạng thái từng thành phần:
- Tầng 1: Đã có đủ tệp mẫu 28 kênh và 23 Agent chưa? Đã cấp quyền `respond_to: anyone` chưa?
- Tầng 2: Node.js đã sẵn sàng chưa? Bộ xoay tài khoản đã nằm trong `~/.codex` chưa? Đã đăng nhập bao nhiêu tài khoản?
- Tầng 3: Repo `marketing-ai-system` đã tồn tại chưa? Môi trường ảo Python (`.venv`) đã kích hoạt chưa? MCP Server có nạp được 37 tools không?
- Tầng 4: Các Custom Harnesses (`codex-harness.json`, `marketing-hub.json`) đã được đăng ký vào Buzz Desktop chưa?

### BƯỚC 2: Tự Động Cài Đặt và Bù Đắp Thành Phần Thiếu (Self-Healing Deployment)
Nếu có bất kỳ chỉ số nào `❌ [FAIL]`, Agent kích hoạt cài đặt tự động toàn bộ:

```bash
# Triển khai toàn bộ cả 3 tầng (Tự động tải repo, tạo venv, cài thư viện, đăng ký harness)
python master_deploy.py --all
```

Hoặc triển khai từng tầng nếu cần cô lập:
- **Tầng 2 (Codex Rotator)**: `python 02-Codex-Rotator/setup_rotator.py`
- **Tầng 3 (Marketing Hub MCP)**: `python 03-Marketing-Hub/setup_hub.py`
- **Tầng 4 (Custom Harnesses)**: `python 04-Buzz-Harnesses/install_harnesses.py`
- **Tầng 1 (Đồng bộ Buzz Desktop)**: `python 01-Community-OS/setup_managed_agents.py`
- **Tầng 1 (Bơm Kênh & Agent vào Relay)**:
  ```bash
  python 01-Community-OS/inject_framework.py --url "<COMMUNITY_URL>" --nsec "<OWNER_NSEC>"
  ```

### BƯỚC 3: Tái Thẩm Định (Post-Audit Re-check)
Chạy lại:
```bash
python verify_system.py
```
Đảm bảo tất cả 10 chỉ số đều đạt `✅ [PASS]`.

### BƯỚC 4: Nghiệm Thu Cuối Cùng (End-to-End Test Suite)
Chạy bộ kiểm thử toàn diện:
```bash
python test_e2e_full.py
```
Tiêu chuẩn bàn giao hoàn hảo: **6/6 TESTS PASS**.

---

## 3. CƠ CHẾ VẬN HÀNH BỘ XOAY TÀI KHOẢN (CODEX ROTATOR ENGINE)

1. **Khám phá tài khoản động (Dynamic Profile Discovery)**:
   - Hệ thống **KHÔNG CỐ ĐỊNH** bất kỳ tài khoản nào.
   - Thư mục quản lý: `%USERPROFILE%\.codex\profiles\<profile_name>\`
   - Bất kỳ thư mục con nào chứa file `auth.json` sẽ tự động được đưa vào danh sách xoay vòng (Round-Robin).
   - Khi chưa có tài khoản nào, hệ thống tạo sẵn các profile mẫu: `account-1`, `account-2`, `account-3`.

2. **Quản lý và Đăng nhập Tài khoản**:
   - Chạy lệnh CLI:
     ```bash
     node 02-Codex-Rotator/account-manager.js
     ```
   - Giao diện menu động:
     - `[A] WIZARD LIÊN HOÀN`: Tự động mở trình duyệt và hướng dẫn người dùng đăng nhập lần lượt tất cả tài khoản OpenAI trong 1 phiên duy nhất.
     - `[1..N]`: Đăng nhập riêng từng tài khoản.
     - `[+]`: Thêm tài khoản mới với tên tùy biến.
     - `[R]`: Thử nghiệm xoay tua và kiểm tra tài khoản tiếp theo.

3. **Cơ chế chịu lỗi (Failover & Cooldown)**:
   - Khi một tài khoản gặp lỗi giới hạn hạn ngạch (Rate Limit 429) hoặc hết token, rotator tự động đánh dấu cooldown trong 60 phút và chuyển ngay sang tài khoản tiếp theo mà không làm gián đoạn người dùng.

---

## 4. TẦNG 3: MARKETING SYSTEM HUB MCP (37 MARKETING TOOLS)

1. **Vị trí cài đặt**:
   - Nằm tại: `%USERPROFILE%\marketing-ai-system\`
   - Kho nguồn công khai: `https://github.com/thangngny/marketing-ai-system.git`
   - Môi trường ảo Python độc lập: `%USERPROFILE%\marketing-ai-system\.venv\`

2. **Chế độ Mock an toàn (Zero-Failure Guarantee)**:
   - Mặc định, file `.env` được tạo từ `.env.example` với trạng thái Mock cho các API chưa điền khóa (Zoho, Apollo, Facebook, TikTok...).
   - Nhờ đó, các Agent trong Buzz có thể gọi thử các công cụ MCP ngay lập tức mà không bao giờ bị crash hoặc trả về lỗi HTTP 500.

3. **Kích hoạt tài khoản thật (Live Connectors)**:
   - Hướng dẫn cấu hình API nằm tại: `03-Marketing-Hub/CONNECTOR_GUIDE.md`.

---

## 5. TẦNG 1: BUZZ COMMUNITY, BUZZ CLI & XỬ LÝ LỖI PHÂN QUYỀN (ACCESS POLICY)

### 1. Khắc phục lỗi "Could not authorize a mentioned agent" / "Agent; owner unavailable"
- **Hiện tượng**: Tài khoản Owner gọi bot bình thường, nhưng thành viên khác tag bot thì bị báo lỗi chặn quyền, dưới tên bot hiện *"Agent; owner unavailable"*, nút gửi tin nhắn bị khóa.
- **Nguyên nhân gốc rễ**: 
  1. Thiếu thuộc tính `respond_to: "anyone"` và `definition_respond_to: "anyone"` trong `managed-agents.json`.
  2. Sự kiện Nostr **Kind 10100** (Access Policy: `anyone`) chưa được ký và phát sóng lên Relay.
  3. Daemon `buzz-acp` thiếu 2 cờ bắt buộc: `--permission-mode bypass-permissions` và `--respond-to anyone`.
  4. Cấu hình LLM Runner chưa tắt chế độ chờ duyệt (`approval_policy = "never"`).
- **Cách tự động sửa dứt điểm trong 1 lệnh (Self-Healing)**:
  ```bash
  python 01-Community-OS/fix_agent_permissions.py
  ```
  Script sẽ tự động thực thi trọn gói 5 bước: sửa `managed-agents.json`, phát sóng Kind 10100 lên WebSocket Relay, làm mới `buzz-acp`, cấu hình Codex không chờ duyệt và kiểm tra Buzz CLI.

### 2. Về Buzz CLI (`buzz.exe` / `buzz-acp.exe`)
- **Vai trò**: Buzz CLI là công cụ dòng lệnh đi kèm của **Buzz Desktop App** (`xyz.block.buzz.app`). Nó cần thiết để tạo kênh, phân quyền kênh, thêm thành viên và phát sóng Nostr.
- **Vị trí và cài đặt**:
  - Buzz CLI nằm sẵn bên trong thư mục cài đặt của Buzz Desktop (thường ở `%LOCALAPPDATA%\Programs\Buzz` hoặc `D:\Buzz`, `/Applications/Buzz.app`).
  - Nếu máy chưa cài Buzz Desktop: Tải bộ cài chính thức tại **https://buzz.xyz**.
  - Nếu đã cài nhưng terminal chưa nhận lệnh `buzz`: Thêm thư mục cài đặt Buzz Desktop vào biến môi trường `PATH`. Các script trong repo đã tích hợp sẵn cơ chế tự động truy quét các thư mục cài đặt này.

---

## 6. DANH MỤC TỆP TIN CỐT LÕI (DIRECTORY MAP)

```
Buzz-Marketing-OS-Enterprise-Suite/
├── AGENTS.md                          # Tài liệu chỉ đạo cho AI Coding Agents (File này)
├── README.md                          # Giới thiệu tổng quan & Hướng dẫn sử dụng
├── Cai-Dat-Tong-Luc.bat               # Trình cài đặt 1-Click cho người dùng Windows
├── master_deploy.py                   # Bộ điều phối cài đặt tự động 3 tầng
├── verify_system.py                   # Bộ kiểm tra chuẩn đoán 10 tiêu chí
├── test_e2e_full.py                   # Bộ kiểm thử E2E 6/6 Tests
│
├── 01-Community-OS/                   # TẦNG 1: Cấu trúc Community & Agent Roster
│   ├── channels_master.json           # 28 phòng ban nghiệp vụ chuẩn
│   ├── agents_template.json           # Roster 23-46 Agent AI chuyên gia
│   ├── Marketing-OS-Full.team.json    # Team Snapshot nạp vào Buzz Desktop
│   ├── inject_framework.py            # Script bơm 28 kênh và phân quyền
│   ├── setup_managed_agents.py        # Cài đặt Agent vào managed-agents.json
│   ├── deploy_official_agents.py      # Claim Relay membership & Phát sóng Kind 0
│   └── broadcast_kind_10100.js        # Phát sóng chính sách Kind 10100 (Anyone)
│
├── 02-Codex-Rotator/                  # TẦNG 2: Bộ Xoay Tài Khoản Đa Nhiệm
│   ├── codex-rotator.js               # Động cơ xoay Round-Robin & Cooldown
│   ├── codex-acp-rotator.js           # Wrapper JSON-RPC tích hợp Buzz ACP
│   ├── account-manager.js             # Quản lý tài khoản & Wizard liên hoàn
│   ├── setup_rotator.py               # Script triển khai rotator vào ~/.codex
│   ├── Quan-Ly-Tai-Khoan.bat          # 1-Click mở menu quản lý tài khoản
│   └── profiles_template/config.toml  # Cấu hình không chặn phê duyệt (never)
│
├── 03-Marketing-Hub/                  # TẦNG 3: Hub Công Cụ Tự Động Hóa (MCP)
│   ├── setup_hub.py                   # Tự động clone, tạo .venv và build hub
│   ├── test_hub.py                    # Kiểm tra 37 công cụ MCP
│   ├── .env.example                   # Biến môi trường mẫu (chế độ mock an toàn)
│   └── CONNECTOR_GUIDE.md             # Hướng dẫn kết nối Zoho, Apollo, Meta...
│
└── 04-Buzz-Harnesses/                 # TẦNG 4: Kết Nối Cầu Nối Vào Buzz Desktop
    ├── codex-harness.template.json    # Template Harness cho Codex Rotator
    ├── marketing-hub.template.json    # Template Harness cho Marketing Hub MCP
    └── install_harnesses.py           # Script nạp harness vào AppData
```
