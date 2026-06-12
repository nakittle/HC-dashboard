# HC Dashboard — Healthier Choice Evaluation (GDA 2568)

Streamlit dashboard สรุปผลการประเมินผลิตภัณฑ์ตามเกณฑ์ **ทางเลือกสุขภาพ (Healthier Choice — HC)** ของไทย จากโครงการตรวจ GDA 2568 ฟรี (836 ผลิตภัณฑ์)

## 📊 Live Dashboard

> **URL**: _(จะใส่หลัง deploy บน Streamlit Cloud)_

## 🎯 Overview

ผลิตภัณฑ์ 836 รายการ ถูกแบ่งเป็น 4 หมวด:

| Criteria | ความหมาย | จำนวน | % |
|---------|---------|------:|--:|
| **3.1** | ผ่านเกณฑ์ HC | 27 | 3.2% |
| **3.2** | ไม่ผ่านเกณฑ์ HC | 375 | 44.9% |
| **3.3** | ข้อมูลโภชนาการไม่พอ | 267 | 31.9% |
| **OOS** | นอกขอบเขต HC | 167 | 20.0% |

## 🧭 Dashboard Sections

1. **Overview** — สัดส่วน Criteria + จำนวนตามกลุ่ม HC
2. **HC Group Analysis** — แยก 15 กลุ่ม HC × 4 Criteria + ตารางรายละเอียด
3. **Geographic** — ภูมิภาค × Criteria, Top 10 จังหวัด, Heatmap
4. **Failed Nutrient Deep-dive** — สารอาหารที่ทำให้ตก HC (น้ำตาล/โซเดียม/ไขมันอิ่มตัว ฯลฯ)
5. **Product Detail Table** — ตารางค้นหา + Export CSV

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Plotly** — interactive charts
- **Pandas + openpyxl** — data handling

## 🚀 Run Locally

```bash
git clone https://github.com/<your-username>/hc-dashboard.git
cd hc-dashboard
pip install -r requirements.txt
streamlit run dashboard.py
```

เปิด browser ที่ `http://localhost:8501`

## 📁 Files

| File | Purpose |
|------|---------|
| `dashboard.py` | Streamlit app (main file) |
| `HC_Dashboard_Data_Public.xlsx` | Anonymized data (836 rows, 9 sheets) |
| `requirements.txt` | Python dependencies |

## 🔒 Privacy

ข้อมูลที่ deploy เป็น **anonymized**:
- ✅ ลบ: ชื่อลูกค้า, เขต, ตราสินค้า (replaced with generic labels)
- ✅ คงไว้: HC group/subgroup, จังหวัด, สารอาหาร, ผลการประเมิน

## 📜 HC Criteria

อ้างอิงเกณฑ์ "ทางเลือกสุขภาพ" (Healthier Choice) ของกระทรวงสาธารณสุข — แบ่งอาหาร 15 กลุ่ม โดยแต่ละกลุ่มมีเกณฑ์สารอาหารแตกต่างกัน (น้ำตาล, โซเดียม, ไขมัน, ไขมันอิ่มตัว, พลังงาน ฯลฯ)

## 📝 License

MIT
