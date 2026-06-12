# HC Dashboard — Healthier Choice Evaluation (GDA 2568–2569)

Streamlit dashboard สรุปผลการประเมินผลิตภัณฑ์ตามเกณฑ์ **ทางเลือกสุขภาพ (Healthier Choice — HC)** ของไทย จากโครงการตรวจ GDA ฟรี ปี 2568–2569 (รวม 2,194 ผลิตภัณฑ์) — เลือกปีข้อมูลได้จากตัวกรอง "📅 ปีข้อมูล (GDA)" ในแถบด้านข้าง (ค่าเริ่มต้น = ปีล่าสุด)

## 📊 Live Dashboard

> **URL**: _(จะใส่หลัง deploy บน Streamlit Cloud)_

## 🎯 Overview

ผลิตภัณฑ์รวม 2,194 รายการ (2 ปีข้อมูล) ถูกแบ่งเป็น 4 หมวด:

| ปี | 3.1 ผ่าน | 3.2 ไม่ผ่าน | 3.3 ข้อมูลไม่พอ | OOS นอกขอบเขต | รวม |
|---:|------:|--------:|------------:|------------:|----:|
| **2568** | 30 | 385 | 261 | 160 | 836 |
| **2569** | 100 | 589 | 369 | 300 | 1,358 |

## 🧭 Dashboard Sections

1. **ภาพรวม** — สัดส่วน Criteria + จำนวนตามกลุ่ม HC
2. **กลุ่ม HC** — แยก 15 กลุ่ม HC × 4 Criteria + ตารางรายละเอียด
3. **ภูมิภาค** — ภูมิภาค × Criteria, Top จังหวัด, Heatmap
4. **เขตสุขภาพ** — เขตสุขภาพ 1–13 × Criteria, Pass Rate, Heatmap
5. **สารอาหาร** — สารอาหารที่ทำให้ตก HC (น้ำตาล/โซเดียม/ไขมันอิ่มตัว ฯลฯ)
6. **ผลิตภัณฑ์** — ตารางค้นหา + Export CSV

ทุกหน้าคำนวณตามปีข้อมูลที่เลือกจากตัวกรองในแถบด้านข้าง (ค่าเริ่มต้น = ปีล่าสุด)

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Plotly** — interactive charts
- **Pandas + openpyxl** — data handling

## 🚀 Run Locally

```bash
git clone https://github.com/nakittle/HC-dashboard.git
cd HC-dashboard
pip install -r requirements.txt
streamlit run dashboard.py
```

เปิด browser ที่ `http://localhost:8501`

## 📁 Files

| File | Purpose |
|------|---------|
| `dashboard.py` | Streamlit app (main file) |
| `HC_Dashboard_Data_Public.xlsx` | Anonymized data (2,194 rows, 9 sheets, 2 ปีข้อมูล) |
| `requirements.txt` | Python dependencies |

## 🔒 Privacy

ข้อมูลที่ deploy เป็น **anonymized**:
- ✅ ลบ: ชื่อลูกค้า, ชื่อผลิตภัณฑ์/ตราสินค้า (replaced with generic labels)
- ✅ คงไว้: HC group/subgroup, ภูมิภาค/จังหวัด/เขตสุขภาพ, สารอาหาร, ผลการประเมิน

## 📜 HC Criteria

อ้างอิงเกณฑ์ "ทางเลือกสุขภาพ" (Healthier Choice) ของกระทรวงสาธารณสุข — แบ่งอาหาร 15 กลุ่ม โดยแต่ละกลุ่มมีเกณฑ์สารอาหารแตกต่างกัน (น้ำตาล, โซเดียม, ไขมัน, ไขมันอิ่มตัว, พลังงาน ฯลฯ) ผลการประเมินทั้งสองปีข้อมูลตัดสินด้วยเกณฑ์เดียวกัน คือเกณฑ์ตามประกาศฉบับที่ 4 (เกณฑ์ที่มีผลบังคับใช้ในปี 2569)

## 📝 License

MIT
