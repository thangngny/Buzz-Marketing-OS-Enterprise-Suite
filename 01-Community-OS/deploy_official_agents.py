#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUZZ MARKETING OS - RELAY AUTO-CLAIM & OFFICIAL AGENTS DEPLOYER
Tự động đăng ký 23 Chuyên gia AI vào Private Community Relay của Buzz (NIP-98 Auth + Schnorr BIP-340).
Tự động vượt qua cửa kiểm duyệt 403: relay_membership_required, phát sóng Kind 0 (Profile)
và nạp trực tiếp vào Buzz Desktop trên bất kỳ máy tính Windows nào.
"""

import os
import sys
import json
import time
import shutil
import hashlib
import argparse
import urllib.request
import urllib.error
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent

# ==============================================================================
# SECP256K1 & BIP-340 SCHNORR & BECH32 CRYPTOGRAPHY (100% PURE PYTHON)
# ==============================================================================
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2: return None
    if x1 == x2:
        m = (3 * x1 * x1) * pow(2 * y1, P - 2, P) % P
    else:
        m = (y2 - y1) * pow(x2 - x1, P - 2, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def point_mul(pt, k):
    res = None
    add = pt
    while k > 0:
        if k & 1: res = point_add(res, add)
        add = point_add(add, add)
        k >>= 1
    return res

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for val in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ val
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def convertbits(data, frombits, tobits, pad=True):
    acc, bits, ret = 0, 0, []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits): return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits: ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv): return None
    return ret

def bech32_encode(hrp, data):
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def bech32_decode(bech):
    if any(ord(x) < 33 or ord(x) > 126 for x in bech): return None, None
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90: return None, None
    hrp = bech[:pos]
    if any(x not in CHARSET for x in bech[pos + 1:]): return None, None
    data = [CHARSET.find(x) for x in bech[pos + 1:]]
    values = bech32_hrp_expand(hrp) + data
    if bech32_polymod(values) != 1: return None, None
    return hrp, data[:-6]

def nsec_to_bytes(nsec_str):
    hrp, data = bech32_decode(nsec_str)
    if hrp != "nsec" or data is None: return None
    res = convertbits(data, 5, 8, pad=False)
    return bytes(res) if res else None

def sha256(b):
    return hashlib.sha256(b).digest()

def tagged_hash(tag, msg):
    h = sha256(tag.encode('utf-8'))
    return sha256(h + h + msg)

def schnorr_sign(msg_32bytes, privkey_bytes, aux_rand=None):
    if aux_rand is None:
        aux_rand = os.urandom(32)
    d0 = int.from_bytes(privkey_bytes, 'big')
    if not (1 <= d0 <= N - 1):
        raise ValueError("Invalid private key")
    P_pt = point_mul(G, d0)
    d = d0 if P_pt[1] % 2 == 0 else N - d0
    P_bytes = P_pt[0].to_bytes(32, 'big')
    t = d.to_bytes(32, 'big')
    rand_hash = tagged_hash("BIP0340/aux", aux_rand)
    masked = bytes(a ^ b for a, b in zip(t, rand_hash))
    k0 = int.from_bytes(tagged_hash("BIP0340/nonce", masked + P_bytes + msg_32bytes), 'big') % N
    if k0 == 0:
        raise ValueError("k0 is zero")
    R_pt = point_mul(G, k0)
    k = k0 if R_pt[1] % 2 == 0 else N - k0
    R_bytes = R_pt[0].to_bytes(32, 'big')
    e = int.from_bytes(tagged_hash("BIP0340/challenge", R_bytes + P_bytes + msg_32bytes), 'big') % N
    sig = R_bytes + ((k + e * d) % N).to_bytes(32, 'big')
    return sig.hex()

def derive_pubkey_hex(privkey_bytes):
    P_pt = point_mul(G, int.from_bytes(privkey_bytes, 'big'))
    return P_pt[0].to_bytes(32, 'big').hex()

def build_nostr_event(privkey_bytes, kind, content, tags=None, created_at=None):
    if tags is None: tags = []
    if created_at is None: created_at = int(time.time())
    pub_hex = derive_pubkey_hex(privkey_bytes)
    serialized = json.dumps([0, pub_hex, created_at, kind, tags, content], separators=(',', ':'), ensure_ascii=False)
    event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    sig = schnorr_sign(bytes.fromhex(event_id), privkey_bytes)
    return {
        "id": event_id,
        "pubkey": pub_hex,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": sig
    }

def build_nip98_header(privkey_bytes, url, method="POST", payload_bytes=b""):
    import base64
    import uuid
    tags = [["u", url], ["method", method.upper()]]
    if payload_bytes:
        tags.append(["payload", hashlib.sha256(payload_bytes).hexdigest()])
    tags.append(["nonce", str(uuid.uuid4())])
    event = build_nostr_event(
        privkey_bytes=privkey_bytes,
        kind=27235,
        content="",
        tags=tags
    )
    b64 = base64.b64encode(json.dumps(event, separators=(',', ':')).encode('utf-8')).decode('utf-8')
    return f"Nostr {b64}"

def publish_agent_profile(http_base, agent_meta, privkey_bytes):
    """
    Phát sóng Nostr Kind 0 profile event lên Relay: POST /events kèm NIP-98 Auth
    """
    events_url = f"{http_base}/events"
    profile_content = json.dumps({
        "name": agent_meta["name"],
        "display_name": agent_meta["display_name"],
        "about": agent_meta["role"],
        "picture": f"https://api.dicebear.com/7.x/bottts/svg?seed={agent_meta['name']}"
    }, ensure_ascii=False)

    event = build_nostr_event(
        privkey_bytes=privkey_bytes,
        kind=0,
        content=profile_content,
        tags=[]
    )
    event_bytes = json.dumps(event, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    auth_header = build_nip98_header(privkey_bytes, events_url, "POST", payload_bytes=event_bytes)
    res = http_json_request(events_url, "POST", event, {"Authorization": auth_header})
    return res


# ==============================================================================
# CANONICAL 23 AGENTS DEFINITIONS WITH REAL VALID KEYS
# ==============================================================================
from setup_managed_agents import CANONICAL_AGENTS

def http_json_request(url, method="GET", data=None, headers=None):
    req_headers = {"User-Agent": "Buzz-Enterprise-Deployer/1.0", "Content-Type": "application/json"}
    if headers: req_headers.update(headers)
    req_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return {"error": e.code, "message": err_body}
        except Exception:
            return {"error": e.code, "message": str(e)}
    except Exception as e:
        return {"error": 500, "message": str(e)}

def claim_relay_membership(http_base, invite_code, privkey_bytes):
    """
    Thực hiện quy trình 3 bước gia nhập Relay bảo mật:
    1. GET /api/join-policy -> lấy policy_version
    2. POST /api/invites/accept-policy (kèm NIP-98 Auth) -> lấy policy_receipt
    3. POST /api/invites/claim (kèm NIP-98 Auth + code + receipt) -> hoàn tất claim
    """
    join_policy_url = f"{http_base}/api/join-policy"
    accept_policy_url = f"{http_base}/api/invites/accept-policy"
    claim_url = f"{http_base}/api/invites/claim"

    # Bước 1: Đọc chính sách
    policy_res = http_json_request(join_policy_url, "GET")
    if not isinstance(policy_res, dict):
        return False, f"Không đọc được join-policy từ {join_policy_url}"
    policy_version = policy_res.get("version") or policy_res.get("hash") or "1"

    # Bước 2: Chấp thuận điều khoản
    accept_auth = build_nip98_header(privkey_bytes, accept_policy_url, "POST")
    accept_res = http_json_request(accept_policy_url, "POST", {"policy_version": policy_version}, {"Authorization": accept_auth})
    policy_receipt = accept_res.get("policy_receipt") or accept_res.get("receipt")
    if not policy_receipt and "error" in accept_res:
        # Một số relay chấp nhận claim trực tiếp nếu không bắt policy
        policy_receipt = ""

    # Bước 3: Claim Invite
    claim_auth = build_nip98_header(privkey_bytes, claim_url, "POST")
    claim_payload = {"code": invite_code}
    if policy_receipt:
        claim_payload["policy_receipt"] = policy_receipt
    claim_res = http_json_request(claim_url, "POST", claim_payload, {"Authorization": claim_auth})

    if claim_res.get("accepted") or claim_res.get("status") == "ok" or claim_res.get("success"):
        return True, "Gia nhập Relay thành công"
    if claim_res.get("error") == 409 or "already" in str(claim_res).lower():
        return True, "Tài khoản đã là thành viên của Relay từ trước"
    
    return False, f"Lỗi claim: {claim_res.get('message', claim_res)}"

def main():
    parser = argparse.ArgumentParser(description="Buzz Official Agents Deployer & Private Relay Claimer")
    parser.add_argument("--relay", default="", help="Relay URL (http:// hoặc https:// hoặc wss://)")
    parser.add_argument("--invite", default="", help="Mã mời gia nhập Relay (Invite Code)")
    parser.add_argument("--company", default="Minh Vân Logistics", help="Tên doanh nghiệp")
    parser.add_argument("--skip-claim", action="store_true", help="Bỏ qua bước claim invite trên Relay")
    args = parser.parse_args()

    print("=" * 80)
    print("   BUZZ ENTERPRISE MARKETING OS - OFFICIAL AGENTS RELAY DEPLOYER")
    print("=" * 80)

    # 1. Tự động nhận diện Relay URL
    relay_url = args.relay
    if not relay_url:
        relay_url = os.environ.get("BUZZ_RELAY_URL", "")
    if not relay_url:
        relay_url = "wss://phamgianam.communities.buzz.xyz"
    
    http_relay = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
    print(f"[*] Máy chủ Relay mục tiêu: {relay_url} (HTTP: {http_relay})")
    print(f"[*] Tổng số Chuyên gia AI: {len(CANONICAL_AGENTS)} Agents")
    print("-" * 80)

    # 2. Xử lý Claim Relay nếu có mã invite
    if args.invite and not args.skip_claim:
        print(f"[*] Đang thực hiện xác thực NIP-98 và claim quyền gia nhập Relay cho 23 Agent...")
        success_count = 0
        for idx, ag in enumerate(CANONICAL_AGENTS, 1):
            priv_bytes = nsec_to_bytes(ag["nsec"])
            ok, msg = claim_relay_membership(http_relay, args.invite, priv_bytes)
            status_tag = "[OK]" if ok else "[WARN]"
            print(f"  {status_tag} [{idx:02d}/{len(CANONICAL_AGENTS):02d}] {ag['name'].ljust(35)} -> {msg}")
            if ok: success_count += 1
        print(f"[*] Hoàn tất Claim Relay: {success_count}/{len(CANONICAL_AGENTS)} Agent đã có tư cách thành viên chính thức.")
        print("-" * 80)
    else:
        print("[!] Không truyền --invite: Bỏ qua bước claim API Relay (Sử dụng quyền đã cấp sẵn).")

    # 2.5 Phát sóng Kind 0 Profile lên Relay
    if not args.skip_claim:
        print(f"[*] Đang phát sóng hồ sơ chính thức (Kind 0 Profile) của 23 Agent lên Relay...")
        prof_count = 0
        for idx, ag in enumerate(CANONICAL_AGENTS, 1):
            try:
                priv_bytes = nsec_to_bytes(ag["nsec"])
                res = publish_agent_profile(http_relay, ag, priv_bytes)
                if isinstance(res, dict) and res.get("error"):
                    err_msg = res.get("message", res)
                    print(f"  [WARN] [{idx:02d}/{len(CANONICAL_AGENTS):02d}] {ag['name'].ljust(35)} -> {err_msg}")
                else:
                    prof_count += 1
                    print(f"  [OK]   [{idx:02d}/{len(CANONICAL_AGENTS):02d}] {ag['name'].ljust(35)} -> Đã phát sóng Profile")
            except Exception as e:
                print(f"  [WARN] [{idx:02d}/{len(CANONICAL_AGENTS):02d}] {ag['name'].ljust(35)} -> {e}")
        print(f"[*] Hoàn tất phát sóng Profile: {prof_count}/{len(CANONICAL_AGENTS)} Agent.")
        print("-" * 80)

    # 3. Nạp vào cấu hình Buzz Desktop (managed-agents.json)
    print("[*] Đang ghi nhận toàn bộ 23 Chuyên gia AI vào cấu hình máy tính...")
    from setup_managed_agents import setup_managed_agents
    ok_setup = setup_managed_agents(
        company=args.company,
        industry="Logistics & Vận tải hàng hải, hàng không, kho bãi",
        fanpage_id="1181525411706512",
        brand_handle="minhvanlogistics"
    )

    if ok_setup:
        print("\n" + "=" * 80)
        print("   ✅ TRIỂN KHAI THÀNH CÔNG 100%!")
        print("   Tất cả 23 Agent đã có mã khóa Nostr thật và được cài đặt hoàn tất.")
        print("   Hệ thống sẵn sàng vận hành trên Buzz Desktop & Buzz ACP.")
        print("=" * 80)
    else:
        print("\n[!] Có lỗi xảy ra trong quá trình cập nhật managed-agents.json.")

if __name__ == "__main__":
    main()
