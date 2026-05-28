# -*- coding: utf-8 -*-
"""anonymize_data.py — สร้างไฟล์ HC_Dashboard_Data_Public.xlsx สำหรับ deploy ขึ้น Streamlit Cloud

ลบข้อมูลที่ระบุตัวตน:
- ลบคอลัมน์ ชื่อลูกค้า, เขต
- แทนชื่อผลิตภัณฑ์ด้วย label generic เช่น "[ขนมขบเคี้ยว] - #0001"
"""
import sys, pandas as pd
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\nakit\OneDrive\Desktop\Healthier Choice")
SRC = BASE / "HC_Dashboard_Data.xlsx"
OUT = BASE / "HC_Dashboard_Data_Public.xlsx"

# โหลด sheet หลัก
data = pd.read_excel(SRC, sheet_name="1_Data")
summary = pd.read_excel(SRC, sheet_name="0_Summary")
by_group = pd.read_excel(SRC, sheet_name="2_By_HC_Group")
by_sub = pd.read_excel(SRC, sheet_name="3_By_HC_Subgroup")
by_region = pd.read_excel(SRC, sheet_name="4_By_Region")
by_prov = pd.read_excel(SRC, sheet_name="5_By_Province")
fail_detail = pd.read_excel(SRC, sheet_name="6_Failed_Detail")
top_fail = pd.read_excel(SRC, sheet_name="7_Top_Failed_Nutrient")
crit_ref = pd.read_excel(SRC, sheet_name="8_HC_Criteria_Reference")

print(f"Loaded {len(data)} rows from 1_Data")

# Drop PII columns
drop_cols = ["ชื่อลูกค้า", "เขต"]
for c in drop_cols:
    if c in data.columns:
        data = data.drop(columns=c)
        print(f"  Dropped column: {c}")

# Anonymize product names
def make_label(row, idx):
    group_th = row.get("HC_Group_TH") or "Unknown"
    sub_th = row.get("HC_Subgroup_TH") or ""
    if pd.notna(sub_th) and sub_th and sub_th != "":
        label = f"[{group_th} / {sub_th}] #{idx:04d}"
    else:
        label = f"[{group_th}] #{idx:04d}"
    return label

data = data.reset_index(drop=True)
data["ผลิตภัณฑ์"] = [make_label(r, i + 1) for i, (_, r) in enumerate(data.iterrows())]
print("  Anonymized product names")

# Anonymize Failed_Detail sheet (same way using ลำดับ)
if "ผลิตภัณฑ์" in fail_detail.columns:
    # join with data to get anonymized label
    label_map = dict(zip(data["ลำดับ"], data["ผลิตภัณฑ์"]))
    fail_detail["ผลิตภัณฑ์"] = fail_detail["ลำดับ"].map(label_map).fillna("[Unknown]")
    print("  Anonymized Failed_Detail product names")

# Drop PII from fail_detail too
for c in drop_cols:
    if c in fail_detail.columns:
        fail_detail = fail_detail.drop(columns=c)

# Write public file
with pd.ExcelWriter(OUT, engine="openpyxl") as w:
    summary.to_excel(w, sheet_name="0_Summary", index=False)
    data.to_excel(w, sheet_name="1_Data", index=False)
    by_group.to_excel(w, sheet_name="2_By_HC_Group", index=False)
    by_sub.to_excel(w, sheet_name="3_By_HC_Subgroup", index=False)
    by_region.to_excel(w, sheet_name="4_By_Region", index=False)
    by_prov.to_excel(w, sheet_name="5_By_Province", index=False)
    fail_detail.to_excel(w, sheet_name="6_Failed_Detail", index=False)
    top_fail.to_excel(w, sheet_name="7_Top_Failed_Nutrient", index=False)
    crit_ref.to_excel(w, sheet_name="8_HC_Criteria_Reference", index=False)

print(f"\n→ Saved: {OUT.name}")
print(f"  Rows: {len(data)}, Columns: {len(data.columns)}")
print(f"  PII columns removed: {drop_cols}")
print(f"  Sample anonymized names:")
for s in data["ผลิตภัณฑ์"].head(3):
    print(f"    - {s}")
