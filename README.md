# 🚀 BUZZ MARKETING OS — FULL ENTERPRISE SUITE

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Architecture: 3--Layer](https://img.shields.io/badge/Architecture-3--Layer%20Enterprise-success.svg)]()
[![MCP Tools: 37](https://img.shields.io/badge/MCP%20Tools-37%20Marketing%20Connectors-orange.svg)]()
[![Protocol: Nostr%20%2B%20ACP](https://img.shields.io/badge/Protocol-Nostr%20%2B%20ACP-purple.svg)]()
[![Audited: 100%20Pass](https://img.shields.io/badge/Verification-10%2F10%20PASS-brightgreen.svg)]()

> **Hệ điều hành Marketing AI Doanh nghiệp toàn diện** — Tự động hóa từ hoạch định chiến lược, sáng tạo nội dung, sản xuất video, chạy quảng cáo đến nuôi dưỡng Lead B2B & CRM.  
> Được thiết kế để chạy mượt mà trên ứng dụng **Buzz Desktop** với giao diện Nostr Community, liên kết động cơ xoay tài khoản **ChatGPT Codex** không giới hạn hạn ngạch và Hub 37 công cụ tiếp thị đa kênh **FastMCP**.

---

## 🌟 TÍNH NĂNG NỔI BẬT

1. **🏢 28 Phòng Ban Chuẩn & 23 Chuyên Gia AI Tinh Nhuệ**:
   - Khung tổ chức phòng ban đầy đủ: Strategy, Creative Studio, Content Planner, SEO & Web, Paid Media, Organic Social, B2B Lead Gen, CRM Lifecycle...
   - Tự động nạp vào Buzz Desktop, thiết lập quyền tương tác mở (`respond_to: anyone`) kèm phát sóng NIP-98 và Nostr Kind 10100 giúp mọi thành viên trong doanh nghiệp đều có thể tag và giao việc trực tiếp cho Bot.

2. **🔄 Bộ Xoay Tài Khoản ChatGPT Codex Đa Nhiệm (Dynamic Multi-Account Rotator)**:
   - Tự động phân tải thông minh (Round-Robin) qua nhiều tài khoản ChatGPT Codex độc lập.
   - Cơ chế tự phục hồi: Tự động đưa tài khoản chạm hạn ngạch (Rate Limit 429) vào danh sách tạm nghỉ 60 phút và chuyển tiếp sang tài khoản khác mà không làm gián đoạn công việc của người dùng.
   - **Hoàn toàn động**: Không giới hạn số lượng tài khoản, tự động nhận diện tài khoản mới trong `~/.codex/profiles/`.
   - Cung cấp Wizard liên hoàn giúp đăng nhập nhiều tài khoản chỉ trong 1 lần chạy duy nhất.

3. **🔌 Marketing System Hub MCP (37 Công Cụ Tự Động Hóa)**:
   - Tích hợp sẵn 37 công cụ MCP chuẩn doanh nghiệp: Zoho CRM, Apollo B2B Leads, Meta Ads, TikTok Channel, YouTube, Google Drive, OneDrive, Tra cứu mã ngành & thuế xuất nhập khẩu...
   - Hỗ trợ chế độ **Mock an toàn** (không gây lỗi khi chưa có khóa API) và chế độ **Live Connectors** khi cấu hình thực tế.

4. **⚡ Triển Khai 1-Chạm & Tự Chuẩn Đoán Hệ Thống (Audit-First Setup)**:
   - Trình cài đặt tự động 1-Click: `Cai-Dat-Tong-Luc.bat` cho người dùng Windows.
   - Bộ công cụ chuẩn đoán `verify_system.py` kiểm tra 10 chỉ số sẵn sàng và `test_e2e_full.py` nghiệm thu 6/6 bài kiểm thử toàn diện.

---

## 🏗️ KIẾN TRÚC TỔNG THỂ (3 TẦNG KẾT HỢP)

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
| * 23 Chuyên gia AI     |      | * Auto-Failover & Cooldown (1h)    |      | * 37 Công cụ tiếp thị|
| * Kind 0 Profile       |      | * Tier Routing (Light/Heavy)       |      | * Zoho, Meta, TikTok |
| * Kind 10100 (Anyone)  |      | * Quản lý: ~/.codex/profiles/      |      | * Chế độ Mock & Live |
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

## 🚀 HƯỚNG DẪN CÀI ĐẶT NHANH (QUICK START)

### Dành cho Người dùng (Chỉ 1 Click)

1. **Chuẩn bị môi trường**:
   - Đã cài đặt [Python 3.10+](https://www.python.org/downloads/) (Lưu ý tích chọn *Add Python to PATH* khi cài).
   - Đã cài đặt [Node.js 18+](https://nodejs.org/).
   - Đã cài đặt ứng dụng [Buzz Desktop](https://buzz.xyz).

2. **Kích hoạt cài đặt**:
   - Nhấp đúp chuột vào file:
     ```
     Cai-Dat-Tong-Luc.bat
     ```
   - Trình cài đặt sẽ tự động:
     - Tạo và thiết lập bộ xoay tài khoản Codex.
     - Tải và cài đặt Marketing System Hub MCP (kèm môi trường ảo Python).
     - Đăng ký các Harness vào Buzz Desktop.
     - Đồng bộ 23 Chuyên gia AI vào cấu hình máy tính.
     - Chạy chuẩn đoán hệ thống và thông báo kết quả sẵn sàng.

3. **Đăng nhập các tài khoản ChatGPT Codex**:
   - Nhấp đúp chuột vào: `02-Codex-Rotator/Quan-Ly-Tai-Khoan.bat`
   - Chọn `[A] WIZARD LIÊN HOÀN` để đăng nhập lần lượt các tài khoản của bạn qua trình duyệt.

---

### Dành cho AI Coding Agents (Cursor, Claude Code, Antigravity, Copilot...)

> 💡 **Khuyến nghị**: Hãy đọc kỹ file [`AGENTS.md`](./AGENTS.md) để nắm toàn bộ quy trình **Audit-First & Self-Healing**.

Quy trình tự động cho AI Agent:
```bash
# 1. Kiểm tra hiện trạng hệ thống
python verify_system.py

# 2. Triển khai toàn bộ tự động (nếu có mục nào chưa đạt)
python master_deploy.py --all

# 3. Xác thực lại toàn bộ hệ thống
python verify_system.py

# 4. Chạy kiểm thử End-to-End nghiệm thu
python test_e2e_full.py
```

---

## 📂 DANH MỤC TỆP TIN DỰ ÁN

| Đường dẫn / Tệp tin | Vai trò & Mục đích |
| :--- | :--- |
| `AGENTS.md` | Chỉ dẫn kiến trúc và luồng thực thi tự động dành riêng cho AI Coding Agents |
| `Cai-Dat-Tong-Luc.bat` | Bộ cài đặt 1-Click dành cho người dùng Windows |
| `master_deploy.py` | Trình điều phối triển khai toàn bộ 3 tầng trên mọi hệ điều hành |
| `verify_system.py` | Bộ công cụ chuẩn đoán tự động kiểm tra 10 tiêu chí sẵn sàng |
| `test_e2e_full.py` | Bộ kiểm thử E2E 6/6 tiêu chuẩn đánh giá hoàn thiện |
| `01-Community-OS/` | Cấu trúc 28 kênh phòng ban, 23 Agent Nostr, chính sách Kind 10100 & Relay |
| `02-Codex-Rotator/` | Động cơ xoay tài khoản ChatGPT Codex, bộ quản lý tài khoản động và harness ACP |
| `03-Marketing-Hub/` | Hub 37 công cụ MCP (kết nối Zoho, Apollo, Meta, TikTok...) và hướng dẫn API |
| `04-Buzz-Harnesses/` | Các mẫu cấu hình Custom Harness nạp trực tiếp vào Buzz Desktop |

---

## 📄 BẢO MẬT & GIẤY PHÉP

- Toàn bộ khóa bảo mật của doanh nghiệp và token cá nhân đều được lưu trữ cục bộ trong thư mục người dùng (`~/.codex/profiles/` và `%APPDATA%\xyz.block.buzz.app`).
- Repository tuân thủ nguyên tắc an toàn: Không lưu cứng bất kỳ token, mã khóa riêng tư hay thông tin cá nhân nào trong mã nguồn.
- Phát hành theo giấy phép **MIT License**.
