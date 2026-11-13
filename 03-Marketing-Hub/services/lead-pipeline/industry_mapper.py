"""
Minh Van Logistics - Official CRM Industry Code Mapper.
Maps candidate companies to the exact Industry Code, Industry Name (EN & VN),
and Description strictly adhering to CRM_Industry_Codes.xlsx.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

JSON_PATH = Path(r"C:\Users\Admin\.buzz\tools\CRM_Industry_Codes.json")


def ascii_fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or "")).upper()
    return "".join(c for c in text if not unicodedata.combining(c))


def norm_search(text: str) -> str:
    folded = ascii_fold(text)
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9]+", " ", folded)).strip().lower()


class IndustryMapper:
    _instance: Optional[IndustryMapper] = None

    def __init__(self, json_path: Path = JSON_PATH):
        self.json_path = json_path
        self.codes: List[Dict[str, str]] = []
        self._load()

    @classmethod
    def get_instance(cls) -> IndustryMapper:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load(self):
        if not self.json_path.exists():
            return
        try:
            data = json.loads(self.json_path.read_text(encoding="utf-8"))
            # Skip header row (row 0)
            for item in data[1:]:
                code = str(item.get("B") or "").strip()
                name_en = str(item.get("C") or "").strip()
                desc_en = str(item.get("E") or "").strip()
                group_vn = str(item.get("F") or "").strip()
                name_vn = str(item.get("G") or "").strip()
                desc_vn = str(item.get("H") or "").strip()
                combine = str(item.get("D") or "").strip()

                if code:
                    search_blob = norm_search(f"{code} {name_en} {name_vn} {desc_en} {desc_vn} {group_vn} {combine}")
                    self.codes.append({
                        "code": code,
                        "name_en": name_en,
                        "name_vn": name_vn,
                        "desc_vn": desc_vn,
                        "desc_en": desc_en,
                        "group_vn": group_vn,
                        "search_blob": search_blob
                    })
        except Exception:
            pass

    def match(self, product_or_text: str, default_code: str = "HLS-003") -> Dict[str, str]:
        """
        Matches a given product / company description to the best matching CRM Industry Code.
        Returns a dict with:
        {
            "Industry_Code": "HLS-003",
            "Industry_Name_EN": "Medical Equipment & Healthcare",
            "Industry_Name_VN": "Thiết bị y tế & Chăm sóc sức khỏe",
            "Industry_Description": "...",
            "Industry_Full": "HLS-003 - Thiết bị y tế & Chăm sóc sức khỏe"
        }
        """
        query = norm_search(product_or_text)

        # 1. Exact rules / common logistics ICP wedges
        if any(w in query for w in ["y te", "medical", "benh vien", "nha khoa", "rang ham mat", "sieu am", "x quang", "noi soi"]):
            return self.get_by_code("HLS-003")
        if any(w in query for w in ["duoc", "pharma", "thuoc", "sinh hoc", "vaccine", "duoc pham"]):
            return self.get_by_code("HLS-001")
        if any(w in query for w in ["may moc", "machinery", "cnc", "co khi", "thiet bi nang", "dong co"]):
            return self.get_by_code("IND-002")
        if any(w in query for w in ["dien tu", "electronic", "chip", "semiconductor", "linh kien dien tu", "pcb", "vi mach"]):
            return self.get_by_code("IND-004")
        if any(w in query for w in ["hoa chat", "chemical", "dung moi", "nguyen lieu hoa chat"]):
            return self.get_by_code("IND-005")
        if any(w in query for w in ["xu ly nuoc", "water treatment", "loc nuoc", "moi truong nuoc"]):
            return self.get_by_code("IND-004")

        # 2. Score-based matching against search blobs
        tokens = query.split()
        best_match = None
        highest_score = 0

        for entry in self.codes:
            score = 0
            for t in tokens:
                if len(t) >= 3 and t in entry["search_blob"]:
                    score += 1
            if score > highest_score:
                highest_score = score
                best_match = entry

        if best_match and highest_score >= 2:
            return {
                "Industry_Code": best_match["code"],
                "Industry_Name_EN": best_match["name_en"],
                "Industry_Name_VN": best_match["name_vn"],
                "Industry_Description": best_match["desc_vn"],
                "Industry_Full": f"{best_match['code']} - {best_match['name_vn']}"
            }

        return self.get_by_code(default_code)

    def get_by_code(self, code: str) -> Dict[str, str]:
        for entry in self.codes:
            if entry["code"].upper() == code.upper():
                return {
                    "Industry_Code": entry["code"],
                    "Industry_Name_EN": entry["name_en"],
                    "Industry_Name_VN": entry["name_vn"],
                    "Industry_Description": entry["desc_vn"],
                    "Industry_Full": f"{entry['code']} - {entry['name_vn']}"
                }
        # Fallback if not found
        return {
            "Industry_Code": code,
            "Industry_Name_EN": "Medical Equipment & Healthcare",
            "Industry_Name_VN": "Thiết bị y tế & Chăm sóc sức khỏe",
            "Industry_Description": "Thiết bị y tế, vật tư tiêu hao phòng mổ và máy móc chẩn đoán hình ảnh",
            "Industry_Full": f"{code} - Thiết bị y tế & Chăm sóc sức khỏe"
        }
