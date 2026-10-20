# HƯỚNG DẪN BÀN GIAO TRỌN GÓI: BUZZ MARKETING OS FULL ENTERPRISE

Chào anh/chị Owner, đây là **gói giải pháp toàn diện nhất** của Hệ điều hành Tiếp thị & Truyền thông Buzz AI (Buzz Marketing Operating System).

Toàn bộ hệ thống đã được đóng gói khoa học thành 3 Tầng độc lập, **100% linh động (dynamic)** và tự động hóa tương thích trên mọi máy tính Windows/macOS/Linux.

---

## 📦 BÊN TRONG BỘ CÀI NÀY CÓ GÌ?

```
Buzz-Marketing-OS-Enterprise-Suite/
├── AGENTS.md                          <-- TÀI LIỆU CHỈ ĐẠO CHO AI CODING AGENTS
├── AGENT_DEPLOYMENT_DIRECTIVE.md       <-- CHỈ THỊ KỸ THUẬT TRIỂN KHAI CHO AGENT
├── HUONG_DAN_CHO_USER.md              <-- HƯỚNG DẪN NHANH DÀNH CHO BẠN (File này)
├── master_deploy.py                   <-- SCRIPT ĐIỀU PHỐI TỔNG LỰC 3 TẦNG
├── verify_system.py                   <-- BỘ KIỂM TRA CHUẨN ĐOÁN 11 CHỈ SỐ SẴN SÀNG
├── test_e2e_full.py                   <-- BỘ KIỂM THỬ E2E TOÀN DIỆN (6/6 TESTS)
├── simulate_e2e_full.py               <-- BỘ GIẢ LẬP GỬI TIN NHẮN THỰC TẾ
├── Cai-Dat-Tong-Luc.bat               <-- 1-CLICK CÀI ĐẶT TRỌN GÓI CHO WINDOWS
│
├── 01-Community-OS/                   <-- TẦNG 1: 28 PHÒNG BAN, 23-46 AGENT, PHÂN QUYỀN MỞ (ANYONE)
│   ├── channels_master.json           <-- Danh mục 28 phòng ban nghiệp vụ chuẩn
│   ├── agents_template.json           <-- Hồ sơ 23-46 Agent AI chuyên gia
│   ├── setup_managed_agents.py        <-- Cài đặt Agent vào Buzz Desktop (Anyone Access)
│   ├── unlock_full_permissions.py     <-- Tự động mở toàn quyền tương tác cho mọi thành viên
│   ├── broadcast_kind_10100.js        <-- Ký & phát sóng Nostr Kind 10100 lên Relay
│   └── inject_framework.py            <-- Bơm kênh phòng ban & phân bổ bot
│
├── 02-Codex-Rotator/                  <-- TẦNG 2: BỘ XOAY TÀI KHOẢN ĐỘNG (DYNAMIC MULTI-ACCOUNT)
│   ├── codex-rotator.js               <-- Động cơ xoay Round-Robin & Cooldown linh hoạt
│   ├── codex-acp-rotator.js           <-- Wrapper ACP tích hợp Buzz Desktop
│   ├── account-manager.js             <-- Giao diện quản lý & đăng nhập tài khoản
│   └── Quan-Ly-Tai-Khoan.bat          <-- 1-Click mở menu quản lý tài khoản
│
├── 03-Marketing-Hub/                  <-- TẦNG 3: HUB MCP 37 CÔNG CỤ (ZOHO, TIKTOK, FACEBOOK, LINKEDIN)
│   ├── setup_hub.py                   <-- Tự động dựng môi trường ảo .venv & MCP
│   ├── test_hub.py                    <-- Kiểm tra 37 công cụ kết nối
│   ├── services/linkedin/             <-- Bộ điều phối xuất bản LinkedIn đa tầng
│   └── CONNECTOR_GUIDE.md             <-- Hướng dẫn kích hoạt API mạng xã hội
│
└── 04-Buzz-Harnesses/                 <-- TẦNG 4: HARNESSES CHO BUZZ DESKTOP
    ├── codex-harness.template.json    <-- Harness cho Codex Rotator (bypass-permissions)
    └── marketing-hub.template.json    <-- Harness cho Marketing System Hub
```

---

## 🌟 ĐẶC ĐIỂM LINH ĐỘNG VƯỢT TRỘI (DYNAMIC ARCHITECTURE)

Khác với các bản dựng tĩnh trước đây, phiên bản Full Enterprise này được thiết kế theo chuẩn **Dynamic Discovery**:

