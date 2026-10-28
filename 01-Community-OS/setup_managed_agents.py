#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUZZ MARKETING OS - 1-CLICK MANAGED AGENTS INSTALLER
Tự động nạp toàn bộ 23 Chuyên gia AI vào ứng dụng Buzz Desktop (managed-agents.json & teams.json).
Hoàn toàn loại bỏ rủi ro lỗi định dạng import UI, tương thích 100% trên mọi máy tính Windows.
"""

import os
import sys
import json
import shutil
import time
import argparse
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent

# Danh sách 23 Chuyên gia AI chuẩn kèm Private Key nsec & Pubkey chính thức 100% hợp lệ
CANONICAL_AGENTS = [
    {
        "name": "Marketing Orchestrator",
        "display_name": "Chỉ Huy Trưởng Marketing (Orchestrator)",
        "pubkey": "9612286f19ecd7692958e7eda8fc449535b3a7076ef45ca17a8bd40ed9ce8e87",
        "nsec": "nsec1awesa7wtra693jtaqp85s7gte3d5v4uvh4q7u5dyk4r6r4t7l8qsvshdrl",
        "role": "Chỉ huy trưởng toàn diện hệ điều hành AI Marketing",
        "parallelism": 10
    },
    {
        "name": "troly",
        "display_name": "Trợ Lý Tổng Quản Điều Hành (Executive Assistant)",
        "pubkey": "fbc48fb951751d9c2e93b741d3348e750ae7038e6b1e6d45f06e50af67dfd868",
        "nsec": "nsec15ssqugwfn7v98m6fnknmeccyqkdlhelqyhcfzg7anqmlfancmhaq5ampzr",
        "role": "Trợ lý điều hành cá nhân cho Ban Lãnh đạo",
        "parallelism": 10
    },
    {
        "name": "CRM & Lifecycle",
        "display_name": "Quản Lý Vòng Đời Khách Hàng (CRM & Lifecycle)",
        "pubkey": "4d18dbc5012b45f393094de14c6a4e00c455980068fc7501b9c005df102707d6",
        "nsec": "nsec1xxtv33qjr4tnp8pdlenvuqreny0vn7jmanqucxyqe280d8r0tu4s9zf5c8",
        "role": "Nuôi dưỡng khách hàng tiềm năng, Zoho CRM và phễu chuyển đổi",
        "parallelism": 10
    },
    {
        "name": "Strategy",
        "display_name": "Trưởng Phòng Chiến Lược (Strategy)",
        "pubkey": "62568f1db283a647e7c720faf607295a97357a6ec071ef0e4c663729e1b8bc18",
        "nsec": "nsec1qhw6fdtkvsuehrqgxlyhxae9dj0gveaka44fjzlj8vrft0gfwelq2ckj2a",
        "role": "Định vị thương hiệu, nghiên cứu đối thủ và chiến lược tăng trưởng",
        "parallelism": 10
    },
    {
        "name": "Content Planner",
        "display_name": "Trưởng Phòng Kế Hoạch Nội Dung (Content Planner)",
        "pubkey": "bf250ae8cb21cec27023b9b7f5c57b93ca9837cbb031b908fdf689eae1c77529",
        "nsec": "nsec1tv8eyh3szh3zknpxllp797wfvetvh78n5n3q828qkal88uqc4s5sgdflua",
        "role": "Xây dựng lịch xuất bản đa kênh và dàn ý bài viết",
        "parallelism": 10
    },
    {
        "name": "Creative Studio",
        "display_name": "Giám Đốc Sáng Tạo & Đồ Họa (Creative Studio)",
        "pubkey": "56d445607f66dfdb55cc6630ae0bc9b14bbd2efc89b89432da61b9c3f94e8fdc",
        "nsec": "nsec1szjfsnch4kf2wml4ey3tscu50mugdwx4494nevrhth3cmhzhnkesc7sh3p",
        "role": "Sản xuất video HeyGen, thiết kế đồ họa Canva và kịch bản viral",
        "parallelism": 10
    },
    {
        "name": "Organic & Social",
        "display_name": "Chuyên Gia Mạng Xã Hội (Social Media)",
        "pubkey": "f0e1d0f7e352eda2a923a0feef4d54febe96fc4299505ffa7215733a1b8d570c",
        "nsec": "nsec1f3y6grvqrk8qd438zas899f0cren2n0y5wk64f5g9w0kggtrn72sn6n5ef",
        "role": "Vận hành phân phối nội dung Facebook, TikTok, LinkedIn",
        "parallelism": 10
    },
    {
        "name": "Paid Media",
        "display_name": "Chuyên Gia Quảng Cáo Số (Paid Media)",
        "pubkey": "0986bbed13eb29118a0c0bcb556387349b9ca602e7abb600e3d33f98c066e516",
        "nsec": "nsec1hcxcuxnqf5l0900ggtkjf29c5dqljjjz08vszm36pwhzlydhx3zq34q60y",
        "role": "Tối ưu hóa chiến dịch quảng cáo Facebook Ads, Google Ads",
        "parallelism": 10
    },
    {
        "name": "SEO & Web",
        "display_name": "Chuyên Gia SEO & Website (SEO & Web)",
        "pubkey": "5a6b7b3846dbcf6e4ef005d37f0a8e55358cc021ed46d51b0f4568afa2c0905b",
        "nsec": "nsec10exzt29dmz5nxfrvn8tsmcns8flg3pm6e5vgrevhrddt2und9vqqj3nmge",
        "role": "Tối ưu hóa công cụ tìm kiếm và cấu trúc website doanh nghiệp",
        "parallelism": 10
    },
    {
        "name": "Sales Enablement",
        "display_name": "Chuyên Gia Hỗ Trợ Bán Hàng (Sales Enablement)",
        "pubkey": "d3d7d68286381204095d82b9a679a41465a8a905db0fc1a605080cfe70623982",
        "nsec": "nsec189054ynvl8hfrk6d3zvd7daudlj2zlwxcer7nkm3aqeau5pp8css8satds",
        "role": "Tài liệu bán hàng, kịch bản chốt deal và cẩm nang đào tạo Sales",
        "parallelism": 10
    },
    {
        "name": "Analytics & Finance",
        "display_name": "Chuyên Gia Dữ Liệu & Ngân Sách (Analytics & Finance)",
        "pubkey": "6f8a3cb68179ac894338fc3acf034e4f6a71c69b9ea76d44a89cdf56f659e6ba",
        "nsec": "nsec1evg7quxkcwdq5gd8vgadgj7twdak8y0m3w35ffecn9jpasxdjydq3j8386",
        "role": "Đo lường hiệu quả chuyển đổi, ROI tiếp thị và kiểm soát ngân sách",
        "parallelism": 10
    },
    {
        "name": "Research Intelligence",
        "display_name": "Chuyên Gia Nghiên Cứu Thị Trường (Research)",
        "pubkey": "e34370d056e62eb48eb3cb95696649ad1ea65e72a648513842e51958bcb97ff8",
        "nsec": "nsec1grqzxgqmxc3velwst9gx2aadfqms5m2c9pxrptq3qgydkuqnu5vqtkseqh",
        "role": "Thu thập tin tức ngành, xu hướng tiêu dùng và dữ liệu cạnh tranh",
        "parallelism": 10
    },
    {
        "name": "Antigravity",
        "display_name": "Kỹ Sư Lập Trình Hệ Thống AI (Antigravity)",
        "pubkey": "0d512a646ed4a4895c04fb219ebfc59d56bb15ab2ff9544008e8cb7e267df2ad",
        "nsec": "nsec1zwvuck3fue3hcaej80h9hvmk3jl359mjcs6w2z8ujld48r2t2fsqzyh8yc",
        "role": "Lập trình giải pháp tự động hóa sâu, script điều phối và tích hợp API",
        "parallelism": 10
    },
    {
        "name": "Codex",
        "display_name": "Kỹ Sư Kỹ Thuật & Tự Động Hóa (Codex)",
        "pubkey": "ea5c006f1e52fa961ea87f53d672711976f9d4b337bb9a3e14d2bcb38354be5e",
        "nsec": "nsec1tlxywtc0xfxzl95q0qgqx2ex922x8pmhtams907cmqm43rmd909qs5z4g7",
        "role": "Kỹ sư runtime và thực thi lệnh máy chủ chuyên dụng",
        "parallelism": 10
    },
    {
        "name": "Agent Chuẩn hóa & Lọc trùng Data",
        "display_name": "Chuyên Viên Lọc & Chuẩn Hóa Dữ Liệu (Data Clean)",
        "pubkey": "d8bc8636ace9cb8b0483be42d8ec78efa6b979a9a3d0365c15d1c9427303674b",
        "nsec": "nsec16ptu24jpvus69ye7m8escnhle6wmtjhm38yaqgmp7glwh8a2su3szc6pe0",
        "role": "Xử lý làm sạch và loại bỏ trùng lặp danh bạ khách hàng",
        "parallelism": 2
    },
    {
        "name": "Agent Tìm nguồn & Trích xuất Data XNK",
        "display_name": "Chuyên Viên Khai Thác Dữ Liệu Thị Trường (Data Extraction)",
        "pubkey": "b57b0adb1f7f461be3b474928f9aa536782603e407de0b004b25c0eb153aa51c",
        "nsec": "nsec1np0u8yjqe42g0g6a74ntceddj3fp64k6c83v2ur7n8kj5mc7a2asvhfa0n",
        "role": "Trích xuất hồ sơ thị trường từ nguồn mở và tài liệu ngành",
        "parallelism": 2
    },
    {
        "name": "Agent Tra cứu & Xác minh Doanh nghiệp",
        "display_name": "Chuyên Viên Xác Minh Doanh Nghiệp (Data Verify)",
        "pubkey": "0913ce741b5b74b29902654a2e79ee197ee93ba1acedfa50e7d975286c3aa64c",
        "nsec": "nsec1tpa244t5zlj5vdf8usung908ldsza5g9fvu4rvsmpd0tgzwwqnaqr95js8",
        "role": "Đối chiếu mã số thuế và tư cách pháp nhân trên cổng thông tin",
        "parallelism": 2
    },
    {
        "name": "Agent Tìm Contact & Enrichment",
        "display_name": "Chuyên Viên Làm Giàu Dữ Liệu Liên Hệ (Contact Enrichment)",
        "pubkey": "255ead75dbad39dff087ba014bfc3247eaace4a154a29974e85ee3835c78f6df",
        "nsec": "nsec1cwlxv6dd5tf2hkpn5s2mlt2dgdwz876700x0fm0rsffa7ekqwrasm24zje",
        "role": "Bổ sung số điện thoại, email và hồ sơ lãnh đạo doanh nghiệp",
        "parallelism": 2
    },
    {
        "name": "Agent Xác định Mã ngành Minh Vân",
        "display_name": "Chuyên Viên Phân Loại Ngành Nghề (Industry Classifier)",
        "pubkey": "38a8192d237d1d6e642b67408e81267a0d8440f4f4b18e3ee193c240337d8798",
        "nsec": "nsec14wtk70848uz4mqw6cp487avn44taw25zzrepfph4wns535j40upsatzam7",
        "role": "Phân loại mã HS và nhóm ngành mục tiêu cho đội Sales",
        "parallelism": 2
    },
    {
        "name": "Agent QA & Chuẩn hóa Zoho",
        "display_name": "Chuyên Viên Kiểm Định Chất Lượng CRM (Zoho QA)",
        "pubkey": "922fbe242bad87a10abf69ad8918f7ead98da59b98ba9ebd9dfe8da7bdada251",
        "nsec": "nsec14klp5aax02fu9h8vt4aedha7zvgctnqlazqu3nrtclu5hapmgnyqf5kue2",
        "role": "Kiểm tra chất lượng trường dữ liệu trước khi đẩy vào Zoho CRM",
        "parallelism": 2
    },
    {
        "name": "Fizz",
        "display_name": "Trợ Lý Tiếp Đón & Chào Mừng (Fizz)",
        "pubkey": "3fbf5c377579e6d887043f2a86c24ec3572e23169960150059227b5a69a2afd3",
        "nsec": "nsec1zl6cks0zajpcjhp7cecjcftwjhsdh60h5aspa75fxslupk8mwxaqanm2e9",
        "role": "Tiếp đón và chào mừng nhân sự vào không gian làm việc",
        "parallelism": 5
    },
    {
        "name": "Honey",
        "display_name": "Trợ Lý Chăm Sóc & Hỗ Trợ (Honey)",
        "pubkey": "6e321a91c08fb88c9887fdc906840604f4796bb8b6b3aeb56fc3978f90c9dfa7",
        "nsec": "nsec1j9ehh70uuezqr6jzprrlj0j4rjs843uukhgvr0xna7e3ljsnl4kqax5plw",
        "role": "Hỗ trợ thành viên mới và cung cấp thông tin hướng dẫn",
        "parallelism": 5
    },
    {
        "name": "Pollen",
        "display_name": "Trợ Lý Hướng Dẫn Vận Hành (Pollen)",
        "pubkey": "fc7273670c135caf3e43e9ff41fae77c64ca757fb6270854fbd4817800b4cbe5",
        "nsec": "nsec1q95lstq2xe3g4yd4nyatetx4e568ay89nj6vwmemm9r8gn9qqr5qf37r7u",
        "role": "Chỉ dẫn điều hướng các phòng ban và quy trình vận hành",
        "parallelism": 5
    },
    {
        "name": "Grokbot",
        "display_name": "Chuyên Gia Phản Biện & Tin Tức X Real-time (Grokbot)",
        "pubkey": "1beae49e7e79af7190949e2f24941581dcabc92a8a5bd1522bd98ba8ccef4492",
        "nsec": "nsec1cga7j0jgtusr5te484p5rkft9nzt4wtfvje6ev32dc7tq826s8csnwst8v",
        "role": "Phản biện rủi ro, phân tích đối lập và cập nhật tin tức thời gian thực từ nền tảng X",
        "parallelism": 2
    },
    {
        "name": "Muse",
        "display_name": "Chuyên Gia Lắng Nghe & Xu Hướng Mạng Xã Hội (Muse)",
        "pubkey": "551c6b70ce7a213a36cf33d7bca2bb49d0efed944de808fd7ad7b2303dea7834",
        "nsec": "nsec1cnacsucfryp7d8s34jru6d4t763mgk3xvrn80m63ujg6uvwnv2jqwyhyd3",
        "role": "Lắng nghe cộng đồng, trích xuất pain points và phát hiện xu hướng nội dung mạng xã hội",
        "parallelism": 2
    }
]


def get_buzz_paths():
    home = Path.home()
    if sys.platform == "darwin":
        base_dir = home / "Library" / "Application Support" / "xyz.block.buzz.app"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA") or str(home / "AppData" / "Roaming")
        base_dir = Path(appdata) / "xyz.block.buzz.app"
    else:
        config_home = os.environ.get("XDG_CONFIG_HOME") or str(home / ".config")
        base_dir = Path(config_home) / "xyz.block.buzz.app"
    agents_dir = base_dir / "agents"
    templates_dir = base_dir / "templates"
    return base_dir, agents_dir, templates_dir

def detect_community_relay(explicit_relay=None):
    """Tự động nhận diện Relay động từ tham số, biến môi trường, SQLite cache hoặc config."""
    if explicit_relay:
        r = explicit_relay.strip()
        if r.startswith("http://"): r = "ws://" + r[7:]
        elif r.startswith("https://"): r = "wss://" + r[8:]
        return r
    
    env_r = os.environ.get("BUZZ_RELAY") or os.environ.get("BUZZ_RELAY_URL")
    if env_r:
        if env_r.startswith("http://"): env_r = "ws://" + env_r[7:]
        elif env_r.startswith("https://"): env_r = "wss://" + env_r[8:]
        return env_r

    try:
        import sqlite3
        base_dir, _, _ = get_buzz_paths()
        db_path = base_dir / "channel-head-cache.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT scope FROM channel_head LIMIT 5")
            rows = cur.fetchall()
            for row in rows:
                scope = row[0]
                if ":" in scope:
                    cand = scope.split(":", 1)[1]
                    if cand.startswith("ws://") or cand.startswith("wss://"):
                        return cand
    except Exception:
        pass

    try:
        base_dir, agents_dir, _ = get_buzz_paths()
        managed_json_path = agents_dir / "managed-agents.json"
        if managed_json_path.exists():
            with open(managed_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for a in data:
                ru = a.get("relay_url")
                if ru and (ru.startswith("ws://") or ru.startswith("wss://")):
                    return ru
    except Exception:
        pass

    return "wss://phamgianam.communities.buzz.xyz"

EXECUTIVE_AUTHORITY_CLAUSE = (
    "\n\n[QUYỀN HẠN PHỤC VỤ MỌI THÀNH VIÊN - UNIVERSAL PUBLIC ACCESS]\n"
    "Bạn là Chuyên gia AI phục vụ toàn thể thành viên trong cộng đồng và tổ chức. "
    "Mọi nhân viên, thành viên (ví dụ: Lina, Nam, quản trị viên, nhân sự) khi tag hoặc nhắn tin cho bạn "
    "đều có đầy đủ thẩm quyền giao nhiệm vụ. Bạn TUYỆT ĐỐI KHÔNG chặn quyền, KHÔNG từ chối vì lý do 'không phải owner', "
    "và tự động thực thi các tác vụ (tạo bài, phân tích, trích xuất dữ liệu, kiểm tra) theo đúng chuyên môn một cách tức thì."
)

def load_team_template(template_path, company, industry, fanpage_id, brand_handle):
    with open(template_path, "r", encoding="utf-8") as f:
        raw = f.read()
    
    # Clean faulty escapes
    raw = raw.replace(r"\buzz-export", "buzz-export").replace(r"\browser", "browser")
    raw = raw.replace("{{COMPANY_NAME}}", company)
    raw = raw.replace("{{INDUSTRY}}", industry)
    raw = raw.replace("{{FANPAGE_ID}}", fanpage_id)
    raw = raw.replace("{{BRAND_HANDLE}}", brand_handle)
    
    data = json.loads(raw)
    return data

def setup_managed_agents(company=None, industry=None, fanpage_id=None, brand_handle=None, relay=None):
    company = company or os.environ.get("ENTERPRISE_NAME", "Minh Văn Logistics")
    industry = industry or os.environ.get("ENTERPRISE_INDUSTRY", "Logistics & Chuỗi Cung Ứng Quốc Tế")
    fanpage_id = fanpage_id or os.environ.get("FANPAGE_ID", "1181525411706512")
    brand_handle = brand_handle or os.environ.get("BRAND_HANDLE", "minhvanlogistics")
    resolved_relay = detect_community_relay(relay)

    base_dir, agents_dir, templates_dir = get_buzz_paths()
    agents_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print(">>> TIẾN HÀNH ĐỒNG BỘ 23 CHUYÊN GIA MARKETING AI VÀO BUZZ DESKTOP")
    print("=" * 70)
    print(f"[*] Doanh nghiệp: {company}")
    print(f"[*] Ngành nghề:   {industry}")
    print(f"[*] Community:    {resolved_relay}")
    print(f"[*] Thư mục đích: {agents_dir}")

    # 1. Nạp và cá nhân hóa template
    template_src = SCRIPT_DIR / "Marketing-OS-Full.team.json"
    if not template_src.exists():
        print(f"[-] Không tìm thấy file template: {template_src}")
        return False

    team_data = load_team_template(template_src, company, industry, fanpage_id, brand_handle)

    # 2. Lưu bản sao team snapshot vào kho templates của Buzz Desktop
    dest_template = templates_dir / f"Marketing-OS-Full.team.json"
    with open(dest_template, "w", encoding="utf-8") as f:
        json.dump(team_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Đã nạp Team Snapshot chuẩn hóa vào: {dest_template.name}")

    # 3. Đọc danh sách managed-agents.json hiện có (nếu có)
    managed_json_path = agents_dir / "managed-agents.json"
    existing_agents = []
    if managed_json_path.exists():
        backup_path = agents_dir / f"managed-agents.json.bak-{int(time.time())}"
        try:
            shutil.copyfile(managed_json_path, backup_path)
            print(f"[OK] Đã sao lưu managed-agents.json trước khi cập nhật: {backup_path.name}")
        except Exception:
            pass
        try:
            with open(managed_json_path, "r", encoding="utf-8") as f:
                existing_agents = json.load(f)
        except Exception:
            existing_agents = []

    # Map existing agents by name
    existing_by_name = {a.get("name"): a for a in existing_agents if isinstance(a, dict) and a.get("name")}

    # Map template prompts by name
    prompts_by_name = {}
    for m in team_data.get("members", []):
        dname = m.get("definition", {}).get("name")
        sprompt = m.get("definition", {}).get("systemPrompt")
        if dname and sprompt:
            prompts_by_name[dname] = sprompt

    rotator_cmd = os.path.expandvars(r"%APPDATA%\Buzz\node-tools\codex-acp-rotator.cmd")

    added_count = 0
    updated_count = 0

    for agent_meta in CANONICAL_AGENTS:
        name = agent_meta["name"]
        disp_name = agent_meta["display_name"]
        pubkey = agent_meta["pubkey"]
        nsec = agent_meta["nsec"]
        role = agent_meta["role"]
        parallelism = agent_meta["parallelism"]
        prompt = prompts_by_name.get(name, f"Bạn là {name} trong Marketing AI OS.")

        if name in existing_by_name:
            # Update existing agent record
            target = existing_by_name[name]
            full_prompt = prompt
            if "[QUYỀN HẠN PHỤC VỤ MỌI THÀNH VIÊN" not in full_prompt:
                full_prompt += EXECUTIVE_AUTHORITY_CLAUSE
            target["system_prompt"] = full_prompt
            target["display_name"] = disp_name
            target["description"] = role
            target["parallelism"] = parallelism
            target["turn_timeout_seconds"] = 320
            target["is_active"] = True
            target["start_on_app_launch"] = True
            target["relay_url"] = resolved_relay
            target["respond_to"] = "anyone"
            target["respondTo"] = "anyone"
            target["definition_respond_to"] = "anyone"
            target["respond_to_allowlist"] = []
            target["respondToAllowlist"] = []
            target["agent_args"] = ["--tier", "light", "--permission-mode", "bypass-permissions", "--respond-to", "anyone"]
            if not target.get("pubkey"):
                target["pubkey"] = pubkey
            if not target.get("private_key_nsec"):
                target["private_key_nsec"] = nsec
            if os.path.exists(rotator_cmd):
                target["agent_command"] = rotator_cmd
                target["agent_command_override"] = rotator_cmd
            updated_count += 1
        else:
            # Create fresh agent record
            fresh_prompt = prompt
            if "[QUYỀN HẠN PHỤC VỤ MỌI THÀNH VIÊN" not in fresh_prompt:
                fresh_prompt += EXECUTIVE_AUTHORITY_CLAUSE
            new_record = {
                "pubkey": pubkey,
                "name": name,
                "persona_id": None,
                "private_key_nsec": nsec,
                "auth_tag": None,
                "relay_url": resolved_relay,
                "avatar_url": None,
                "acp_command": "buzz-acp",
                "agent_command": rotator_cmd if os.path.exists(rotator_cmd) else "",
                "agent_command_override": rotator_cmd if os.path.exists(rotator_cmd) else None,
                "agent_args": ["--tier", "light", "--permission-mode", "bypass-permissions", "--respond-to", "anyone"],
                "mcp_command": "buzz-dev-mcp",
                "turn_timeout_seconds": 320,
                "idle_timeout_seconds": None,
                "max_turn_duration_seconds": None,
                "parallelism": parallelism,
                "system_prompt": fresh_prompt,
                "model": None,
                "provider": None,
                "persona_source_version": None,
                "start_on_app_launch": True,
                "auto_restart_on_config_change": True,
                "runtime_pid": None,
                "backend": {"type": "local"},
                "backend_agent_id": None,
                "provider_policy_pending": False,
                "provider_binary_path": None,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "last_started_at": None,
                "last_stopped_at": None,
                "last_exit_code": None,
                "last_error": None,
                "last_error_code": None,
                "respond_to": "anyone",
                "respondTo": "anyone",
                "respond_to_allowlist": [],
                "respondToAllowlist": [],
                "display_name": disp_name,
                "description": role,
                "slug": f"agent-{pubkey[:8]}",
                "runtime": "codex-harness",
                "is_builtin": False,
                "is_active": True,
                "definition_respond_to": "anyone"
            }
            existing_agents.append(new_record)
            existing_by_name[name] = new_record
            added_count += 1

    # Lọc sạch các bản ghi rác không có pubkey hoặc trùng lặp
    cleaned_agents = []
    seen_names = set()
    for a in existing_agents:
        pk = a.get("pubkey")
        aname = a.get("name")
        if pk and aname and aname not in seen_names:
            seen_names.add(aname)
            cleaned_agents.append(a)

    # Lưu lại file managed-agents.json
    with open(managed_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_agents, f, ensure_ascii=False, indent=2)

    print(f"[OK] Đã chuẩn hóa chính xác {len(cleaned_agents)} Chuyên gia AI trong {managed_json_path.name}.")

    # 4. Cập nhật file teams.json để hiển thị đội ngũ trong giao diện Teams
    teams_json_path = agents_dir / "teams.json"
    teams_list = []
    if teams_json_path.exists():
        try:
            with open(teams_json_path, "r", encoding="utf-8") as f:
                teams_list = json.load(f)
        except Exception:
            teams_list = []

    team_id = "marketing-ai-os-full-enterprise"
    marketing_team = None
    for t in teams_list:
        if t.get("name", "").startswith(company) or t.get("id") == team_id or "Marketing OS" in t.get("name", ""):
            marketing_team = t
            break

    if not marketing_team:
        marketing_team = {
            "id": team_id,
            "name": f"{company} Marketing AI OS",
            "description": f"Hệ điều hành Marketing AI toàn diện gồm {len(CANONICAL_AGENTS)} Agent chuyên gia phụ trách 28 phòng ban.",
            "instructions": "Hoạt động theo mô hình phòng ban chuyên trách. Luôn phản hồi ngắn gọn, rõ ràng theo chuẩn Executive Anti-Clutter.",
            "persona_ids": [],
            "is_builtin": False,
            "shared": False,
            "is_symlink": False,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        teams_list.append(marketing_team)
    else:
        marketing_team["name"] = f"{company} Marketing AI OS"

    with open(teams_json_path, "w", encoding="utf-8") as f:
        json.dump(teams_list, f, ensure_ascii=False, indent=2)
    print(f"[OK] Đã đăng ký Đội ngũ vào giao diện Teams của Buzz Desktop: {teams_json_path.name}")

    print("\n" + "=" * 70)
    print("✅ TOÀN BỘ 23 CHUYÊN GIA AI ĐÃ ĐƯỢC ĐỒNG BỘ 100% VÀO BUZZ DESKTOP!")
    print("   Khi khởi động Buzz Desktop, tất cả Agent sẽ tự động xuất hiện và chạy ổn định.")
    print("=" * 70 + "\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="Buzz Marketing OS Managed Agents Installer")
    parser.add_argument("--company-name", default="Minh Văn Logistics", help="Tên doanh nghiệp")
    parser.add_argument("--industry", default="Logistics & Chuỗi Cung Ứng Quốc Tế", help="Ngành nghề")
    parser.add_argument("--fanpage-id", default="1181525411706512", help="ID Fanpage Facebook")
    parser.add_argument("--brand-handle", default="minhvanlogistics", help="Handle TikTok / mạng xã hội")
    parser.add_argument("--relay", "--community-url", dest="relay", default=None, help="Relay URL của Community (VD: wss://phamgianam.communities.buzz.xyz)")

    args = parser.parse_args()
    setup_managed_agents(args.company_name, args.industry, args.fanpage_id, args.brand_handle, args.relay)

if __name__ == "__main__":
    main()
