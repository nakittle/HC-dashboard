# -*- coding: utf-8 -*-
"""เพิ่ม keyword สำหรับ unmapped products รอบที่ 2"""
import sys, pandas as pd
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\nakit\OneDrive\Desktop\Healthier Choice")
KW = BASE / "keyword_map.csv"

NEW_ROWS = [
    # เครื่องดื่มสมุนไพร/สูตร/กลิ่น/ผง/อัดก๊าซ
    ("เครื่องดื่มสมุนไพร", "beverage", "soft_drink", 4, ""),
    ("เครื่องดื่มน้ำ", "beverage", "soft_drink", 4, ""),
    ("เครื่องดื่มสูตร", "beverage", "soft_drink", 3, ""),
    ("เครื่องดื่มกลิ่น", "beverage", "soft_drink", 4, ""),
    ("เครื่องดื่มอัดก๊าซ", "beverage", "soft_drink", 5, ""),
    ("เครื่องดื่มอัดลม", "beverage", "soft_drink", 5, ""),
    ("เครื่องดื่มผงสำเร็จรูป", "beverage", "soft_drink", 5, "powder→3.3"),
    ("เครื่องดื่มผง", "beverage", "soft_drink", 4, "powder→3.3"),
    ("เครื่องดื่มชง", "beverage", "soft_drink", 4, ""),
    ("เครื่องดื่มเข้มข้น", "beverage", "soft_drink", 4, ""),
    ("เครื่องดื่มมิกซ์", "beverage", "soft_drink", 4, ""),
    ("เครื่องดื่มผสม", "beverage", "soft_drink", 3, ""),
    ("เครื่องดื่มสกัด", "beverage", "soft_drink", 4, ""),
    ("ปรุงสำเร็จพร้อมดื่ม", "beverage", "soft_drink", 4, ""),
    ("พร้อมดื่ม", "beverage", "soft_drink", 3, ""),
    ("ผงสำเร็จรูป", "beverage", "soft_drink", 3, "powder→3.3"),
    ("ผงชงดื่ม", "beverage", "soft_drink", 4, "powder→3.3"),
    # ชาเฉพาะชนิด
    ("เพียวมัทฉะ", "beverage", "tea_ready", 5, ""),
    ("มัทฉะ", "beverage", "tea_ready", 5, ""),
    ("อูจิ", "beverage", "tea_ready", 4, ""),
    ("ชามะนาว", "beverage", "tea_ready", 5, ""),
    ("ชาไทย", "beverage", "tea_ready", 5, ""),
    ("ชานม", "beverage", "tea_ready", 5, ""),
    ("ชานมไต้หวัน", "beverage", "tea_ready", 5, ""),
    ("ชาหัวปลี", "beverage", "tea_ready", 5, ""),
    ("ชาเก๊กฮวย", "beverage", "tea_ready", 5, ""),
    ("ชาขิง", "beverage", "tea_ready", 5, ""),
    ("ชากระชาย", "beverage", "tea_ready", 5, ""),
    ("ชาผลไม้", "beverage", "tea_ready", 5, ""),
    ("ชาดอกไม้", "beverage", "tea_ready", 5, ""),
    ("ชาโรสฮิป", "beverage", "tea_ready", 5, ""),
    # น้ำ... (เครื่องดื่ม)
    ("น้ำกลิ่น", "beverage", "soft_drink", 4, ""),
    ("น้ำว่านหางจระเข้", "beverage", "soft_drink", 5, ""),
    ("น้ำพลูคาว", "beverage", "soft_drink", 5, ""),
    ("น้ำกระชาย", "beverage", "soft_drink", 4, ""),
    ("น้ำกระชายดำ", "beverage", "soft_drink", 5, ""),
    ("น้ำขิงสำเร็จรูป", "beverage", "soft_drink", 5, ""),
    ("น้ำลำไยผง", "beverage", "soft_drink", 5, ""),
    ("น้ำมะขามพร้อมดื่ม", "beverage", "soft_drink", 5, ""),
    ("น้ำมะขามเข้มข้น", "beverage", "soft_drink", 5, ""),
    ("น้ำมะดัน", "beverage", "soft_drink", 5, ""),
    ("น้ำดอกบัว", "beverage", "soft_drink", 5, ""),
    ("น้ำดอกไม้", "beverage", "soft_drink", 4, ""),
    ("น้ำกุหลาบ", "beverage", "soft_drink", 5, ""),
    ("น้ำมัลเบอรี่", "beverage", "soft_drink", 5, ""),
    ("น้ำมิกซ์เบอร์รี่", "beverage", "soft_drink", 5, ""),
    ("น้ำเบอร์รี่", "beverage", "soft_drink", 5, ""),
    ("น้ำมิกซ์ผลไม้", "beverage", "soft_drink", 5, ""),
    ("น้ำมังคุด", "beverage", "soft_drink", 5, ""),
    ("น้ำลูกสำรอง", "beverage", "soft_drink", 5, ""),
    ("ลูกสำรอง", "beverage", "soft_drink", 3, ""),
    ("น้ำใบเตย", "beverage", "soft_drink", 5, ""),
    ("น้ำอินทผลัม", "beverage", "soft_drink", 5, ""),
    ("น้ำนมข้าวกล้อง", "beverage", "cereal_drink", 5, ""),
    ("น้ำนมมะพร้าว", "beverage", "cereal_drink", 5, ""),
    ("นมมะพร้าว", "beverage", "cereal_drink", 5, ""),
    ("น้ำลูกเดือย", "beverage", "cereal_drink", 5, ""),
    ("ข้าวคั่วชง", "beverage", "cereal_drink", 5, ""),
    ("ข้าวชงดื่ม", "beverage", "cereal_drink", 5, ""),
    ("เมล็ดข้าวคั่ว", "beverage", "cereal_drink", 4, ""),
    # ไซเดอร์/โซดา
    ("ไซเดอร์", "beverage", "soft_drink", 5, ""),
    ("ไซเดอร์อินทผลัม", "beverage", "soft_drink", 5, ""),
    ("เมล่อนโซดา", "beverage", "soft_drink", 5, ""),
    ("น้ำเมล่อน", "beverage", "soft_drink", 5, ""),
    # ตรา / สมุนไพรเฉพาะ
    ("ดื่มด่ำ", "beverage", "tea_ready", 4, ""),
    ("ดื่มดี", "beverage", "soft_drink", 4, ""),
    ("ผงพลูคาว", "beverage", "soft_drink", 5, ""),
    ("พลูคาว", "beverage", "soft_drink", 4, ""),
    ("กระชายดำ", "beverage", "soft_drink", 3, ""),
    ("ดอกอัญชัน", "beverage", "soft_drink", 4, ""),
    ("คาโมมายล์", "beverage", "tea_ready", 5, ""),
    ("ลาเวนเดอร์", "beverage", "tea_ready", 5, ""),
    ("อัญชันมะนาว", "beverage", "soft_drink", 5, ""),
    ("เก๊กฮวย", "beverage", "soft_drink", 4, ""),
    ("จับเลี้ยง", "beverage", "soft_drink", 4, ""),
    ("ตรีผลา", "beverage", "soft_drink", 4, ""),
    # โจ๊ก/อาหาร
    ("โจ๊กข้าวกล้อง", "instant_food", "instant_rice", 5, ""),
    ("โจ๊กข้าว", "instant_food", "instant_rice", 5, ""),
    ("โจ๊กพร้อมรับประทาน", "instant_food", "instant_rice", 5, ""),
    ("โจ๊กพร้อมทาน", "instant_food", "instant_rice", 5, ""),
    ("โจ๊กตรา", "instant_food", "instant_rice", 4, ""),
    ("โจ๊กปรุงสำเร็จ", "instant_food", "instant_rice", 5, ""),
    # ขนม
    ("ขนมจาก", "bakery", "cookie_cake", 5, ""),
    ("ขนมก้านบัว", "bakery", "cookie_cake", 5, ""),
    ("ขนมเปี๊ยะลูกเต๋า", "bakery", "cookie_cake", 5, ""),
    ("ขนมโสมนัส", "bakery", "cookie_cake", 5, ""),
    ("ขนมโสน", "bakery", "cookie_cake", 4, ""),
    ("ดอกจอกทอด", "snack", "fried_baked_snack", 5, ""),
    ("ดอกจอก", "snack", "fried_baked_snack", 4, ""),
    # ปลา/เนื้อ
    ("ปลาเค็มทอด", "fish_seafood", "fried_fish", 5, ""),
    ("ปลาส้มฟัก", "meat_product", "seasoned_meat", 4, ""),
    ("อ่องมันปูนา", "meat_product", "seasoned_meat", 4, ""),
    ("มันปูนา", "meat_product", "seasoned_meat", 4, ""),
    ("น้ำพริกปูนา", "seasoning", "other_dip", 4, ""),
    ("น้ำพริกตา", "seasoning", "other_dip", 4, ""),
    # meal (อาหารพร้อมรับประทาน)
    ("ก๋วยจั๊บญวน", "meal", "", 5, ""),
    ("ก๋วยเตี๋ยวเส้นสด", "meal", "", 5, ""),
    ("ก๋วยเตี๋ยวลุยสวน", "meal", "", 5, ""),
    ("อาหารพร้อมอุ่น", "meal", "", 4, ""),
    ("อาหารกล่องแช่แข็ง", "meal", "", 5, ""),
    ("ข้าวกล่องแช่แข็ง", "meal", "", 5, ""),
    ("เส้นจันท์ผัด", "meal", "", 5, ""),
    ("เส้นใหญ่ผัด", "meal", "", 5, ""),
    ("ผัดไทยกุ้งสด", "meal", "", 5, ""),
    ("ผัดไทยพร้อมทาน", "meal", "", 5, ""),
    ("ราดหน้า", "meal", "", 5, ""),
    ("ข้าวพร้อมทาน", "meal", "", 5, ""),
    ("อาหารแช่แข็งพร้อมทาน", "meal", "", 5, ""),
    ("อาหารพร้อมรับประทาน", "meal", "", 4, ""),
]

df = pd.read_csv(KW)
print(f"Original: {len(df)} keywords")
existing = set(df["keyword"].astype(str).str.lower())
add = [r for r in NEW_ROWS if r[0].lower() not in existing]
print(f"To add (skip duplicates): {len(add)}")
new_df = pd.DataFrame(add, columns=["keyword", "hc_group", "subgroup", "confidence", "note"])
out = pd.concat([df, new_df], ignore_index=True)
out.to_csv(KW, index=False, encoding="utf-8-sig")
print(f"Saved: {len(out)} keywords → {KW.name}")
