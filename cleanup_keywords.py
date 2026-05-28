# -*- coding: utf-8 -*-
"""
cleanup_keywords.py — แก้ keyword_map.csv ตามการรีวิวของผู้ใช้
- ลบ keyword ที่กว้างเกิน (match ผิด เช่น 'ชา' ติด 'กระชาย')
- ย้าย keyword บางตัวไป OUT_OF_SCOPE
- เพิ่ม keyword OUT_OF_SCOPE ใหม่
"""
import sys
import pandas as pd
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\nakit\OneDrive\Desktop\Healthier Choice")
KW_FILE = BASE / "keyword_map.csv"

df = pd.read_csv(KW_FILE)
print(f"Original: {len(df)} keywords")

# ── 1) ลบ keyword ที่กว้างเกินจนทำให้ map ผิด ──
REMOVE = {
    "ชา",                  # match "กระชาย" ผิด (มี keyword 'ชา' Conf 2)
    "ข้าว", "ผัด", "แกง",   # กว้างเกินสำหรับ meal
    "ผง", "ผงชง", "ผงพร้อมชง",  # ใช้ is_powder_product() ใน script แทน
    "แป้ง",                 # กว้างเกินสำหรับ bakery
    "หอย", "ปู", "กุ้ง",    # กว้างเกินสำหรับ fish_seafood
    "อาหารพร้อมบริโภค", "อาหารพร้อมปรุง",  # กว้างเกิน → meal โดยปริยาย
    "ผัดผัก", "สลัด", "สลัดผัก",
    "ขนมแห้ง", "ขนมรวมรส", "ขนมหวานสด",
    "สูตรหวานน้อย", "สูตรหวานปกติ", "ลดโซเดียม", "รสบาร์บีคิว",
    "แตงโม",
    "ขนม",
    "เครื่องดื่ม",           # กว้าง — เก็บก่อนแต่ลด confidence (จัดการด้านล่าง)
    "อาหารกึ่งสำเร็จรูป",     # กว้างเกิน
    "ขนมขบเคี้ยว",
    "ขนมจีน",                # อาจเป็นเส้นหรือเมนูพร้อมรับประทาน
    "ขนมแท่ง",
    "เห็ดสามอย่าง",
    "บะหมี่โฮลวีท", "บะหมี่ผัก", "บะหมี่",   # เป็นเส้นบะหมี่ดิบ ไม่ใช่ instant_noodle
    "เส้นบะหมี่",
    "ขนมไทย",
    "นมไทย",
}

mask_remove = df["keyword"].isin(REMOVE)
removed_n = mask_remove.sum()
df = df[~mask_remove].reset_index(drop=True)
print(f"Removed: {removed_n} broad keywords")

# ── 2) ย้าย keyword ที่ระบุไป OUT_OF_SCOPE ──
TO_OOS = {
    "ไข่เค็ม", "ไข่เยี่ยวม้า",
    "คาเคา", "อะโวคาโด", "อะโวคาโดเพียวเร่",
    "เนื้อสำรอง",
    "ไซรัป", "syrup", "น้ำเชื่อม", "น้ำเชื่อมผลไม้",
    "น้ำผึ้ง", "รสน้ำผึ้ง",
    "แยม", "เยลลี่",
    "น้ำตาล",
}
for kw in TO_OOS:
    mask = df["keyword"] == kw
    df.loc[mask, "hc_group"] = "OUT_OF_SCOPE"
    df.loc[mask, "subgroup"] = ""
    df.loc[mask, "confidence"] = 5
    df.loc[mask, "note"] = "out of scope (per user)"
print(f"Moved to OUT_OF_SCOPE: {len(TO_OOS)} keywords")

# ── 3) ลด confidence ของ keyword กว้าง ที่ยังเก็บไว้ ──
LOW_CONF = {
    # keep but lower confidence
}

