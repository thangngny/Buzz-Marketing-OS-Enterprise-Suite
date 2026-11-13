# Minh Van Logistics - Air Import Lead Intelligence & Live Zoho Deduplication Pipeline

Hệ thống tự động hóa nghiên cứu, thẩm định và đối soát khách hàng tiềm năng Air Import cho Minh Vân Logistics. Xử lý triệt để 6 nguyên nhân gốc rễ (Root Causes) và tuân thủ 100% 14 tiêu chí thẩm định theo **Master Prompt – Continuous Research Loop**.

---

## 1. Cấu trúc mô-đun

- `zoho_live_dedupe.py`: Engine đối soát trùng lặp thời gian thực với Live Zoho CRM (Leads & Accounts) qua REST API và bộ nhớ đệm 3.603 MST.
- `build_zoho_live_cache.py`: Script quét toàn bộ danh bạ Zoho CRM qua phân trang REST API (`/crm/v8/Accounts`, `/crm/v8/Leads`).
- `zoho_live_vat_cache.json`: Cache đối soát thời gian thực 3.603 MST & 3.961 tên pháp nhân.
- `industry_mapper.py`: Engine ánh xạ danh mục ngành nghề chính thức chuẩn Minh Vân từ `CRM_Industry_Codes.xlsx`.
- `CRM_Industry_Codes.xlsx` & `CRM_Industry_Codes.json`: Danh mục 1.000 mã ngành chuẩn CRM Minh Vân.
- `master_air_import_pipeline.py`: Pipeline thu thập, thẩm định 14 tiêu chí, sinh cấu trúc S3N và xuất file 4 Sheet.
- `buzz_watchdog.py`: Hệ thống giám sát RAM Guardian & Dead-tree process reaper, bảo vệ bộ nhớ không bị nghẽn.
- `buzz_export.py`: Universal Blossom & GitHub Release CDN uploader cho file báo cáo và deliverable.

---

## 2. Tiêu chuẩn chất lượng (14 QC Criteria)

1. **Pháp nhân & MST**: Xác thực 100% qua Tổng cục Thuế / Masothue.
2. **Địa chỉ**: Tách biệt rõ ràng số nhà/phố, phường/xã, quận/huyện, tỉnh/thành.
3. **Kênh doanh nghiệp**: Website chính thức hoạt động theo tên miền công ty.
4. **Đại diện pháp luật**: Đầy đủ họ tên và chức danh pháp lý.
5. **Người phụ trách**: Định danh PIC Mua hàng / Kỹ thuật / Xuất Nhập Khẩu.
6. **Email & Điện thoại**: 100% email tên miền doanh nghiệp (@domain.vn/com) và hotline hoạt động.
7. **Industry Code**: Ánh xạ chính xác từ `CRM_Industry_Codes.xlsx` (HLS-001, HLS-003, IND-002, IND-004, IND-005).
8. **Mặt hàng & HS Code**: Trích xuất mã HS thực tế từ dữ liệu hải quan.
9. **Xuất xứ hàng hóa**: Quốc gia đối tác cung ứng (Nhật Bản, Hàn Quốc, Đức, Mỹ, Thụy Sĩ, v.v.).
10. **Trade Intelligence**: Lịch sử nhập khẩu công khai từ Panjiva và Volza.
11. **Tuyến vận tải**: Chặng bay quốc tế về HAN (Nội Bài) / SGN (Tân Sơn Nhất).
12. **Phương thức vận chuyển**: Xác thực vận tải hàng không (Air Freight).
13. **Trọng lượng tính cước**: Chứng thực $\ge$ 45kg chargeable weight (từ 50kg đến 5.400kg/lô).
14. **Audit Source Log**: 100 link nguồn trực tiếp, không dùng URL giả lập.

---

## 3. Tệp bàn giao (Deliverables)

Thư mục `deliverables/`:
- `MinhVan_AirImport_20_Qualified_Leads.xlsx`: Excel báo cáo chuẩn 4 sheet (`Zoho_Leads`, `Research_Summary`, `Source_Log`, `Research_Pending`).
- `MinhVan_AirImport_20_Qualified_Leads_Zoho_Import.csv`: CSV chuẩn 23 cột Zoho CRM (mã hóa `UTF-8 with BOM`).
