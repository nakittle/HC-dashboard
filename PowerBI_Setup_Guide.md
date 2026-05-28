# คู่มือสร้าง Power BI Dashboard — HC Evaluation 2026

## สรุปผลการประเมิน (สถานะปัจจุบัน)

| Criteria | ความหมาย | จำนวน | สัดส่วน |
|---|---|---:|---:|
| **3.1** | สารอาหารครบ **และ** ผ่านเกณฑ์ HC | 135 | 9.9% |
| **3.2** | สารอาหารครบ แต่ **ไม่ผ่าน**เกณฑ์ HC | 773 | 56.9% |
| **3.3** | สารอาหารไม่ครบสำหรับประเมิน | 450 | 33.1% |
| Unmapped | จัดกลุ่ม HC ไม่ได้ | 1 | 0.1% |
| **รวม** |  | **1,358** | **100%** |

**ข้อสังเกตสำคัญ**: กลุ่มที่ตกเป็น 3.3 ทั้งหมด ได้แก่ `meal` (79), `bakery` (339), `bread` (10), `cereal` (10) — เพราะเกณฑ์ HC ของกลุ่มเหล่านี้ต้องใช้ **ใยอาหาร / แคลเซียม / เหล็ก** ซึ่งไม่ได้มีอยู่ในข้อมูล GDA 2026 — ต้องส่งตรวจเพิ่มเติมในรอบถัดไป

**Top สารอาหารที่ทำให้ตกเกณฑ์** (Criteria 3.2): น้ำตาล (501) > พลังงาน/หน่วยบริโภค (415) > โซเดียม (355) > ไขมันอิ่มตัว (236) > ไขมัน (226)

---

## ขั้นตอนนำเข้า Power BI Desktop

1. เปิด **Power BI Desktop**
2. **Home → Get data → Excel workbook** → เลือก `evaluation_result.xlsx`
3. ใน Navigator เลือก sheet ทั้ง 6:
   - ☑ `Result` (1,358 แถว — ข้อมูลหลัก)
   - ☑ `Summary`
   - ☑ `By_HC_Group`
   - ☑ `By_Province`
   - ☑ `Top_Failed_Nutrient`
   - ☑ `Unmapped_Review`
4. คลิก **Load**

### Data Transformation (ถ้าจำเป็น)
- คอลัมน์ `Criteria` ใน sheet `Result`: ตรวจให้แน่ใจว่า data type = Text
- คอลัมน์ `จังหวัด`: trim whitespace (Home → Transform → Format → Trim)
- คอลัมน์ `Failed_Nutrients` กับ `Missing_Nutrients`: เป็น semicolon-separated — ต้อง split ถ้าจะวิเคราะห์รายสารอาหาร (Power Query: Split Column by Delimiter `;` → Pivot/Unpivot)

### สร้าง Measures (DAX)
```dax
Total Products = COUNTROWS(Result)
Pass HC = CALCULATE([Total Products], Result[Criteria] = "3.1")
Fail HC = CALCULATE([Total Products], Result[Criteria] = "3.2")
Incomplete = CALCULATE([Total Products], Result[Criteria] = "3.3")
% Pass = DIVIDE([Pass HC], [Total Products])
% Fail = DIVIDE([Fail HC], [Total Products])
% Incomplete = DIVIDE([Incomplete], [Total Products])
```

---

## โครงสร้าง Dashboard 4 หน้า

### หน้า 1: Executive Summary
| Visual | Field |
|---|---|
| **KPI Card** × 4 | Total Products / Pass HC (3.1) / Fail HC (3.2) / Incomplete (3.3) |
| **Donut chart** | Axis: Criteria · Values: Total Products |
| **Bar chart** | Axis: จังหวัด (Top 10 by Pass HC) · Values: Pass HC |
| **Slicer** | จังหวัด, HC_Group |
| **Title** | "ภาพรวมการประเมิน Healthier Choice 1,358 ผลิตภัณฑ์" |

### หน้า 2: HC Group Analysis
| Visual | Field |
|---|---|
| **Stacked column chart** | Axis: HC_Group · Legend: Criteria · Values: Count |
| **Matrix table** | Rows: HC_Group · Columns: Criteria · Values: Count, % Pass |
| **Bar chart** | Axis: HC_Subgroup · Values: Pass HC, Fail HC |
| **Slicer** | HC_Group |

### หน้า 3: Geographic View
| Visual | Field |
|---|---|
| **Filled Map (ประเทศไทย)** | Location: จังหวัด · Color saturation: % Pass HC · Tooltip: Total, Pass, Fail, Incomplete |
| **Stacked bar** | Axis: จังหวัด · Legend: Criteria · Values: Count |
| **Top N by % Pass** | Table: จังหวัด, % Pass HC, จำนวน |

### หน้า 4: Failed Nutrient Deep-dive
| Visual | Field |
|---|---|
| **Bar chart** | Axis: Nutrient (จาก sheet Top_Failed_Nutrient) · Values: Count |
| **Heatmap (Matrix)** | Rows: HC_Group · Columns: Failed Nutrient (จาก split) · Values: Count |
| **Drill-through table** | คลิกแล้วเห็น ผลิตภัณฑ์ + จังหวัด + สารอาหารที่ตก |

---

## สี Theme ที่แนะนำ
- **3.1 ผ่าน**: เขียว `#2E7D32`
- **3.2 ไม่ผ่าน**: ส้ม/แดง `#E64A19`
- **3.3 สารอาหารไม่พอ**: เทา `#757575`

ตั้งใน **View → Themes → Customize**

---

## การ Publish & Share
1. คลิก **Publish** → เลือก Workspace
2. ตั้ง **Scheduled refresh** (ถ้าข้อมูลจะอัปเดต): Dataset settings → Scheduled refresh
3. แชร์ลิงก์กับผู้บริหารผ่าน Power BI Service

---

## การปรับปรุงในอนาคต

1. **เพิ่มสารอาหารที่ขาด**: ถ้าได้ผลตรวจใยอาหาร/แคลเซียม/เหล็กเพิ่ม จะปลดล็อกกลุ่ม `meal`, `bread`, `cereal`, `bakery` ออกจาก 3.3 (โอกาส ~32% ของ dataset)
2. **อัปเดต `keyword_map.csv`**: ถ้ามีผลิตภัณฑ์ใหม่ที่ unmapped หรือ map ผิด เพิ่ม keyword แล้วรัน `python evaluate_hc.py` ใหม่
3. **อัปเดต `hc_criteria.json`**: ถ้าเกณฑ์ HC เปลี่ยน (เช่น ปรับ phase ของโซเดียมในเนื้อสัตว์/อาหารมื้อหลัก) ปรับ field `current_phase` หรือเพิ่ม subgroup
4. **ตรวจสอบ Manual Review**: เปิด `mapping_review.xlsx` → sheet `Low_Confidence` รีวิวรายการที่ confidence ≤ 2 เพื่อ fine-tune mapping

---

## ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | บทบาท |
|---|---|
| `GDA 2026.xlsx` | ข้อมูลต้นทาง (ไม่ถูกแก้ไข) |
| `hc_criteria.json` | เกณฑ์ HC 15 กลุ่ม |
| `keyword_map.csv` | Mapping keyword → กลุ่ม HC (1,037 keywords) |
| `evaluate_hc.py` | สคริปต์หลัก |
| **`evaluation_result.xlsx`** | **Input ของ Power BI** ⭐ |
| `mapping_review.xlsx` | รายการรีวิวมือ |
| `PowerBI_Setup_Guide.md` | เอกสารนี้ |
