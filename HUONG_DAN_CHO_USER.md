# HƯỚNG DẪN BÀN GIAO TRỌN GÓI: BUZZ MARKETING OS FULL ENTERPRISE

Chào anh/chị Owner, đây là **gói giải pháp toàn diện nhất** của Hệ điều hành Tiếp thị & Truyền thông Buzz AI (Buzz Marketing Operating System).

Toàn bộ hệ thống đã được đóng gói khoa học thành 3 Tầng độc lập, tự động hóa tương thích trên mọi máy tính Windows.

---

## 📦 BÊN TRONG BỘ CÀI NÀY CÓ GÌ?

```
Buzz-Marketing-OS-Enterprise-Suite/
├── AGENT_DEPLOYMENT_DIRECTIVE.md   <-- CHỈ THỊ DÀNH RIÊNG CHO CODING AGENT
├── HUONG_DAN_CHO_USER.md          <-- HƯỚNG DẪN NHANH DÀNH CHO BẠN
├── master_deploy.py                <-- SCRIPT ĐIỀU PHỐI TỔNG LỰC
├── verify_system.py                <-- BỘ KIỂM TRA CHUẨN ĐOÁN 10 CHỈ SỐ
├── Cai-Dat-Tong-Luc.bat            <-- FILE BẤM 1 CHUỘT CÀI ĐẶT
│
├── 01-Community-OS/                <-- TẦNG 1: 28 PHÒNG BAN & 25 AGENT CHUYÊN GIA
├── 02-Codex-Rotator/               <-- TẦNG 2: BỘ XOAY NHIỀU TÀI KHOẢN CHATGPT
├── 03-Marketing-Hub/               <-- TẦNG 3: HUB KẾT NỐI FACEBOOK, TIKTOK, ZOHO
└── 04-Buzz-Harnesses/              <-- CẤU HÌNH TỰ ĐỘNG CHO ỨNG DỤNG BUZZ DESKTOP
```

---

## 🚀 KHI CHUYỂN SANG MÁY KHÁC: GIAO CHO CODING AGENT NHƯ THẾ NÀO?

Khi giải nén thư mục này trên máy mới, anh chỉ cần nhắn đúng 1 câu lệnh cho Coding Agent (Antigravity, Claude, Cursor, v.v.):

> *"Đọc thật kỹ file AGENT_DEPLOYMENT_DIRECTIVE.md rồi thực thi triển khai full hệ thống cho tôi. Đây là link community: `<LINK>` và mã khóa: `<NSEC>`"*

Coding Agent trên máy đó sẽ:
1. Đọc chỉ thị kỹ thuật.
2. Tự động chạy `master_deploy.py --all`.
3. Tự động thiết lập Tầng 1 (kênh + bot), Tầng 2 (bộ xoay tài khoản), Tầng 3 (Hub kết nối).
4. Tự động chạy `verify_system.py` và báo cáo lại kết quả hoàn tất cho anh.

---

## 🛠️ NẾU ANH MUỐN TỰ BẤM CHUỘT CÀI ĐẶT:

Nếu không dùng Agent, anh chỉ cần thực hiện 3 bước đơn giản:

1. **Bấm đúp file `Cai-Dat-Tong-Luc.bat`**:
   * Nhập số `[1]` để chọn cài đặt toàn bộ.
   * Nhập Link Community và Mã khóa `nsec` khi được hỏi.
2. **Nhập Team vào Buzz Desktop**:
   * Mở Buzz Desktop -> Vào mục **Teams** -> Bấm **Import Team Snapshot**.
   * Chọn file: `01-Community-OS/Marketing-OS-Full.team.json`.
3. **Đăng nhập tài khoản ChatGPT (Nếu dùng bộ xoay nhiều tài khoản)**:
   * Chạy file: `02-Codex-Rotator/Quan-Ly-Tai-Khoan.bat` để đăng nhập 1 đến 3 tài khoản.

---

## 🔒 AN TOÀN & BẢO MẬT
* Hệ thống mặc định chạy ở chế độ **Mock / An toàn**, các bot có đầy đủ công cụ phân tích và tạo nội dung mà không gây ảnh hưởng hay xung đột với tài khoản thật.
* Khi muốn kết nối trang Facebook Fanpage hoặc tài khoản TikTok của công ty, chỉ cần làm theo hướng dẫn tại: `03-Marketing-Hub/CONNECTOR_GUIDE.md`.