1. **Bộ xoay tài khoản Codex HOÀN TOÀN ĐỘNG (Không giới hạn)**:
   - **Không cố định 3 tài khoản**: Bạn có thể đăng nhập **1, 2, 3, 5 hay 10 tài khoản ChatGPT Codex** tùy ý (`acc-1`, `acc-2`, `lina.ho`, `sales-team`...).
   - Hệ thống tự động quét thư mục `~/.codex/profiles/` và nạp mọi tài khoản đã đăng nhập (`auth.json`) vào vòng xoay tải.
   - Khi một tài khoản hết token hoặc bị Rate Limit 429, hệ thống tự động cho tài khoản đó "nghỉ ngơi" (cooldown) và chuyển ngay sang tài khoản tiếp theo.

2. **Phân quyền Mở Toàn Diện (Universal Anyone Access)**:
   - Tất cả Agent đều mang chính sách `respond_to: anyone`, cờ `bypass-permissions`, và Runner Codex `approval_policy = never`.
   - Bất kỳ thành viên nào trong công ty (Lina, Nam, nhân viên...) khi tag `@Agent` trong Buzz đều có thể giao việc và nhận kết quả trực tiếp mà **không bị chặn quyền, không bị khóa nút gửi và không cần chờ duyệt từ Owner**.

3. **Tự động nhận diện Community Relay (Relay Auto-Discovery)**:
   - Khi chuyển sang máy mới, hệ thống tự động phát hiện URL Community từ Buzz Desktop hoặc nhận qua cờ `--community-url`, không bị dán cứng vào bất kỳ tên miền cụ thể nào.

4. **Đóng gói trọn gói Bộ điều phối LinkedIn Đa tầng**:
   - Tích hợp sẵn trong thư mục `03-Marketing-Hub/services/linkedin/` và tự động cài đặt vào máy đích, hỗ trợ đầy đủ 3 tầng dự phòng: Official REST API, 1-Click Page Repost và Trình duyệt soạn thảo thông minh.

---

## 🚀 KHI CHUYỂN SANG MÁY KHÁC: GIAO CHO CODING AGENT NHƯ THẾ NÀO?

Khi giải nén thư mục này trên máy mới, anh chỉ cần nhắn đúng 1 câu lệnh cho Coding Agent (Antigravity, Claude, Cursor, Codex...):

> *"Đọc thật kỹ file AGENT_DEPLOYMENT_DIRECTIVE.md rồi thực thi triển khai full hệ thống cho tôi. Đây là link community: `<LINK>` và mã khóa: `<NSEC>`"*

Coding Agent trên máy đó sẽ:
1. Đọc chỉ thị kỹ thuật.
2. Tự động chạy `python master_deploy.py --all --community-url "<LINK>" --nsec "<NSEC>"`.
3. Tự động thiết lập Tầng 1 (kênh + bot), Tầng 2 (bộ xoay tài khoản động), Tầng 3 (Hub kết nối).
4. Tự động chạy `verify_system.py` và `test_e2e_full.py` để nghiệm thu 100% PASS trước khi bàn giao.

---

## 🛠️ NẾU ANH MUỐN TỰ BẤM CHUỘT CÀI ĐẶT:

1. **Bấm đúp file `Cai-Dat-Tong-Luc.bat`**:
   - Nhập số `[1]` để chọn cài đặt toàn bộ.
   - Hệ thống sẽ **tự động nạp toàn bộ 23 Agent & Đội ngũ vào Buzz Desktop** (`managed-agents.json`), tự động mở full quyền `anyone` và cấu hình các Harness.

2. **Đăng nhập các tài khoản ChatGPT Codex**:
   - Chạy file: `02-Codex-Rotator/Quan-Ly-Tai-Khoan.bat`.
   - Chọn `[A]` (Wizard liên hoàn) để đăng nhập lần lượt các tài khoản, hoặc chọn `[+]` để thêm tài khoản mới với tên tùy ý.

3. **Kiểm tra trạng thái hệ thống**:
   - Chạy `python verify_system.py` để xác nhận toàn bộ 11/11 chỉ số đều đạt `✅ [PASS]`.
   - Chạy `python test_e2e_full.py` để xác nhận 6/6 bài kiểm thử E2E thành công 100%.

---

## 🔒 AN TOÀN & BẢO MẬT
* Hệ thống mặc định chạy ở chế độ **Mock / An toàn**, các bot có đầy đủ công cụ phân tích và tạo nội dung mà không gây ảnh hưởng hay xung đột với tài khoản thật.
* Khi muốn kết nối trang Facebook Fanpage hoặc tài khoản TikTok của công ty, chỉ cần làm theo hướng dẫn tại: `03-Marketing-Hub/CONNECTOR_GUIDE.md`.
