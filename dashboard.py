# -*- coding: utf-8 -*-
"""
HC Dashboard — Streamlit Single-Page App
ประเมิน Healthier Choice (HC) สำหรับผลิตภัณฑ์ GDA 2026 จำนวน 1,358 รายการ
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
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

# ── Palette ──────────────────────────────────────────────────────────
COLORS = {
    "3.1": "#1F8A4C",   # green  - ผ่าน
    "3.2": "#E5484D",   # red    - ไม่ผ่าน
    "3.3": "#F2B705",   # amber  - ข้อมูลไม่พอ
    "OOS": "#9AA8B2",   # gray   - นอกขอบเขต
}
LABEL_TH = {
    "3.1": "3.1 ผ่าน HC",
    "3.2": "3.2 ไม่ผ่าน HC",
    "3.3": "3.3 ข้อมูลไม่พอ",
    "OOS": "นอกขอบเขต (OOS)",
}
INK = "#16231F"        # primary text (near-black)
MUTED = "#3A4A44"      # secondary text (dark slate — clearly readable)
BRAND = "#1F8A4C"      # brand green
BRAND_DARK = "#15663A"

# light-capped heatmap scales → dark INK text stays readable on every cell
HEAT_GREEN = [[0.0, "#F2F9F5"], [0.45, "#A7DBB6"], [1.0, "#5FB37B"]]
HEAT_RED = [[0.0, "#FDF3F3"], [0.45, "#F3B4B6"], [1.0, "#E08A8E"]]
FONT_FAMILY = "'IBM Plex Sans Thai', 'Segoe UI', sans-serif"

DATA_FILE = Path(__file__).parent / "HC_Dashboard_Data_Public.xlsx"


# ════════════════════════════════════════════════════════════════════
# STYLING
# ════════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');

        /* apply Thai font broadly to text widgets (avoid icon fonts) */
        .stApp, .hero, .hero *, .kpi, .kpi *, .sec, .sec *, .insight,
        [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *,
        [data-testid="stMetric"], [data-testid="stMetric"] *,
        .stMultiSelect, .stMultiSelect *, .stSelectbox, .stSelectbox *,
        .stTextInput, .stTextInput *, .stButton, .stDownloadButton,
        h1, h2, h3, h4, p {{
            font-family: {FONT_FAMILY} !important;
        }}
        .stApp {{ background: #F6F9F7; }}

        /* hide default chrome */
        #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px; }}

        /* ── Hero header ── */
        .hero {{
            background: linear-gradient(120deg, {BRAND} 0%, {BRAND_DARK} 100%);
            border-radius: 18px;
            padding: 26px 32px;
            color: #fff;
            box-shadow: 0 10px 30px rgba(31,138,76,0.25);
            margin-bottom: 22px;
        }}
        .hero h1 {{
            font-size: 1.85rem; font-weight: 700; margin: 0 0 6px 0; color: #fff !important;
            letter-spacing: -0.5px;
        }}
        .hero p {{ font-size: 0.98rem; margin: 0; color: rgba(255,255,255,0.97) !important; }}
        .hero .badge {{ color: #fff !important; }}
        .hero .badge {{
            display: inline-block; background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.35);
            padding: 3px 12px; border-radius: 999px; font-size: 0.8rem;
            margin-top: 12px; font-weight: 500;
        }}

        /* ── KPI cards ── */
        .kpi-row {{ display: flex; gap: 14px; margin-bottom: 8px; flex-wrap: wrap; }}
        .kpi {{
            flex: 1; min-width: 150px; background: #fff; border-radius: 14px;
            padding: 18px 20px; border: 1px solid #E6EDE9;
            border-top: 4px solid var(--accent);
            box-shadow: 0 2px 10px rgba(26,43,39,0.04);
            transition: transform .15s ease, box-shadow .15s ease;
        }}
        .kpi:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(26,43,39,0.10); }}
        .kpi .label {{ font-size: 0.85rem; color: {INK}; font-weight: 600; margin-bottom: 6px; }}
        .kpi .value {{ font-size: 2.0rem; font-weight: 700; color: {INK}; line-height: 1.1; }}
        .kpi .pct {{ font-size: 0.85rem; font-weight: 600; color: {MUTED}; margin-top: 2px; }}

        /* ── Section header ── */
        .sec {{
            display: flex; align-items: center; gap: 12px;
            margin: 8px 0 6px 0;
        }}
        .sec .num {{
            background: {BRAND}; color: #fff; width: 32px; height: 32px;
            border-radius: 9px; display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 1rem; flex-shrink: 0;
        }}
        .sec .title {{ font-size: 1.3rem; font-weight: 700; color: {INK}; }}
        .sec-sub {{ color: {MUTED}; font-size: 0.9rem; margin: 0 0 6px 44px; }}

        /* insight banner */
        .insight {{
            background: #EAF6EF; border-left: 4px solid {BRAND};
            border-radius: 10px; padding: 12px 18px; color: {BRAND_DARK};
            font-size: 0.92rem; margin: 6px 0 14px 0;
        }}

        /* subheaders + all body text dark */
        h1, h2, h3, h4, h5, h6 {{ color: {INK} !important; font-weight: 600 !important; }}
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span {{ color: {INK}; }}

        /* st.caption — Streamlit renders these very faint; force readable */
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p,
        small, .stCaption {{ color: {MUTED} !important; }}

        /* dataframe text */
        [data-testid="stDataFrame"] {{ color: {INK}; }}

        /* sidebar */
        section[data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid #E6EDE9; }}
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{ color: {INK} !important; }}
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
            background: {BRAND} !important;
        }}

        /* dataframe rounding */
        [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; border: 1px solid #E6EDE9; }}

        /* divider tighten */
        hr {{ margin: 1.2rem 0; border-color: #E6EDE9; }}

        /* download button */
        .stDownloadButton button {{
            background: {BRAND}; color: #fff; border: none; border-radius: 9px;
            font-weight: 600; padding: 8px 20px;
        }}
        .stDownloadButton button:hover {{ background: {BRAND_DARK}; color: #fff; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_cards(items):
    """items: list of (label, value, pct_text, accent_color)"""
    cards = "".join(
        f"""<div class="kpi" style="--accent:{color}">
              <div class="label">{label}</div>
              <div class="value">{value}</div>
              <div class="pct">{pct}</div>
            </div>"""
        for label, value, pct, color in items
    )
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)


def section(num, title, subtitle=""):
    st.markdown(
        f'<div class="sec"><div class="num">{num}</div>'
        f'<div class="title">{title}</div></div>'
        + (f'<p class="sec-sub">{subtitle}</p>' if subtitle else ""),
        unsafe_allow_html=True,
    )


# ── Shared Plotly template ──────────────────────────────────────────
pio.templates["hc"] = go.layout.Template(
    layout=dict(
        font=dict(family=FONT_FAMILY, color=INK, size=14),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[BRAND, "#E5484D", "#F2B705", "#3B82C4", "#9AA8B2", "#7C5CBF"],
        xaxis=dict(gridcolor="#E2EAE6", zerolinecolor="#D5DEDA", automargin=True,
                   tickfont=dict(color=INK, size=13), title=dict(font=dict(color=INK, size=13))),
        yaxis=dict(gridcolor="#E2EAE6", zerolinecolor="#D5DEDA", automargin=True,
                   tickfont=dict(color=INK, size=13), title=dict(font=dict(color=INK, size=13))),
        legend=dict(font=dict(size=13, color=INK)),
        title=dict(font=dict(size=15, color=INK)),
    )
)
pio.templates.default = "hc"


def show(fig, height=None):
    """Apply consistent template + render. theme=None → use our 'hc' template
    instead of Streamlit's default gray plotly theme.
    automargin=True lets axes expand to fit long Thai tick labels."""
    fig.update_layout(template="hc", font=dict(family=FONT_FAMILY, color=INK, size=14))
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    if height:
        fig.update_layout(height=height)
    # crisp bar labels: dark outside (on white), white inside (on colored bars)
    fig.update_traces(
        selector=dict(type="bar"),
        outsidetextfont=dict(family=FONT_FAMILY, color=INK, size=13),
        insidetextfont=dict(family=FONT_FAMILY, color="#FFFFFF", size=13),
    )
    # pie / donut labels
    fig.update_traces(
        selector=dict(type="pie"),
        textfont=dict(family=FONT_FAMILY, size=13),
        insidetextfont=dict(family=FONT_FAMILY, color="#FFFFFF", size=13),
    )
    # heatmap cell numbers: dark INK text (scales capped light → always readable)
    fig.update_traces(
        selector=dict(type="heatmap"),
        textfont=dict(family=FONT_FAMILY, size=12, color=INK),
    )
    st.plotly_chart(fig, use_container_width=True, theme=None,
                    config={"displayModeBar": False})


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

inject_css()


# ════════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ════════════════════════════════════════════════════════════════════
st.sidebar.markdown(
    f"<div style='font-size:1.15rem;font-weight:700;color:{INK};margin-bottom:2px'>"
    f"🔍 ตัวกรอง</div>"
    f"<div style='font-size:0.82rem;color:{MUTED};margin-bottom:10px'>"
    f"กรองข้อมูลก่อนดูทุก section ด้านขวา</div>",
    unsafe_allow_html=True,
)

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
# HERO HEADER + KPI CARDS
# ════════════════════════════════════════════════════════════════════
total = len(f)
n31 = int((f["Criteria"] == "3.1").sum())
n32 = int((f["Criteria"] == "3.2").sum())
n33 = int((f["Criteria"] == "3.3").sum())
noos = int((f["Criteria"] == "OOS").sum())
in_scope = total - noos

st.markdown(
    f"""
    <div class="hero">
      <h1>🥗 Healthier Choice Evaluation — GDA 2026</h1>
      <p>ภาพรวมการประเมินผลิตภัณฑ์ตามเกณฑ์ <b>ทางเลือกสุขภาพ (HC)</b> ของไทย
      — จำแนกเป็น 3.1 ผ่าน / 3.2 ไม่ผ่าน / 3.3 ข้อมูลไม่พอ / OOS นอกขอบเขต</p>
      <span class="badge">📦 {total:,} ผลิตภัณฑ์ที่เลือก จากทั้งหมด {len(df):,} รายการ</span>
    </div>
    """,
    unsafe_allow_html=True,
)

pct = lambda n: f"{n/total*100:.1f}% ของทั้งหมด" if total else "—"
kpi_cards([
    ("ผลิตภัณฑ์ทั้งหมด", f"{total:,}", "100%", BRAND),
    ("✅ ผ่าน HC (3.1)", f"{n31:,}", pct(n31), COLORS["3.1"]),
    ("❌ ไม่ผ่าน (3.2)", f"{n32:,}", pct(n32), COLORS["3.2"]),
    ("⚠️ ข้อมูลไม่พอ (3.3)", f"{n33:,}", pct(n33), COLORS["3.3"]),
    ("➖ นอกขอบเขต", f"{noos:,}", pct(noos), COLORS["OOS"]),
])

if in_scope > 0:
    st.markdown(
        f'<div class="insight">📊 <b>อยู่ในขอบเขต HC</b> {in_scope:,} รายการ — '
        f'ผ่าน <b>{n31/in_scope*100:.1f}%</b> · ไม่ผ่าน <b>{n32/in_scope*100:.1f}%</b> · '
        f'ข้อมูลไม่พอ <b>{n33/in_scope*100:.1f}%</b></div>',
        unsafe_allow_html=True,
    )

st.write("")


# ════════════════════════════════════════════════════════════════════
# SECTION 1: OVERVIEW
# ════════════════════════════════════════════════════════════════════
section("1", "ภาพรวม", "Overview — สัดส่วนผลการประเมินและจำนวนตามกลุ่ม HC")

col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("สัดส่วน Criteria")
    crit_counts = f["Criteria"].value_counts().reindex(["3.1", "3.2", "3.3", "OOS"]).fillna(0)
    fig = go.Figure(go.Pie(
        labels=[LABEL_TH[c] for c in crit_counts.index],
        values=crit_counts.values,
        hole=0.58,
        marker=dict(colors=[COLORS[c] for c in crit_counts.index],
                    line=dict(color="#FFFFFF", width=2)),
        texttemplate="%{percent:.1%}",      # percent inside slices (no outside overflow)
        textposition="inside",
        insidetextorientation="horizontal",
        sort=False,
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True, height=400,
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5),
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text=f"<b>{total:,}</b><br>รายการ", x=0.5, y=0.5,
                          font=dict(size=18, color=INK), showarrow=False)],
    )
    show(fig)

with col_b:
    st.subheader("จำนวนผลิตภัณฑ์ตามกลุ่ม HC")
    grp = f.groupby("HC_Group_TH").size().reset_index(name="จำนวน").sort_values("จำนวน", ascending=True)
    fig = px.bar(
        grp, x="จำนวน", y="HC_Group_TH", orientation="h",
        text="จำนวน", color="จำนวน", color_continuous_scale="Greens",
    )
    fig.update_layout(
        height=400, margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="จำนวน", yaxis_title="",
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside")
    show(fig)

st.write("")


# ════════════════════════════════════════════════════════════════════
# SECTION 2: HC GROUP ANALYSIS
# ════════════════════════════════════════════════════════════════════
section("2", "วิเคราะห์ตามกลุ่ม HC", "HC Group Analysis — เปรียบเทียบ 15 กลุ่มอาหาร")

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
show(fig)

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

st.write("")


# ════════════════════════════════════════════════════════════════════
# SECTION 3: GEOGRAPHIC VIEW
# ════════════════════════════════════════════════════════════════════
section("3", "มุมมองภูมิภาค", "Geographic — แยกตามภูมิภาคและจังหวัด")

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
    show(fig)

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
        show(fig)
    else:
        st.info("จังหวัดที่มี ≥10 ผลิตภัณฑ์ในตัวกรองนี้ไม่เพียงพอ")

# Heatmap: region × HC group (count)
st.subheader("Heatmap: ภูมิภาค × กลุ่ม HC (จำนวนผลิตภัณฑ์)")
heat = f.groupby(["ภูมิภาค", "HC_Group_TH"]).size().unstack(fill_value=0)
if not heat.empty:
    fig = px.imshow(
        heat.values, x=heat.columns, y=heat.index,
        color_continuous_scale=HEAT_GREEN, aspect="auto", text_auto=True,
    )
    fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
    show(fig)

st.write("")


# ════════════════════════════════════════════════════════════════════
# SECTION 4: HEALTH ZONE ANALYSIS (เขตสุขภาพ)
# ════════════════════════════════════════════════════════════════════
if "เขตสุขภาพ" in f.columns:
    section("4", "วิเคราะห์ตามเขตสุขภาพ", "Health Zone — เขตสุขภาพ 1-13 ของกระทรวงสาธารณสุข")
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
        show(fig)

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
        show(fig)

    # Heatmap: เขตสุขภาพ × HC group
    st.subheader("Heatmap: เขตสุขภาพ × กลุ่ม HC (จำนวนผลิตภัณฑ์)")
    zone_heat = f.groupby(["เขตสุขภาพ", "HC_Group_TH"]).size().unstack(fill_value=0)
    if not zone_heat.empty:
        zone_heat.index = [f"เขต {z}" for z in zone_heat.index]
        fig = px.imshow(
            zone_heat.values, x=zone_heat.columns, y=zone_heat.index,
            color_continuous_scale=HEAT_GREEN, aspect="auto", text_auto=True,
        )
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
        show(fig)

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

    st.write("")


# ════════════════════════════════════════════════════════════════════
# SECTION 5: FAILED NUTRIENT DEEP-DIVE
# ════════════════════════════════════════════════════════════════════
section("5", "สารอาหารที่ทำให้ตก", "Failed Nutrient Deep-dive — น้ำตาล/โซเดียม/ไขมัน ฯลฯ")

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
        show(fig)
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
        show(fig)

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
        color_continuous_scale=HEAT_RED, aspect="auto", text_auto=True,
    )
    fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
    show(fig)

st.write("")


# ════════════════════════════════════════════════════════════════════
# SECTION 5: PRODUCT DETAIL TABLE
# ════════════════════════════════════════════════════════════════════
section("6", "ตารางรายละเอียดผลิตภัณฑ์", "Product Detail — ค้นหาและดาวน์โหลด")

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

st.write("")
st.caption(
    "© Healthier Choice Evaluation Pipeline — Powered by Streamlit + Plotly  \n"
    "Source code: github.com/<your-username>/hc-dashboard"
)
