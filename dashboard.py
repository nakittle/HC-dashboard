# -*- coding: utf-8 -*-
"""
HC Dashboard — Streamlit Single-Page App
ประเมิน Healthier Choice (HC) สำหรับผลิตภัณฑ์ GDA 2026 จำนวน 1,358 รายการ
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# ════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HC Dashboard — GDA 2026",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Traffic light colors (consistent across all charts)
COLORS = {
    "3.1": "#4CAF50",   # green - ผ่าน
    "3.2": "#F44336",   # red - ไม่ผ่าน
    "3.3": "#FFC107",   # yellow - ข้อมูลไม่พอ
    "OOS": "#9E9E9E",   # gray - นอกขอบเขต
}
LABEL_TH = {
    "3.1": "3.1 ผ่าน HC",
    "3.2": "3.2 ไม่ผ่าน HC",
    "3.3": "3.3 ข้อมูลไม่พอ",
    "OOS": "นอกขอบเขต (OOS)",
}

DATA_FILE = Path(__file__).parent / "HC_Dashboard_Data_Public.xlsx"


# ════════════════════════════════════════════════════════════════════
# DATA LOADING (cached)
# ════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="กำลังโหลดข้อมูล...")
def load_data():
    data = pd.read_excel(DATA_FILE, sheet_name="1_Data")
    fail_detail = pd.read_excel(DATA_FILE, sheet_name="6_Failed_Detail")
    return data, fail_detail


try:
    df, fail_df = load_data()
except FileNotFoundError:
    st.error(f"ไม่พบไฟล์ข้อมูล: {DATA_FILE.name}")
    st.stop()


# ════════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ════════════════════════════════════════════════════════════════════
st.sidebar.title("🔍 ตัวกรอง (Filters)")
st.sidebar.caption("กรองข้อมูลก่อนดูทุก section ด้านขวา")

# Region filter
regions = sorted(df["ภูมิภาค"].dropna().unique().tolist())
sel_regions = st.sidebar.multiselect(
    "ภูมิภาค", regions, default=regions,
    help="เลือก 1+ ภูมิภาค"
)

# Health Zone filter
if "เขตสุขภาพ" in df.columns:
    zones = sorted(df["เขตสุขภาพ"].dropna().unique().tolist())
    sel_zones = st.sidebar.multiselect(
        "เขตสุขภาพ", zones, default=zones,
        format_func=lambda z: f"เขต {z}",
        help="เขตสุขภาพของกระทรวงสาธารณสุข 1-13",
    )
else:
    sel_zones = None

# Province filter (cascade from region)
provs_available = sorted(df[df["ภูมิภาค"].isin(sel_regions)]["จังหวัด"].dropna().unique().tolist())
sel_provs = st.sidebar.multiselect(
    "จังหวัด", provs_available, default=[],
    help="ปล่อยว่าง = ทุกจังหวัดในภูมิภาคที่เลือก"
)

# HC Group filter
groups = sorted(df["HC_Group_TH"].dropna().unique().tolist())
sel_groups = st.sidebar.multiselect(
    "กลุ่ม HC", groups, default=groups,
    help="เลือก 1+ กลุ่ม"
)

# Criteria filter
crits = ["3.1", "3.2", "3.3", "OOS"]
sel_crits = st.sidebar.multiselect(
    "เกณฑ์ Criteria", crits, default=crits,
    format_func=lambda x: LABEL_TH.get(x, x),
)

# Apply filters
f = df[df["ภูมิภาค"].isin(sel_regions) & df["HC_Group_TH"].isin(sel_groups) & df["Criteria"].isin(sel_crits)]
if sel_provs:
    f = f[f["จังหวัด"].isin(sel_provs)]
if sel_zones is not None and "เขตสุขภาพ" in f.columns:
    f = f[f["เขตสุขภาพ"].isin(sel_zones)]

st.sidebar.divider()
st.sidebar.metric("รายการที่เลือก", f"{len(f):,} / {len(df):,}")
st.sidebar.caption("ผลทั้งหมดด้านขวาคำนวณจาก subset นี้")
st.sidebar.divider()
st.sidebar.markdown(
    "**ข้อมูล**: GDA 2026 (1,358 รายการ)  \n"
    "**ที่มา**: โครงการตรวจ GDA ฟรี  \n"
    "**สถานะ**: ข้อมูล anonymized (ลบชื่อตราสินค้า/ลูกค้า)"
)


# ════════════════════════════════════════════════════════════════════
# HEADER + KPI CARDS
# ════════════════════════════════════════════════════════════════════
st.title("🥗 Healthier Choice Evaluation — GDA 2026")
st.markdown(
    "ภาพรวมการประเมินผลิตภัณฑ์ตามเกณฑ์ **ทางเลือกสุขภาพ (HC)** ของไทย "
    "— จำแนกตามเกณฑ์ 3.1 (ผ่าน) / 3.2 (ไม่ผ่าน) / 3.3 (ข้อมูลไม่พอ) และ OOS (นอกขอบเขต)"
)

# KPI cards
total = len(f)
n31 = int((f["Criteria"] == "3.1").sum())
n32 = int((f["Criteria"] == "3.2").sum())
n33 = int((f["Criteria"] == "3.3").sum())
noos = int((f["Criteria"] == "OOS").sum())
in_scope = total - noos

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ผลิตภัณฑ์ทั้งหมด", f"{total:,}")
c2.metric("✅ ผ่าน HC (3.1)", f"{n31:,}", f"{n31/total*100:.1f}%" if total else "")
c3.metric("❌ ไม่ผ่าน (3.2)", f"{n32:,}", f"{n32/total*100:.1f}%" if total else "")
c4.metric("⚠️ ข้อมูลไม่พอ (3.3)", f"{n33:,}", f"{n33/total*100:.1f}%" if total else "")
c5.metric("➖ นอกขอบเขต", f"{noos:,}", f"{noos/total*100:.1f}%" if total else "")

if in_scope > 0:
    st.info(
        f"📊 **อยู่ในขอบเขต HC**: {in_scope:,} รายการ — "
        f"ผ่าน {n31/in_scope*100:.1f}% / ไม่ผ่าน {n32/in_scope*100:.1f}% / ข้อมูลไม่พอ {n33/in_scope*100:.1f}%"
    )

st.divider()


# ════════════════════════════════════════════════════════════════════
# SECTION 1: OVERVIEW
# ════════════════════════════════════════════════════════════════════
st.header("1️⃣ ภาพรวม (Overview)")

col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("สัดส่วน Criteria")
    crit_counts = f["Criteria"].value_counts().reindex(["3.1", "3.2", "3.3", "OOS"]).fillna(0)
    fig = go.Figure(go.Pie(
        labels=[LABEL_TH[c] for c in crit_counts.index],
        values=crit_counts.values,
        hole=0.55,
        marker=dict(colors=[COLORS[c] for c in crit_counts.index]),
        textinfo="label+percent",
        textfont_size=12,
    ))
    fig.update_layout(
        showlegend=False, height=400,
        margin=dict(t=20, b=20, l=20, r=20),
        annotations=[dict(text=f"<b>{total:,}</b><br>รายการ", x=0.5, y=0.5, font_size=16, showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("จำนวนผลิตภัณฑ์ตามกลุ่ม HC")
    grp = f.groupby("HC_Group_TH").size().reset_index(name="จำนวน").sort_values("จำนวน", ascending=True)
    fig = px.bar(
        grp, x="จำนวน", y="HC_Group_TH", orientation="h",
        text="จำนวน", color="จำนวน", color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=400, margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="จำนวน", yaxis_title="",
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
# SECTION 2: HC GROUP ANALYSIS
# ════════════════════════════════════════════════════════════════════
st.header("2️⃣ วิเคราะห์ตามกลุ่ม HC")

# Stacked bar: group × criteria
pivot = f.groupby(["HC_Group_TH", "Criteria"]).size().unstack(fill_value=0)
for c in ["3.1", "3.2", "3.3", "OOS"]:
    if c not in pivot.columns:
        pivot[c] = 0
pivot = pivot[["3.1", "3.2", "3.3", "OOS"]]
pivot["Total"] = pivot.sum(axis=1)
pivot = pivot.sort_values("Total", ascending=True)

fig = go.Figure()
for c in ["3.1", "3.2", "3.3", "OOS"]:
    fig.add_trace(go.Bar(
        name=LABEL_TH[c], y=pivot.index, x=pivot[c], orientation="h",
        marker_color=COLORS[c], text=pivot[c].where(pivot[c] > 0, ""),
        textposition="inside",
    ))
fig.update_layout(
    barmode="stack", height=max(400, len(pivot) * 35),
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="จำนวน", yaxis_title="",
    legend=dict(orientation="h", y=-0.1),
)
st.plotly_chart(fig, use_container_width=True)

# Detail table
st.subheader("ตารางรายละเอียดกลุ่ม HC")
det = pivot.copy()
det["Pass Rate (%)"] = (det["3.1"] / (det["Total"] - det["OOS"]).replace(0, 1) * 100).round(1)
det = det.reset_index().rename(columns={
    "HC_Group_TH": "กลุ่ม HC",
    "3.1": "ผ่าน 3.1", "3.2": "ไม่ผ่าน 3.2",
    "3.3": "ข้อมูลไม่พอ 3.3", "OOS": "OOS", "Total": "รวม",
})
det = det.sort_values("รวม", ascending=False)
st.dataframe(det, use_container_width=True, hide_index=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
# SECTION 3: GEOGRAPHIC VIEW
# ════════════════════════════════════════════════════════════════════
st.header("3️⃣ มุมมองภูมิภาค (Geographic)")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("จำนวนตามภูมิภาค × Criteria")
    region_pv = f.groupby(["ภูมิภาค", "Criteria"]).size().unstack(fill_value=0)
    for c in ["3.1", "3.2", "3.3", "OOS"]:
        if c not in region_pv.columns:
            region_pv[c] = 0
    region_pv = region_pv[["3.1", "3.2", "3.3", "OOS"]]

    fig = go.Figure()
    for c in ["3.1", "3.2", "3.3", "OOS"]:
        fig.add_trace(go.Bar(
            name=LABEL_TH[c], x=region_pv.index, y=region_pv[c],
            marker_color=COLORS[c],
        ))
    fig.update_layout(
        barmode="stack", height=400,
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis_title="จำนวน", xaxis_title="",
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_g2:
    st.subheader("Top 10 จังหวัด — Pass Rate (%)")
    prov_stats = f.groupby("จังหวัด").agg(
        Total=("ลำดับ", "count"),
        Passed=("Passed", "sum"),
        OOS=("OutOfScope", "sum"),
    ).reset_index()
    prov_stats["In_Scope"] = prov_stats["Total"] - prov_stats["OOS"]
    prov_stats["Pass_Rate"] = (prov_stats["Passed"] / prov_stats["In_Scope"].replace(0, 1) * 100).round(1)
    prov_stats = prov_stats[prov_stats["Total"] >= 10].sort_values("Pass_Rate", ascending=True).tail(10)

    if len(prov_stats) > 0:
        fig = px.bar(
            prov_stats, x="Pass_Rate", y="จังหวัด", orientation="h",
            text="Pass_Rate", color="Pass_Rate", color_continuous_scale="RdYlGn",
            hover_data=["Total", "Passed"],
        )
        fig.update_layout(
            height=400, margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="% ผ่าน HC", yaxis_title="",
            coloraxis_showscale=False,
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("จังหวัดที่มี ≥10 ผลิตภัณฑ์ในตัวกรองนี้ไม่เพียงพอ")

# Heatmap: region × HC group (count)
st.subheader("Heatmap: ภูมิภาค × กลุ่ม HC (จำนวนผลิตภัณฑ์)")
heat = f.groupby(["ภูมิภาค", "HC_Group_TH"]).size().unstack(fill_value=0)
if not heat.empty:
    fig = px.imshow(
        heat.values, x=heat.columns, y=heat.index,
        color_continuous_scale="Blues", aspect="auto", text_auto=True,
    )
    fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
# SECTION 4: HEALTH ZONE ANALYSIS (เขตสุขภาพ)
# ════════════════════════════════════════════════════════════════════
if "เขตสุขภาพ" in f.columns:
    st.header("4️⃣ วิเคราะห์ตามเขตสุขภาพ (Health Zone)")
    st.caption("เขตสุขภาพ 1-13 ตามการแบ่งของกระทรวงสาธารณสุข (กทม. = เขต 13)")

    col_z1, col_z2 = st.columns(2)

    with col_z1:
        st.subheader("จำนวนตามเขตสุขภาพ × Criteria")
        zone_pv = f.groupby(["เขตสุขภาพ", "Criteria"]).size().unstack(fill_value=0)
        for c in ["3.1", "3.2", "3.3", "OOS"]:
            if c not in zone_pv.columns:
                zone_pv[c] = 0
        zone_pv = zone_pv[["3.1", "3.2", "3.3", "OOS"]]
        zone_pv = zone_pv.sort_index()
        zone_labels = [f"เขต {z}" for z in zone_pv.index]

        fig = go.Figure()
        for c in ["3.1", "3.2", "3.3", "OOS"]:
            fig.add_trace(go.Bar(
                name=LABEL_TH[c], x=zone_labels, y=zone_pv[c],
                marker_color=COLORS[c],
            ))
        fig.update_layout(
            barmode="stack", height=430,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis_title="จำนวน", xaxis_title="",
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_z2:
        st.subheader("Pass Rate (%) แต่ละเขตสุขภาพ")
        zone_stats = f.groupby("เขตสุขภาพ").agg(
            Total=("ลำดับ", "count"),
            Passed=("Passed", "sum"),
            OOS=("OutOfScope", "sum"),
        ).reset_index()
        zone_stats["In_Scope"] = zone_stats["Total"] - zone_stats["OOS"]
        zone_stats["Pass_Rate"] = (zone_stats["Passed"] / zone_stats["In_Scope"].replace(0, 1) * 100).round(1)
        zone_stats["Zone_Label"] = zone_stats["เขตสุขภาพ"].apply(lambda z: f"เขต {z}")
        zone_stats = zone_stats.sort_values("Pass_Rate", ascending=True)

        fig = px.bar(
            zone_stats, x="Pass_Rate", y="Zone_Label", orientation="h",
            text="Pass_Rate", color="Pass_Rate", color_continuous_scale="RdYlGn",
            hover_data=["Total", "Passed", "In_Scope"],
        )
        fig.update_layout(
            height=430, margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="% ผ่าน HC (จากในขอบเขต)", yaxis_title="",
            coloraxis_showscale=False,
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap: เขตสุขภาพ × HC group
    st.subheader("Heatmap: เขตสุขภาพ × กลุ่ม HC (จำนวนผลิตภัณฑ์)")
    zone_heat = f.groupby(["เขตสุขภาพ", "HC_Group_TH"]).size().unstack(fill_value=0)
    if not zone_heat.empty:
        zone_heat.index = [f"เขต {z}" for z in zone_heat.index]
        fig = px.imshow(
            zone_heat.values, x=zone_heat.columns, y=zone_heat.index,
            color_continuous_scale="Blues", aspect="auto", text_auto=True,
        )
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    # Zone detail table
    st.subheader("ตารางสรุปเขตสุขภาพ")
    zd = f.groupby("เขตสุขภาพ").agg(
        Total=("ลำดับ", "count"),
        Passed=("Passed", "sum"),
        Failed=("Failed", "sum"),
        Insufficient=("Insufficient", "sum"),
        OOS=("OutOfScope", "sum"),
    ).reset_index()
    zd["In_Scope"] = zd["Total"] - zd["OOS"]
    zd["Pass_Rate (%)"] = (zd["Passed"] / zd["In_Scope"].replace(0, 1) * 100).round(1)
    zd = zd.rename(columns={
        "เขตสุขภาพ": "เขต",
        "Total": "รวม",
        "Passed": "ผ่าน 3.1",
        "Failed": "ไม่ผ่าน 3.2",
        "Insufficient": "ข้อมูลไม่พอ 3.3",
        "OOS": "OOS",
        "In_Scope": "ในขอบเขต",
    })
    st.dataframe(zd, use_container_width=True, hide_index=True)

    st.divider()


# ════════════════════════════════════════════════════════════════════
# SECTION 5: FAILED NUTRIENT DEEP-DIVE
# ════════════════════════════════════════════════════════════════════
st.header("5️⃣ วิเคราะห์สารอาหารที่ทำให้ตก (Failed Nutrient)")

# Filter fail_df by same selection (using ลำดับ)
selected_ids = set(f[f["Criteria"] == "3.2"]["ลำดับ"].tolist())
ff = fail_df[fail_df["ลำดับ"].isin(selected_ids)] if len(selected_ids) > 0 else fail_df.iloc[0:0]

col_f1, col_f2 = st.columns([3, 2])

with col_f1:
    st.subheader("Top สารอาหารที่ทำให้ตก")
    if len(ff) > 0:
        top = ff["Failed_Nutrient"].value_counts().head(15).reset_index()
        top.columns = ["สารอาหาร", "จำนวน"]
        top = top.sort_values("จำนวน", ascending=True)
        fig = px.bar(
            top, x="จำนวน", y="สารอาหาร", orientation="h",
            text="จำนวน", color="จำนวน", color_continuous_scale="Reds",
        )
        fig.update_layout(
            height=500, margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="จำนวนผลิตภัณฑ์ที่ตก", yaxis_title="",
            coloraxis_showscale=False,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ไม่มีผลิตภัณฑ์ที่ตก (3.2) ในตัวกรองนี้")

with col_f2:
    st.subheader("สัดส่วนการตกของสารหลัก")
    if len(ff) > 0:
        # Map detailed nutrient → main category
        def categorize(n):
            n = str(n).lower()
            if "sugar" in n: return "น้ำตาล"
            if "sodium" in n: return "โซเดียม"
            if "satfat" in n: return "ไขมันอิ่มตัว"
            if "fat" in n: return "ไขมัน"
            if "energy" in n: return "พลังงาน"
            return "อื่นๆ"
        ff_cat = ff.copy()
        ff_cat["หมวด"] = ff_cat["Failed_Nutrient"].map(categorize)
        cat_counts = ff_cat["หมวด"].value_counts()
        fig = go.Figure(go.Pie(
            labels=cat_counts.index, values=cat_counts.values,
            hole=0.45, textinfo="label+percent",
        ))
        fig.update_layout(
            height=500, showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

# Heatmap: group × failed nutrient main category
if len(ff) > 0:
    st.subheader("Heatmap: กลุ่ม HC × หมวดสารอาหารที่ตก")
    def cat_main(n):
        n = str(n).lower()
        if "sugar" in n: return "น้ำตาล"
        if "sodium" in n: return "โซเดียม"
        if "satfat" in n: return "ไขมันอิ่มตัว"
        if "fat" in n: return "ไขมัน"
        if "energy" in n: return "พลังงาน"
        return "อื่นๆ"
    ff2 = ff.copy()
    ff2["หมวด"] = ff2["Failed_Nutrient"].map(cat_main)
    heat2 = ff2.groupby(["HC_Group_TH", "หมวด"]).size().unstack(fill_value=0)
    fig = px.imshow(
        heat2.values, x=heat2.columns, y=heat2.index,
        color_continuous_scale="Reds", aspect="auto", text_auto=True,
    )
    fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
# SECTION 5: PRODUCT DETAIL TABLE
# ════════════════════════════════════════════════════════════════════
st.header("6️⃣ ตารางรายละเอียดผลิตภัณฑ์")

search = st.text_input("🔎 ค้นหาในผลิตภัณฑ์ / ประเภท / จังหวัด", placeholder="พิมพ์คำค้นหา...")

cols_show = [
    "ลำดับ", "ผลิตภัณฑ์", "ประเภท (อย.)", "จังหวัด", "ภูมิภาค", "เขตสุขภาพ",
    "HC_Group_TH", "HC_Subgroup_TH", "Criteria",
    "พลังงาน/100", "น้ำตาล/100", "โซเดียม/100", "ไขมัน/100", "ไขมันอิ่มตัว/100",
    "Failed_Nutrients", "Missing_Nutrients",
]
cols_show = [c for c in cols_show if c in f.columns]

view = f[cols_show].copy()
if search:
    s = search.lower()
    mask = (
        view["ผลิตภัณฑ์"].astype(str).str.lower().str.contains(s, na=False) |
        view["ประเภท (อย.)"].astype(str).str.lower().str.contains(s, na=False) |
        view["จังหวัด"].astype(str).str.lower().str.contains(s, na=False)
    )
    view = view[mask]

st.caption(f"แสดง {len(view):,} จาก {len(f):,} รายการ")
st.dataframe(view, use_container_width=True, hide_index=True, height=400)

# Download button
csv = view.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "📥 ดาวน์โหลด CSV", csv,
    file_name=f"hc_filtered_{len(view)}_items.csv", mime="text/csv",
)

st.divider()
st.caption(
    "© Healthier Choice Evaluation Pipeline — Powered by Streamlit + Plotly  \n"
    "Source code: github.com/<your-username>/hc-dashboard"
)
