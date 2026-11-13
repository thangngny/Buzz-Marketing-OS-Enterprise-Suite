import sys, json, time, re, unicodedata
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.append(r"C:\Users\Admin\marketing-ai-system\src")

from marketing_system.config import Settings
from marketing_system.constants import Environment
from marketing_system.connectors.zoho import ZohoConnector

CACHE_FILE = Path(r"C:\Users\Admin\.buzz\tools\zoho_live_vat_cache.json")

def norm_digits(v):
    return re.sub(r"\D", "", str(v or ""))

def ascii_fold(v):
    text = unicodedata.normalize("NFKD", str(v or "")).upper()
    return "".join(c for c in text if not unicodedata.combining(c))

def norm_text(v):
    text = ascii_fold(v)
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9]+", " ", text)).strip()

def build_cache(force=False):
    if not force and CACHE_FILE.exists():
        # Check cache age (valid for 4 hours)
        mtime = CACHE_FILE.stat().st_mtime
        if time.time() - mtime < 14400:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            print(f"Loaded existing Zoho live cache: {len(data['vats'])} VATs, {len(data['names'])} names (Updated: {data['updated_at']})")
            return data

    settings = Settings.from_env()
    settings.environment = Environment.PRODUCTION
    conn = ZohoConnector(settings)
    token, domain = conn._access_context()

    vats = set()
    names = set()

    # 1. Accounts
    print("Fetching live Accounts from Zoho...")
    page = 1
    while True:
        url = f"{domain.rstrip('/')}/crm/v8/Accounts?fields=id,Account_Name,VAT_number&per_page=200&page={page}"
        resp = conn.request("GET", url, headers={"Authorization": f"Zoho-oauthtoken {token}"})
        if not resp.is_success or resp.status_code == 204:
            break
        items = resp.json().get("data", [])
        if not items:
            break
        for a in items:
            v = norm_digits(a.get("VAT_number"))
            if v and len(v) in (10, 13, 14): vats.add(v)
            n = norm_text(a.get("Account_Name"))
            if n: names.add(n)
        if len(items) < 200:
            break
        page += 1

    print(f"Accounts processed: {page} pages. VATs so far: {len(vats)}")

    # 2. Leads
    print("Fetching live Leads from Zoho...")
    page = 1
    while True:
        url = f"{domain.rstrip('/')}/crm/v8/Leads?fields=id,Company,VAT_Number&per_page=200&page={page}"
        resp = conn.request("GET", url, headers={"Authorization": f"Zoho-oauthtoken {token}"})
        if not resp.is_success or resp.status_code == 204:
            break
        items = resp.json().get("data", [])
        if not items:
            break
        for l in items:
            v = norm_digits(l.get("VAT_Number"))
            if v and len(v) in (10, 13, 14): vats.add(v)
            n = norm_text(l.get("Company"))
            if n: names.add(n)
        if len(items) < 200:
            break
        page += 1

    print(f"Leads processed: {page} pages. Total VATs: {len(vats)}, Names: {len(names)}")

    payload = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vats": sorted(vats),
        "names": sorted(names)
    }
    CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved live Zoho cache to {CACHE_FILE}")
    return payload

if __name__ == "__main__":
    build_cache(force=True)
