# HƯỚNG DẪN CẤU HÌNH API & KẾT NỐI HỆ THỐNG MARKETING HUB

Marketing Hub (`marketing-ai-system`) là cầu nối giúp 25 nhân sự AI trên Buzz có thể thực thi các tác vụ ra thế giới thực (đăng bài Facebook, tải video TikTok, tra cứu khách hàng Zoho CRM, kiểm tra Google Drive...).

---

## 1. Chế Độ Mặc Định (An Toàn - Mock / Dry Run)
Trong file `.env`:
```env
MARKETING_ENVIRONMENT=mock
MARKETING_SAFE_DRY_RUN=true
```
* **Ý nghĩa**: Khi chưa có tài khoản thực tế, hệ thống vẫn phản hồi kết quả giả lập chuẩn xác để các Agent AI lập chiến lược, soạn bài và chạy quy trình mà không bị báo lỗi.
* **Lợi ích**: Cài đặt là chạy ngay được ngay cả khi doanh nghiệp chưa kịp cấp quyền mạng xã hội.

---

## 2. Kết Nối Các Kênh Thực Tế (Khi Doanh Nghiệp Muốn Đăng Bài Thật)

Khi muốn chuyển sang chế độ thực tế, đổi `MARKETING_ENVIRONMENT=production` và điền các khóa sau:

### A. Facebook Fanpage & Meta Ads
1. Truy cập [Meta for Developers](https://developers.facebook.com/)
2. Tạo App -> Thêm sản phẩm: **Marketing API** & **Pages API**.
3. Điền vào file `.env`:
```env
META_APP_ID=<ID_Ứng_Dụng>
META_APP_SECRET=<Khóa_Bí_Mật>
META_ACCESS_TOKEN=<Mã_Truy_Cập_Trang_Dài_Hạn>
META_AD_ACCOUNT_ID=act_<ID_Tài_Khoản_Quảng_Cáo>
```

### B. Zoho CRM
1. Truy cập [Zoho API Console](https://api-console.zoho.com/)
2. Tạo Self-Client hoặc Server-based Application.
3. Cấp phạm vi: `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`.
4. Điền vào file `.env`:
```env
ZOHO_CLIENT_ID=<Client_ID>
ZOHO_CLIENT_SECRET=<Client_Secret>
ZOHO_REFRESH_TOKEN=<Refresh_Token>
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
ZOHO_API_DOMAIN=https://www.zohoapis.com
```

### C. TikTok Video & Studio
1. Đăng ký tại [TikTok Developers](https://developers.tiktok.com/)
2. Cấp quyền: `video.upload`, `user.info.basic`.
3. Điền vào file `.env`:
```env
TIKTOK_CLIENT_KEY=<Client_Key>
TIKTOK_CLIENT_SECRET=<Client_Secret>
TIKTOK_REFRESH_TOKEN=<Refresh_Token>
```

### D. YouTube & Google Drive
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Bật **YouTube Data API v3** và **Google Drive API**.
3. Tạo OAuth 2.0 Client ID (Desktop Application).
4. Điền vào file `.env`:
```env
YOUTUBE_API_KEY=<API_Key>
YOUTUBE_CHANNEL_ID=<Channel_ID>
GOOGLE_DRIVE_CLIENT_ID=<Client_ID>
GOOGLE_DRIVE_CLIENT_SECRET=<Client_Secret>
GOOGLE_DRIVE_REFRESH_TOKEN=<Refresh_Token>
```

---

## 3. Cách Kiểm Tra Kết Nối
Chạy script kiểm tra:
```bash
python test_hub.py
```
Nếu màn hình thông báo `✅ Trạng thái: SẴN SÀNG KẾT NỐI VỚI BUZZ AGENTS`, nghĩa là toàn bộ công cụ đã sẵn sàng!
