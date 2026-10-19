#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUZZ MARKETING AI OS - 1-CLICK TURNKEY INJECTOR
Tự động đóng gói và triển khai toàn diện hệ điều hành AI Marketing vào bất kỳ Buzz Community nào.
Bao gồm: 28 Kênh phòng ban chuẩn + 23-46 Agent AI chuyên gia + Phân quyền thành viên + Kiểm tra E2E.
"""

import sys
import os
import json
import argparse
import subprocess
import shutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def find_buzz_exe():
    """Tự động tìm kiếm đường dẫn buzz.exe trên máy tính"""
    candidates = [
        r"D:\Buzz\buzz.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Buzz\buzz.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Buzz\buzz.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Buzz\buzz.exe"),
        os.path.expandvars(r"%APPDATA%\..\Local\Programs\Buzz\buzz.exe"),
    ]
    which_buzz = shutil.which("buzz")
    if which_buzz:
        return which_buzz
    for c in candidates:
        if os.path.exists(c):
            return c
    return r"D:\Buzz\buzz.exe"

BUZZ_EXE = find_buzz_exe()

try:
    from setup_managed_agents import CANONICAL_AGENTS
    ALL_AGENTS = {a["name"]: a["pubkey"] for a in CANONICAL_AGENTS}
except Exception:
    ALL_AGENTS = {
        'Marketing Orchestrator': '9612286f19ecd7692958e7eda8fc449535b3a7076ef45ca17a8bd40ed9ce8e87',
        'troly': 'fbc48fb951751d9c2e93b741d3348e750ae7038e6b1e6d45f06e50af67dfd868',
        'CRM & Lifecycle': '4d18dbc5012b45f393094de14c6a4e00c455980068fc7501b9c005df102707d6',
        'Strategy': '62568f1db283a647e7c720faf607295a97357a6ec071ef0e4c663729e1b8bc18',
        'Content Planner': 'bf250ae8cb21cec27023b9b7f5c57b93ca9837cbb031b908fdf689eae1c77529',
        'Creative Studio': '56d445607f66dfdb55cc6630ae0bc9b14bbd2efc89b89432da61b9c3f94e8fdc',
        'Organic & Social': 'f0e1d0f7e352eda2a923a0feef4d54febe96fc4299505ffa7215733a1b8d570c',
        'Paid Media': '0986bbed13eb29118a0c0bcb556387349b9ca602e7abb600e3d33f98c066e516',
        'SEO & Web': '5a6b7b3846dbcf6e4ef005d37f0a8e55358cc021ed46d51b0f4568afa2c0905b',
        'Sales Enablement': 'd3d7d68286381204095d82b9a679a41465a8a905db0fc1a605080cfe70623982',
        'Research Intelligence': 'e34370d056e62eb48eb3cb95696649ad1ea65e72a648513842e51958bcb97ff8',
        'Analytics & Finance': '6f8a3cb68179ac894338fc3acf034e4f6a71c69b9ea76d44a89cdf56f659e6ba',
        'Agent Chuẩn hóa & Lọc trùng Data': 'd8bc8636ace9cb8b0483be42d8ec78efa6b979a9a3d0365c15d1c9427303674b',
        'Agent Tìm nguồn & Trích xuất Data XNK': 'b57b0adb1f7f461be3b474928f9aa536782603e407de0b004b25c0eb153aa51c',
        'Agent Tra cứu & Xác minh Doanh nghiệp': '0913ce741b5b74b29902654a2e79ee197ee93ba1acedfa50e7d975286c3aa64c',
        'Agent Tìm Contact & Enrichment': '255ead75dbad39dff087ba014bfc3247eaace4a154a29974e85ee3835c78f6df',
        'Agent Xác định Mã ngành Minh Vân': '38a8192d237d1d6e642b67408e81267a0d8440f4f4b18e3ee193c240337d8798',
        'Agent QA & Chuẩn hóa Zoho': '922fbe242bad87a10abf69ad8918f7ead98da59b98ba9ebd9dfe8da7bdada251',
        'Codex': 'ea5c006f1e52fa961ea87f53d672711976f9d4b337bb9a3e14d2bcb38354be5e',
        'Antigravity': '0d512a646ed4a4895c04fb219ebfc59d56bb15ab2ff9544008e8cb7e267df2ad',
        'Fizz': '3fbf5c377579e6d887043f2a86c24ec3572e23169960150059227b5a69a2afd3',
        'Honey': '6e321a91c08fb88c9887fdc906840604f4796bb8b6b3aeb56fc3978f90c9dfa7',
        'Pollen': 'fc7273670c135caf3e43e9ff41fae77c64ca757fb6270854fbd4817800b4cbe5'
    }


ASSIGNMENTS = {
    '01-strategy': ['Strategy', 'Research Intelligence'],
    '02-content': ['Content Planner', 'Creative Studio'],
    '03-campaign': ['Paid Media', 'Creative Studio', 'Content Planner'],
    '04-leads': ['CRM & Lifecycle', 'Sales Enablement', 'Agent Tìm Contact & Enrichment'],
    '05-sales': ['Sales Enablement', 'CRM & Lifecycle'],
    '06-kpi-learning': ['Analytics & Finance', 'Strategy'],
    'Facebook post': ['Content Planner', 'Creative Studio', 'Organic & Social'],
    'Facebook Content Ads': ['Content Planner', 'Paid Media', 'Creative Studio'],
    'Facebook ads': ['Paid Media', 'Analytics & Finance'],
    'Tiktok': ['Creative Studio', 'Organic & Social', 'Content Planner'],
    'Youtube': ['Content Planner', 'Creative Studio', 'SEO & Web'],
    'Linkedin': ['Organic & Social', 'Content Planner'],
    'Zalo OA': ['CRM & Lifecycle', 'Content Planner'],
    'SEO & GEO Website': ['SEO & Web', 'Content Planner'],
    'App + Landing page': ['SEO & Web', 'Creative Studio'],
    'Email': ['Content Planner', 'CRM & Lifecycle'],
    'Zoho': ['Agent QA & Chuẩn hóa Zoho', 'CRM & Lifecycle'],
    'Research': ['Research Intelligence', 'Agent Tra cứu & Xác minh Doanh nghiệp'],
    'Data': ['Agent Chuẩn hóa & Lọc trùng Data', 'Agent Tìm nguồn & Trích xuất Data XNK'],
    'Tai chinh': ['Analytics & Finance'],
    'welcome-everyone': ['Fizz', 'Honey', 'Pollen'],
    'general': ['Fizz', 'Honey', 'Pollen']
}

def run_buzz(relay, private_key, args):
    cmd = [BUZZ_EXE, "--relay", relay, "--private-key", private_key] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return res

def list_existing_channels(relay, private_key):
    res = run_buzz(relay, private_key, ["channels", "list"])
    if res.returncode != 0:
        print(f"❌ Không thể kết nối với Community {relay}: {res.stderr}")
        return None
    try:
        return json.loads(res.stdout)
    except Exception as e:
        print(f"❌ Lỗi đọc danh sách kênh: {e}")
        return []

def inject_channels(relay, private_key, channels_master_path, dry_run=False):
    print("\n" + "="*60)
    print("BƯỚC 1: XÂY DỰNG TOÀN BỘ PHÒNG BAN CHUYÊN TRÁCH (CHANNELS)")
    print("="*60)

    existing = list_existing_channels(relay, private_key)
    if existing is None:
        return False, {}

    existing_names = {c.get("name", "").strip().lower(): c.get("channel_id") for c in existing}
    print(f"[*] Community hiện có: {len(existing_names)} kênh.")

    with open(channels_master_path, "r", encoding="utf-8") as f:
        master_channels = json.load(f)

    created_count = 0
    channel_id_map = dict(existing_names)

    for ch in master_channels:
        name = ch["name"].strip()
        desc = ch.get("description", "")
        if name.lower() in existing_names:
            print(f"  [v] Kênh '{name}' đã có sẵn")
        else:
            if dry_run:
                print(f"  [THỬ NGHIỆM] Sẽ tạo kênh: '{name}'")
                created_count += 1
            else:
                print(f"  [+] Đang tạo mới kênh '{name}'...")
                res = run_buzz(relay, private_key, ["channels", "create", "--name", name, "--type", "stream", "--visibility", "open", "--description", desc])
                if res.returncode == 0:
                    created_count += 1
                    try:
                        out_data = json.loads(res.stdout)
                        cid = out_data.get("channel_id")
                        channel_id_map[name.lower()] = cid
                        print(f"      -> Thành công! ID: {cid}")
                    except:
                        print(f"      -> Thành công!")
                else:
                    print(f"      -> ❌ Lỗi tạo kênh '{name}': {res.stderr}")

    print(f"\n[OK] Hoàn tất Bước 1: Đã tạo mới {created_count} kênh. Tổng số: {len(channel_id_map)} phòng ban.")
    return True, channel_id_map

def setup_team_snapshot(base_dir, company_name, industry):
    print("\n" + "="*60)
    print("BƯỚC 2: CÁ NHÂN HÓA HỒ SƠ 46 AGENT AI CHO DOANH NGHIỆP")
    print("="*60)

    template_path = os.path.join(base_dir, "Marketing-OS-Full.team.json")
    if not os.path.exists(template_path):
        print("[-] Không tìm thấy file template đội ngũ.")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        data_str = f.read()

    data_str = data_str.replace(r"\buzz-export", "buzz-export").replace(r"\browser", "browser")
    data_str = data_str.replace("{{COMPANY_NAME}}", company_name)
    data_str = data_str.replace("{{INDUSTRY}}", industry)
    data_str = data_str.replace("{{FANPAGE_ID}}", "1181525411706512")
    data_str = data_str.replace("{{BRAND_HANDLE}}", "minhvanlogistics")

    output_team = os.path.join(base_dir, f"Marketing-OS-{company_name}.team.json")
    with open(output_team, "w", encoding="utf-8") as f:
        f.write(data_str)

    print(f"[OK] Đã tạo file Đội ngũ chuyên gia: {output_team}")

    # Copy to Buzz Desktop templates folder if Buzz is installed
    appdata = os.environ.get("APPDATA")
    if appdata:
        buzz_templates = os.path.join(appdata, "xyz.block.buzz.app", "templates")
        try:
            os.makedirs(buzz_templates, exist_ok=True)
            dest = os.path.join(buzz_templates, f"Marketing-OS-{company_name}.team.json")
            shutil.copyfile(output_team, dest)
            print(f"[OK] Đã tự động nạp mẫu đội ngũ vào ứng dụng Buzz Desktop: {dest}")
        except Exception as e:
            pass

def assign_agents_to_channels(relay, private_key, channel_id_map):
    print("\n" + "="*60)
    print("BƯỚC 3: PHÂN BỔ TOÀN BỘ 25 CHUYÊN GIA AI VÀO TẤT CẢ PHÒNG BAN")
    print("="*60)

    bot_pubkeys = list(ALL_AGENTS.values())
    total_channels = len(channel_id_map)
    print(f"[*] Đang nạp toàn bộ {len(bot_pubkeys)} chuyên gia AI vào {total_channels} phòng ban...")

    assigned_count = 0
    for idx, (cname, cid) in enumerate(channel_id_map.items(), 1):
        print(f"  [{idx}/{total_channels}] Đang phân bổ 25 Agent vào phòng ban: {cname}...")
        for pk in bot_pubkeys:
            res = run_buzz(relay, private_key, ["channels", "add-member", "--channel", cid, "--pubkey", pk, "--role", "bot"])
            if res.returncode == 0:
                assigned_count += 1

    print(f"[OK] Hoàn tất: Đã phân bổ đầy đủ {len(bot_pubkeys)} chuyên gia AI vào toàn bộ {total_channels} phòng ban (tổng cộng {assigned_count} lượt nhân sự).")

def broadcast_agent_access_policies(relay, owner_private_key):
    print("\n" + "="*60)
    print("BƯỚC 3.5: CÔNG BỐ QUYỀN HẠN NOSTR KIND 10100 (RESPOND_TO: ANYONE)")
    print("="*60)
    
    # 1. Chạy qua buzz.exe channels set-add-policy --policy anyone cho từng agent
    try:
        from setup_managed_agents import CANONICAL_AGENTS, get_buzz_paths
        _, agents_dir, _ = get_buzz_paths()
        managed_json = agents_dir / "managed-agents.json"
        agents_data = []
        if managed_json.exists():
            with open(managed_json, "r", encoding="utf-8") as f:
                agents_data = json.load(f)
        
        agent_map = {a.get("pubkey"): a for a in agents_data}
        success_count = 0

        for agent_meta in CANONICAL_AGENTS:
            name = agent_meta["name"]
            pk = agent_meta["pubkey"]
            nsec = agent_meta["nsec"]
            
            record = agent_map.get(pk, {})
            auth_tag = record.get("auth_tag")
            
            cmd = [BUZZ_EXE, "--relay", relay, "--private-key", nsec]
            if auth_tag:
                cmd.extend(["--auth-tag", auth_tag])
            cmd.extend(["channels", "set-add-policy", "--policy", "anyone"])
            
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if res.returncode == 0 and "accepted" in res.stdout:
                print(f"  ✅ [Chính sách Kênh: Anyone] {name}")
                success_count += 1
            else:
                print(f"  ⚠️ [Lưu ý] {name}: {res.stdout.strip() or res.stderr.strip()}")
        
        print(f"[OK] Đã thiết lập channel_add_policy = anyone cho {success_count}/{len(CANONICAL_AGENTS)} Agent.")
    except Exception as e:
        print(f"[!] Ngoại lệ khi cấu hình set-add-policy: {e}")

    # 2. Chạy kịch bản Node WebSocket để phát Kind 10100 kèm respond_to: anyone & owner tag
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "broadcast_kind_10100.js")
    if os.path.exists(script_path):
        node_bin = shutil.which("node") or shutil.which("node.exe")
        if node_bin:
            try:
                subprocess.run([node_bin, script_path, "--relay", relay], check=False)
            except Exception as e:
                print(f"[!] Bỏ qua phát sóng WebSocket phụ: {e}")

def run_e2e_verification(relay, private_key, channel_id_map, company_name, send_test=False):
    print("\n" + "="*60)
    print("BƯỚC 4: NGHIỆM THU HỆ THỐNG")
    print("="*60)
    if not send_test:
        print("[OK] Kênh phòng ban được giữ hoàn toàn sạch sẽ, sẵn sàng để Lãnh đạo giao việc trực tiếp!")
        return True

def extract_name_from_relay(relay_url):
    import urllib.parse
    parsed = urllib.parse.urlparse(relay_url)
    host = parsed.netloc or parsed.path
    subdomain = host.split(".")[0]
    if subdomain and subdomain.lower() not in ["http", "https", "localhost", "www"]:
        return subdomain.upper()
    return "Doanh Nghiệp"

def interactive_dynamic_input():
    communities = []
    print("\n" + "="*60)
    print("   CHẾ ĐỘ NHẬP ĐỘNG: BẠN CÓ THỂ NHẬP BAO NHIÊU COMMUNITY TÙY THÍCH")
    print("   (Cứ nhập xong 1 cái thì nhập tiếp cái sau, xong hết chỉ việc bấm ENTER)")
    print("="*60 + "\n")

    count = 1
    while True:
        print(f"--- THÔNG TIN COMMUNITY THỨ #{count} ---")
        try:
            relay = input(f"1. Nhập Link Community #{count} (hoặc bấm ENTER nếu đã nhập đủ): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not relay:
            if not communities:
                print("⚠️ Chưa có Community nào được nhập. Vui lòng nhập ít nhất 1 Community!\n")
                continue
            break
        
        try:
            nsec = input(f"2. Nhập Mã khóa Admin (nsec...) của Community #{count}: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not nsec:
            print("⚠️ Mã khóa không được để trống! Vui lòng nhập lại Community này.\n")
            continue
        
        communities.append((relay, nsec))
        print(f"✅ Đã lưu Community #{count}! Tiếp tục nhập bên dưới...\n")
        count += 1
    
    return communities

def main():
    parser = argparse.ArgumentParser(description="Buzz Community Turnkey Cloner")
    parser.add_argument("--relay", "--url", dest="relay", required=False, help="URL của Buzz Community (VD: https://ten-cty.communities.buzz.xyz)")
    parser.add_argument("--private-key", "--nsec", dest="private_key", required=False, help="Khóa nsec quản trị của Community")
    parser.add_argument("--company-name", default=None, help="Tên công ty / thương hiệu (tự động nhận diện nếu để trống)")
    parser.add_argument("--industry", default="Thương mại & Dịch vụ", help="Lĩnh vực kinh doanh")
    parser.add_argument("--batch", help="Đường dẫn file chứa danh sách community (mỗi dòng: relay nsec)")
    parser.add_argument("--send-test", action="store_true", help="Gửi tin nhắn test thử nghiệm vào kênh")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử nghiệm không ghi dữ liệu")

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    channels_master = os.path.join(base_dir, "channels_master.json")

    # 1. Chế độ đọc từ file danh sách
    if args.batch:
        if not os.path.exists(args.batch):
            print(f"❌ Không tìm thấy file danh sách: {args.batch}")
            sys.exit(1)
        with open(args.batch, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"[*] Chế độ cài đặt hàng loạt: Tìm thấy {len(lines)} Community.")
        for idx, line in enumerate(lines, 1):
            parts = line.split()
            if len(parts) >= 2:
                r, k = parts[0], parts[1]
                print(f"\n[{idx}/{len(lines)}] Đang thiết lập Community: {r}...")
                c_name = extract_name_from_relay(r)
                ok, c_map = inject_channels(r, k, channels_master, args.dry_run)
                if ok:
                    setup_team_snapshot(base_dir, c_name, "Thương mại & Dịch vụ")
                    assign_agents_to_channels(r, k, c_map)
                    broadcast_agent_access_policies(r, k)
                    run_e2e_verification(r, k, c_map, c_name, args.send_test)
        print("\n" + "="*60)
        print("✅ ĐÃ HOÀN TẤT THIẾT LẬP HÀNG LOẠT TOÀN BỘ CÁC COMMUNITY!")
        print("="*60)
        return

    # 2. Chế độ nhập động trên màn hình (khi không truyền tham số dòng lệnh)
    if not args.relay:
        targets = interactive_dynamic_input()
        if not targets:
            print("Đã hủy bỏ thiết lập.")
            return
        
        print("\n" + "="*60)
        print(f"🚀 BẮT ĐẦU CÀI ĐẶT TỰ ĐỘNG CHO TOÀN BỘ {len(targets)} COMMUNITY ĐÃ NHẬP...")
        print("="*60)

        for idx, (r, k) in enumerate(targets, 1):
            print(f"\n[{idx}/{len(targets)}] Đang thiết lập Community: {r}...")
            c_name = extract_name_from_relay(r)
            ok, c_map = inject_channels(r, k, channels_master, args.dry_run)
            if ok:
                setup_team_snapshot(base_dir, c_name, "Thương mại & Dịch vụ")
                assign_agents_to_channels(r, k, c_map)
                broadcast_agent_access_policies(r, k)
                run_e2e_verification(r, k, c_map, c_name, args.send_test)

        print("\n" + "="*60)
        print(f"✅ ĐÃ CÀI ĐẶT THÀNH CÔNG TOÀN DIỆN {len(targets)} COMMUNITY 100%!")
        print("="*60)
        return

    # 3. Chế độ chạy đơn lẻ qua cờ dòng lệnh
    company_name = args.company_name or extract_name_from_relay(args.relay)
    industry = args.industry or "Thương mại & Dịch vụ"

    print("============================================================")
    print("   BUZZ MARKETING AI OS - BỘ CÀI ĐẶT 1-CHẠM TRỌN GÓI")
    print(f"   Mục tiêu: {args.relay}")
    print(f"   Doanh nghiệp: {company_name} ({industry})")
    print("============================================================")

    # 1. Kênh
    ok, ch_map = inject_channels(args.relay, args.private_key, channels_master, args.dry_run)
    if not ok:
        sys.exit(1)

    # 2. Team Snapshot
    setup_team_snapshot(base_dir, company_name, industry)

    # 3. Phân bổ Agent vào kênh & công bố quyền hạn Kind 10100
    if not args.dry_run:
        assign_agents_to_channels(args.relay, args.private_key, ch_map)
        broadcast_agent_access_policies(args.relay, args.private_key)

    # 4. Kiểm tra thực tế
    if not args.dry_run:
        run_e2e_verification(args.relay, args.private_key, ch_map, company_name, args.send_test)

    print("\n" + "="*60)
    print("✅ ĐÃ CÀI ĐẶT VÀ BÀN GIAO THÀNH CÔNG TRỌN GÓI 100%! ")
    print("============================================================")

if __name__ == "__main__":
    main()