# ── 4) เพิ่ม keyword OUT_OF_SCOPE ใหม่ ──
ADD_OOS = [
    # ไข่
    ("ไข่ดอง", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("ไข่ตุ๋น", "OUT_OF_SCOPE", "", 5, "out of scope"),
    # วัตถุดิบ/sweetener
    ("คาเคานิบส์", "OUT_OF_SCOPE", "", 5, "out of scope - raw material"),
    ("คาเคาแมส", "OUT_OF_SCOPE", "", 5, "out of scope - raw material"),
    ("คาเคา นิบส์", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("คาเคา เนยโกโก้", "OUT_OF_SCOPE", "", 5, "out of scope - raw material"),
    ("cacao", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("เพียวเร่", "OUT_OF_SCOPE", "", 5, "out of scope - puree"),
    ("puree", "OUT_OF_SCOPE", "", 5, "out of scope - puree"),
    # น้ำดื่ม
    ("น้ำดื่ม", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("น้ำแร่", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("น้ำแข็ง", "OUT_OF_SCOPE", "", 5, "out of scope"),
    # อาหารทางการแพทย์/เสริม
    ("ผลิตภัณฑ์เสริมอาหาร", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("อาหารทางการแพทย์", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("อาหารทารก", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("นมผงสำหรับทารก", "OUT_OF_SCOPE", "", 5, "out of scope"),
    # อื่นๆ
    ("เครื่องดื่มเกลือแร่", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("เครื่องดื่มแอลกอฮอล์", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("เบียร์", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("ไวน์", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("เหล้า", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("สาเก", "OUT_OF_SCOPE", "", 5, "out of scope"),
    # สมุนไพรแห้ง / ชาแห้ง (ไม่ใช่ผลิตภัณฑ์พร้อมบริโภค)
    ("ใบชาแห้ง", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("สมุนไพรแห้ง", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("อบเชย", "OUT_OF_SCOPE", "", 5, "out of scope - spice"),
    # ผลิตภัณฑ์ดิบ/สด/แช่แข็ง
    ("เนื้อสด", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("ปลาสด", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("ผักสด", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("ผลไม้สด", "OUT_OF_SCOPE", "", 5, "out of scope"),
    # อื่น
    ("ข้าวเปลือก", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("ข้าวสาร", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("งาดำ", "OUT_OF_SCOPE", "", 3, "out of scope ถ้าเป็นวัตถุดิบ"),
    ("งาขาว", "OUT_OF_SCOPE", "", 3, "out of scope ถ้าเป็นวัตถุดิบ"),
    # ผลไม้แช่อิ่ม/ผลไม้ดอง (อยู่นอกขอบ HC จริงๆ)
    ("ผลไม้แช่อิ่ม", "OUT_OF_SCOPE", "", 4, "out of scope"),
    ("ผลไม้ดอง", "OUT_OF_SCOPE", "", 4, "out of scope"),
    ("มะม่วงแช่อิ่ม", "OUT_OF_SCOPE", "", 4, "out of scope"),
    ("บ๊วยดอง", "OUT_OF_SCOPE", "", 4, "out of scope"),
    ("มะนาวดอง", "OUT_OF_SCOPE", "", 4, "out of scope"),
    # สารปรุงรส/น้ำตาล/น้ำผึ้ง
    ("น้ำตาลทราย", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("น้ำตาลปี๊ป", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("น้ำตาลมะพร้าว", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("น้ำตาลโตนด", "OUT_OF_SCOPE", "", 5, "out of scope"),
    # อื่นๆ
    ("ฟิชออยล์", "OUT_OF_SCOPE", "", 5, "out of scope - supplement"),
    ("fish oil", "OUT_OF_SCOPE", "", 5, "out of scope"),
    ("โปรตีนสกัด", "OUT_OF_SCOPE", "", 4, "out of scope - ingredient"),
    ("คอลลาเจน", "OUT_OF_SCOPE", "", 5, "out of scope - supplement"),
]

# ระวังซ้ำ
existing_keys = set(df["keyword"].astype(str).str.lower())
add_rows = []
for k, g, s, c, n in ADD_OOS:
    if k.lower() not in existing_keys:
        add_rows.append({"keyword": k, "hc_group": g, "subgroup": s, "confidence": c, "note": n})
        existing_keys.add(k.lower())
new_df = pd.concat([df, pd.DataFrame(add_rows)], ignore_index=True)
print(f"Added OUT_OF_SCOPE: {len(add_rows)} new keywords")

# ── 5) ปรับ keyword 'เครื่องดื่ม' ให้เป็น Conf 0 (ไม่ใช้แล้ว) ──
# จริงๆ จะลบเลย แต่ในกรณีบางตัวที่ระบุชัด "เครื่องดื่ม" ก็พอจะใช้ default beverage/soft_drink ได้
# แต่เพื่อให้ user เห็นว่าไม่ได้ map → ลบเลย

# ── Save ──
new_df.to_csv(KW_FILE, index=False, encoding="utf-8-sig")
print()
print(f"✓ Saved {len(new_df)} keywords → {KW_FILE.name}")
print()
print("Breakdown by HC group (after cleanup):")
print(new_df["hc_group"].value_counts().to_string())
