# -*- coding: utf-8 -*-
"""
HC Dashboard — Multi-page Streamlit App (dark theme)
ประเมิน Healthier Choice (HC) สำหรับผลิตภัณฑ์ GDA หลายปีข้อมูล —
เลือกปีได้จากตัวกรอง "📅 ปีข้อมูล (GDA)" ในแถบด้านข้าง (ทุกหน้าคำนวณตามปีที่เลือก)
"""
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# ════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HC Dashboard — GDA",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "HC_Dashboard_Data_Public.xlsx"

# ── Palette (dark) ───────────────────────────────────────────────────
COLORS = {
    "3.1": "#2FBF8F",   # emerald - ผ่าน
    "3.2": "#FF6B6B",   # coral   - ไม่ผ่าน
    "3.3": "#FFC857",   # amber   - ข้อมูลไม่พอ
    "OOS": "#7E97A3",   # slate   - นอกขอบเขต
}
LABEL_TH = {
    "3.1": "3.1 ผ่าน HC",
    "3.2": "3.2 ไม่ผ่าน HC",
    "3.3": "3.3 ข้อมูลไม่พอ",
    "OOS": "นอกขอบเขต (OOS)",
}
INK = "#E8F2EF"        # primary light text
MUTED = "#9DB5AE"      # secondary muted text
TEAL = "#2FBF8F"
CYAN = "#37C7C7"
BLUE = "#4DA3E8"
ORANGE = "#F2934A"
VIOLET = "#9B8CFF"
CARD_BORDER = "rgba(255,255,255,0.10)"

FONT_FAMILY = "'IBM Plex Sans Thai', 'Segoe UI', sans-serif"

# dark heatmap scales
HEAT_GREEN = [[0.0, "#0E332C"], [0.5, "#1E7A5C"], [1.0, "#34D399"]]
HEAT_RED = [[0.0, "#3A1A1C"], [0.5, "#9E3B40"], [1.0, "#FF6B6B"]]


# ════════════════════════════════════════════════════════════════════
# PLOTLY DARK TEMPLATE
# ════════════════════════════════════════════════════════════════════
pio.templates["hcdark"] = go.layout.Template(
    layout=dict(
        font=dict(family=FONT_FAMILY, color=INK, size=14),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[TEAL, CYAN, BLUE, ORANGE, VIOLET, "#FF6B6B"],
        xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.12)",
                   automargin=True, tickfont=dict(color=INK, size=13),
                   title=dict(font=dict(color=MUTED, size=13))),
        yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.12)",
                   automargin=True, tickfont=dict(color=INK, size=13),
                   title=dict(font=dict(color=MUTED, size=13))),
        legend=dict(font=dict(size=13, color=INK)),
        title=dict(font=dict(size=15, color=INK)),
    )
)
pio.templates.default = "hcdark"


def show(fig, height=None):
    """Apply consistent dark template + render."""
    fig.update_layout(template="hcdark", font=dict(family=FONT_FAMILY, color=INK, size=14))
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    if height:
        fig.update_layout(height=height)
    fig.update_traces(
        selector=dict(type="bar"),
        outsidetextfont=dict(family=FONT_FAMILY, color=INK, size=13),
        insidetextfont=dict(family=FONT_FAMILY, color="#0C2826", size=13),
    )
    fig.update_traces(
        selector=dict(type="pie"),
        textfont=dict(family=FONT_FAMILY, size=13),
        insidetextfont=dict(family=FONT_FAMILY, color="#0C2826", size=13),
    )
    fig.update_traces(
        selector=dict(type="heatmap"),
        textfont=dict(family=FONT_FAMILY, size=12, color=INK),
    )
    st.plotly_chart(fig, use_container_width=True, theme=None,
                    config={"displayModeBar": False})


def show_scrollable(fig, width, height=560):
    """Render a fixed-width chart that scrolls left-right (via an HTML iframe,
    bypassing Streamlit's auto-resize)."""
    fig.update_layout(template="hcdark", autosize=False, width=int(width), height=height,
                      font=dict(family=FONT_FAMILY, color=INK, size=14),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    html = fig.to_html(include_plotlyjs="cdn", full_html=False,
                       config={"displayModeBar": False, "responsive": False})
    wrapper = (
        "<style>@import url('https://fonts.googleapis.com/css2?"
        "family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');"
        "html,body{margin:0;padding:0;background:#11302B;}"
        "*{font-family:'IBM Plex Sans Thai',sans-serif;}"
        "::-webkit-scrollbar{height:10px;}"
        "::-webkit-scrollbar-thumb{background:#2FBF8F;border-radius:6px;}</style>"
        f"<div style='overflow-x:auto;width:100%;'>{html}</div>"
    )
    components.html(wrapper, height=height + 30, scrolling=False)


# ════════════════════════════════════════════════════════════════════
# STYLING
# ════════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');

        .stApp, .stApp * {{ font-family: {FONT_FAMILY}; }}

        /* keep Material Symbols icon font on icon spans (don't let Thai font break ligatures) */
        span[data-testid="stIconMaterial"], [data-testid="stIconMaterial"],
        [class*="material-symbols"], [class*="material-icons"] {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                         'Material Icons' !important;
        }}

        /* teal-green gradient canvas (lightened) */
        .stApp {{
            background:
              radial-gradient(1200px 600px at 80% -10%, rgba(55,199,199,0.16), transparent 60%),
              radial-gradient(1000px 700px at -10% 110%, rgba(47,191,143,0.18), transparent 55%),
              linear-gradient(135deg, #154E45 0%, #1B5A50 45%, #246B5E 100%);
        }}

        /* hide default chrome but KEEP the sidebar expand button usable */
        #MainMenu, footer {{ visibility: hidden; height: 0; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stDecoration"] {{ display: none; }}
        [data-testid="stAppDeployButton"], [data-testid="stStatusWidget"] {{ display: none; }}

        /* allow wide (fixed-width) charts to scroll left-right inside their card */
        [data-testid="stPlotlyChart"] {{ overflow-x: auto; overflow-y: hidden; }}

        /* sidebar collapse / expand buttons — clearly visible teal pills */
        button[data-testid="stExpandSidebarButton"],
        [data-testid="stExpandSidebarButton"] button,
        button[data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] button {{
            background: rgba(47,191,143,0.95) !important;
            border-radius: 10px !important; border: none !important;
        }}
        button[data-testid="stExpandSidebarButton"] *,
        [data-testid="stExpandSidebarButton"] button *,
        button[data-testid="stSidebarCollapseButton"] *,
        [data-testid="stSidebarCollapseButton"] button * {{
            color: #0C2826 !important;
        }}
        button[data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stSidebarCollapseButton"] button:hover {{
            background: {CYAN} !important;
        }}
        .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px; }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B2B29 0%, #0E332E 100%);
            border-right: 1px solid {CARD_BORDER};
        }}
        section[data-testid="stSidebar"] * {{ color: {INK}; }}
        .brand {{
            display: flex; align-items: center; gap: 12px;
            background: linear-gradient(120deg, rgba(47,191,143,0.18), rgba(55,199,199,0.10));
            border: 1px solid {CARD_BORDER}; border-radius: 16px;
            padding: 14px 16px; margin-bottom: 14px;
        }}
        .brand .logo {{
            width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
            background: linear-gradient(135deg, {TEAL}, {CYAN});
            display: flex; align-items: center; justify-content: center; font-size: 22px;
        }}
        .brand .t1 {{ font-size: 0.72rem; letter-spacing: 1.5px; color: {MUTED}; font-weight: 600; }}
        .brand .t2 {{ font-size: 1.05rem; font-weight: 700; color: #fff; line-height: 1.15; }}

        /* nav links from st.navigation — keep Streamlit's own layout, only restyle */
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{
            border-radius: 10px;
        }}
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{
            background: rgba(255,255,255,0.06);
        }}
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: linear-gradient(120deg, rgba(47,191,143,0.28), rgba(55,199,199,0.16));
            box-shadow: inset 0 0 0 1px rgba(47,191,143,0.45);
        }}
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] span {{
            white-space: nowrap;
        }}
        /* menu font = 16pt */
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"],
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] *:not([data-testid="stIconMaterial"]) {{
            font-size: 16pt !important;
            line-height: 1.5 !important;
        }}
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] span[data-testid="stIconMaterial"] {{
            font-size: 18pt !important;
        }}
        /* tidy nav heading + spacing */
        [data-testid="stSidebarNav"] {{ margin-bottom: 6px; }}

        /* ── Hero header ── */
        .hero {{
            background: linear-gradient(120deg, rgba(47,191,143,0.22) 0%, rgba(55,199,199,0.12) 60%, rgba(77,163,232,0.10) 100%);
            border: 1px solid {CARD_BORDER};
            border-radius: 20px; padding: 22px 28px; margin-bottom: 18px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.28);
        }}
        .hero h1 {{ font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0; color: #fff !important; letter-spacing: -0.3px; }}
        .hero p {{ font-size: 0.95rem; margin: 0; color: {INK} !important; }}
        .hero .badge {{
            display: inline-block; background: rgba(255,255,255,0.12);
            border: 1px solid {CARD_BORDER}; padding: 4px 14px; border-radius: 999px;
            font-size: 0.82rem; margin-top: 12px; font-weight: 500; color: #fff !important;
        }}

        /* ── KPI cards ── */
        .kpi-row {{ display: flex; gap: 16px; margin: 4px 0 8px 0; flex-wrap: wrap; }}
        .kpi {{
            flex: 1; min-width: 170px; border-radius: 18px; padding: 18px 20px;
            border: 1px solid {CARD_BORDER};
            background: var(--grad);
            box-shadow: 0 10px 26px rgba(0,0,0,0.30);
            transition: transform .15s ease, box-shadow .15s ease;
        }}
        .kpi:hover {{ transform: translateY(-4px); box-shadow: 0 16px 34px rgba(0,0,0,0.40); }}
        .kpi .label {{ font-size: 0.84rem; color: rgba(255,255,255,0.92); font-weight: 600; margin-bottom: 8px; }}
        .kpi .value {{ font-size: 2.05rem; font-weight: 700; color: #fff; line-height: 1.05; }}
        .kpi .pct {{ font-size: 0.82rem; font-weight: 600; color: rgba(255,255,255,0.85); margin-top: 4px; }}

        /* ── glass content cards (st.container border=True) ── */
        [data-testid="stVerticalBlockBorderWrapper"]:has(> div > div [data-testid="stVerticalBlock"]) {{ }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(255,255,255,0.04);
            border: 1px solid {CARD_BORDER} !important;
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        }}

        /* section header */
        .sec {{ display: flex; align-items: center; gap: 12px; margin: 6px 0 4px 0; }}
        .sec .num {{
            background: linear-gradient(135deg, {TEAL}, {CYAN}); color: #0C2826;
            width: 34px; height: 34px; border-radius: 10px; display: flex;
            align-items: center; justify-content: center; font-weight: 700; font-size: 1rem; flex-shrink: 0;
        }}
        .sec .title {{ font-size: 1.25rem; font-weight: 700; color: #fff; }}
        .sec-sub {{ color: {MUTED}; font-size: 0.9rem; margin: 0 0 8px 46px; }}

        /* insight banner */
        .insight {{
            background: linear-gradient(120deg, rgba(47,191,143,0.16), rgba(55,199,199,0.08));
            border-left: 4px solid {TEAL}; border-radius: 12px; padding: 12px 18px;
            color: {INK}; font-size: 0.92rem; margin: 8px 0 14px 0;
        }}

        h1, h2, h3, h4, h5, h6 {{ color: #fff !important; }}
        [data-testid="stMetricValue"] {{ color: #fff; }}

        /* download button */
        .stDownloadButton button {{
            background: linear-gradient(135deg, {TEAL}, {CYAN}); color: #0C2826; border: none;
            border-radius: 10px; font-weight: 700; padding: 8px 20px;
        }}
        .stDownloadButton button:hover {{ filter: brightness(1.07); color: #0C2826; }}

        hr {{ border-color: {CARD_BORDER}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section(num, title, subtitle=""):
    st.markdown(
        f'<div class="sec"><div class="num">{num}</div>'
        f'<div class="title">{title}</div></div>'
        + (f'<p class="sec-sub">{subtitle}</p>' if subtitle else ""),
        unsafe_allow_html=True,
    )


def kpi_cards(items):
    """items: list of (label, value, pct_text, gradient_css)"""
    cards = "".join(
        f"""<div class="kpi" style="--grad:{grad}">
              <div class="label">{label}</div>
              <div class="value">{value}</div>
              <div class="pct">{pct}</div>
            </div>"""
        for label, value, pct, grad in items
    )
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# DATA LOADING (cached)
# ════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="กำลังโหลดข้อมูล...")
def load_data(mtime):
    """mtime = cache key: invalidates the cache when the xlsx is regenerated in place."""
    data = pd.read_excel(DATA_FILE, sheet_name="1_Data")
    fail_detail = pd.read_excel(DATA_FILE, sheet_name="6_Failed_Detail")
    return data, fail_detail


def _rules_to_nutrients(rules):
    keys = " ".join(rules.keys()).lower()
    s = set()
    if "sugar" in keys: s.add("sugar")
    if "sodium" in keys: s.add("sodium")
    if "saturated_fat" in keys or "satfat" in keys: s.add("satfat")
    if "energy" in keys: s.add("energy")
    for k in rules:
        kl = k.lower()
        if "fat" in kl and "saturated" not in kl and "satfat" not in kl:
            s.add("fat")
    return s


@st.cache_data(show_spinner=False)
def load_criteria_nutrient_map_sub(mtime):
    """From sheet 8: unit (Subgroup_TH ถ้ามี ไม่งั้น HC_Group_TH) → set of nutrients.
    mtime = cache key (invalidates when the xlsx is regenerated in place)."""
    try:
        ref = pd.read_excel(DATA_FILE, sheet_name="8_HC_Criteria_Reference")
    except Exception:
        return {}
    m = {}
    for _, row in ref.iterrows():
        sub = row.get("Subgroup_TH")
        grp = str(row.get("HC_Group_TH", "")).strip()
        unit = str(sub).strip() if (pd.notna(sub) and str(sub).strip() not in ("", "nan")) else grp
        raw = row.get("Rules", "")
        try:
            rules = json.loads(raw) if isinstance(raw, str) and raw.strip() else {}
        except Exception:
            rules = {}
        m.setdefault(unit, set()).update(_rules_to_nutrients(rules))
    return m


# ════════════════════════════════════════════════════════════════════
# SIDEBAR (brand + Looker-style dropdown filters)
# ════════════════════════════════════════════════════════════════════
def _set_state(key, value):
    st.session_state[key] = value


def _only_state(key, sel_key):
    """isolate a single value (Looker 'Only'); then reset the picker."""
    v = st.session_state.get(sel_key)
    if v is not None:
        st.session_state[key] = [v]
    st.session_state[sel_key] = None


def filter_dropdown(label, key, options, fmt=None, empty_means_all=False, help_text=None):
    """Looker-style filter: a button that opens a dropdown with
    'เลือกเฉพาะค่าเดียว' picker + ทั้งหมด / ล้าง buttons + a checkbox multiselect."""
    options = list(options)
    if key not in st.session_state:
        st.session_state[key] = [] if empty_means_all else list(options)
    # keep selection valid against current options (cascading filters)
    st.session_state[key] = [v for v in st.session_state[key] if v in options]
    sel = st.session_state[key]
    n, total = len(sel), len(options)
    if empty_means_all:
        summary = "ทั้งหมด" if n == 0 else (fmt(sel[0]) if (fmt and n == 1) else f"{n} รายการ")
    else:
        summary = "ทั้งหมด" if n == total else (
            (fmt(sel[0]) if (fmt and n == 1) else f"{n}/{total}") if n else "—")

    only_key = f"{key}__only"
    if only_key not in st.session_state:
        st.session_state[only_key] = None
    if st.session_state[only_key] not in options:
        st.session_state[only_key] = None

    with st.sidebar.popover(f"{label}  ·  {summary}", use_container_width=True):
        # ── เลือกเฉพาะค่าเดียวในคลิกเดียว (เหมือน "Only" ของ Looker) ──
        st.selectbox(
            "เลือกเฉพาะค่าเดียว", options, key=only_key,
            placeholder="⚡ เลือกเฉพาะค่าเดียว…",
            format_func=(fmt or (lambda x: str(x))),
            on_change=_only_state, args=(key, only_key),
            label_visibility="collapsed",
        )
        b1, b2 = st.columns(2)
        b1.button("เลือกทั้งหมด", key=f"{key}__all", use_container_width=True,
                  on_click=_set_state, args=(key, list(options)))
        b2.button("ล้าง", key=f"{key}__clr", use_container_width=True,
                  on_click=_set_state, args=(key, []))
        st.caption("หรือติ๊กหลายค่าด้านล่าง")
        st.multiselect(label, options, key=key,
                       format_func=(fmt or (lambda x: x)),
                       label_visibility="collapsed", placeholder="เลือกค่า...")
        if help_text:
            st.caption(help_text)
    return st.session_state[key]


def _reset_year_dependent_filters():
    # เปลี่ยนปี = ล้างตัวกรองที่ขึ้นกับปี (ตัวเลือกต่างกันในแต่ละปี; ค่าค้างจะตัดค่าที่มี
    # เฉพาะบางปีออกเงียบ ๆ เช่น ผลิตภัณฑ์นม ที่มีเฉพาะปี 2569)
    for k in ("f_regions", "f_zones", "f_provs", "f_groups", "f_crits"):
        st.session_state.pop(k, None)


def build_sidebar_filters(df):
    """Render sidebar filters; return (filtered_df, selected_year, year_total)."""
    st.sidebar.markdown(
        '<div class="brand">'
        '<div class="logo">🥗</div>'
        '<div><div class="t1">HEALTHIER CHOICE</div>'
        '<div class="t2">HC Dashboard</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"<div style='font-size:1.0rem;font-weight:700;color:#fff;margin:6px 0 2px'>🔍 ตัวกรอง</div>"
        f"<div style='font-size:0.8rem;color:{MUTED};margin-bottom:8px'>"
        f"คลิกแต่ละปุ่มเพื่อเลือกค่า (ใช้ร่วมกันทุกหน้า)</div>",
        unsafe_allow_html=True,
    )

    # ── ปีข้อมูล: เลือกได้ทีละปี (ค่าเริ่มต้น = ปีล่าสุด) — กรองก่อนตัวกรองอื่นทั้งหมด ──
    years = [int(y) for y in sorted(df["ปี"].dropna().unique(), reverse=True)]
    sel_year = st.sidebar.selectbox("📅 ปีข้อมูล (GDA)", years, index=0, key="f_year",
                                    on_change=_reset_year_dependent_filters)
    df = df[df["ปี"] == sel_year]

    regions = sorted(df["ภูมิภาค"].dropna().unique().tolist())
    sel_regions = filter_dropdown("🌏 ภูมิภาค", "f_regions", regions)

    if "เขตสุขภาพ" in df.columns:
        zones = sorted(df["เขตสุขภาพ"].dropna().unique().tolist())
        sel_zones = filter_dropdown("🏥 เขตสุขภาพ", "f_zones", zones,
                                    fmt=lambda z: f"เขต {z}")
    else:
        sel_zones = None

    provs_available = sorted(
        df[df["ภูมิภาค"].isin(sel_regions)]["จังหวัด"].dropna().unique().tolist())
    sel_provs = filter_dropdown("📍 จังหวัด", "f_provs", provs_available,
                                empty_means_all=True,
                                help_text="ว่าง = ทุกจังหวัดในภูมิภาคที่เลือก")

    groups = sorted(df["HC_Group_TH"].dropna().unique().tolist())
    sel_groups = filter_dropdown("🍱 กลุ่ม HC", "f_groups", groups)

    crits = ["3.1", "3.2", "3.3", "OOS"]
    sel_crits = filter_dropdown("📊 เกณฑ์ Criteria", "f_crits", crits,
                                fmt=lambda x: LABEL_TH.get(x, x))

    f = df[df["ภูมิภาค"].isin(sel_regions) & df["HC_Group_TH"].isin(sel_groups)
           & df["Criteria"].isin(sel_crits)]
    if sel_provs:
        f = f[f["จังหวัด"].isin(sel_provs)]
    if sel_zones is not None and "เขตสุขภาพ" in f.columns:
        f = f[f["เขตสุขภาพ"].isin(sel_zones)]

    st.sidebar.divider()
    st.sidebar.metric("รายการที่เลือก", f"{len(f):,} / {len(df):,}")
    st.sidebar.caption(f"ทุกหน้าคำนวณจาก subset นี้ · ข้อมูล GDA {sel_year} (anonymized)")
    return f, sel_year, len(df)


# ════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════
def hero(title, subtitle, badge):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p>'
        f'<span class="badge">{badge}</span></div>',
        unsafe_allow_html=True,
    )


def page_overview():
    f = FILTERED
    total = len(f)
    n31 = int((f["Criteria"] == "3.1").sum())
    n32 = int((f["Criteria"] == "3.2").sum())
    n33 = int((f["Criteria"] == "3.3").sum())
    noos = int((f["Criteria"] == "OOS").sum())
    in_scope = total - noos

    hero(f"🥗 การประเมินผลิตภัณฑ์ที่ได้รับการส่งเสริมตรวจฉลากโภชนาการ "
         f"ปีงบประมาณ {SELECTED_YEAR}<br>ตามเกณฑ์ Healthier Choice",
         f"สรุปผลการประเมินผลิตภัณฑ์ตามเกณฑ์ทางเลือกสุขภาพ (HC) ของไทย — GDA {SELECTED_YEAR}",
         f"📦 {total:,} ผลิตภัณฑ์ที่เลือก จากทั้งหมด {YEAR_TOTAL:,} รายการ")

    pct = lambda n: f"{n/total*100:.1f}% ของทั้งหมด" if total else "—"
    kpi_cards([
        ("ผลิตภัณฑ์ทั้งหมด", f"{total:,}", "100%",
         "linear-gradient(135deg,#1FA88A,#37C7C7)"),
        ("✅ ผ่าน HC (3.1)", f"{n31:,}", pct(n31),
         "linear-gradient(135deg,#1E9E76,#2FBF8F)"),
        ("❌ ไม่ผ่าน (3.2)", f"{n32:,}", pct(n32),
         "linear-gradient(135deg,#C94B53,#FF6B6B)"),
        ("⚠️ ข้อมูลไม่พอ (3.3)", f"{n33:,}", pct(n33),
         "linear-gradient(135deg,#C9942F,#FFC857)"),
        ("➖ นอกขอบเขต", f"{noos:,}", pct(noos),
         "linear-gradient(135deg,#4B6470,#7E97A3)"),
    ])

    if in_scope > 0:
        st.markdown(
            f'<div class="insight">📊 <b>อยู่ในขอบเขต HC</b> {in_scope:,} รายการ — '
            f'ผ่าน <b>{n31/in_scope*100:.1f}%</b> · ไม่ผ่าน <b>{n32/in_scope*100:.1f}%</b> · '
            f'ข้อมูลไม่พอ <b>{n33/in_scope*100:.1f}%</b></div>',
            unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.6])
    with col_a:
        with st.container(border=True):
            st.subheader("สัดส่วน Criteria")
            cc = f["Criteria"].value_counts().reindex(["3.1", "3.2", "3.3", "OOS"]).fillna(0)
            fig = go.Figure(go.Pie(
                labels=[LABEL_TH[c] for c in cc.index], values=cc.values, hole=0.6,
                marker=dict(colors=[COLORS[c] for c in cc.index],
                            line=dict(color="#0C2826", width=2)),
                texttemplate="%{percent:.1%}", textposition="inside",
                insidetextorientation="horizontal", sort=False,
                hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
            ))
            fig.update_layout(
                showlegend=True, height=400,
                legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5),
                margin=dict(t=10, b=10, l=10, r=10),
                annotations=[dict(text=f"<b>{total:,}</b><br>รายการ", x=0.5, y=0.5,
                                  font=dict(size=18, color=INK), showarrow=False)])
            show(fig)
    with col_b:
        with st.container(border=True):
            st.subheader("กลุ่มผลิตภัณฑ์ที่ผ่าน HC")
            g = f.groupby("HC_Group_TH").agg(
                Passed=("Passed", "sum"), Total=("ลำดับ", "count"), OOS=("OutOfScope", "sum")
            ).reset_index()
            # % = สัดส่วนที่ผ่าน เทียบกับจำนวนทั้งหมดในกลุ่มของตัวเอง
            g["Pass_Rate"] = (g["Passed"] / g["Total"].replace(0, 1) * 100).round(1)
            g = g.sort_values("Passed")
            g["label"] = g.apply(
                lambda r: f"{int(r['Passed'])} ({r['Pass_Rate']}%)", axis=1)
            xmax = max(1, int(g["Passed"].max()))
            fig = px.bar(g, x="Passed", y="HC_Group_TH", orientation="h",
                         text="label", color="Passed",
                         color_continuous_scale=["#13403B", TEAL],
                         custom_data=["Total", "Pass_Rate"])
            fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=80),
                              xaxis_title="จำนวนที่ผ่าน HC (3.1)", yaxis_title="",
                              coloraxis_showscale=False,
                              xaxis_range=[0, xmax * 1.25])
            fig.update_traces(
                textposition="outside", textangle=0, cliponaxis=False,
                hovertemplate="%{y}<br>ผ่าน HC: %{x} จากทั้งกลุ่ม %{customdata[0]} "
                              "(%{customdata[1]}%)<extra></extra>")
            show(fig)


def page_groups():
    f = FILTERED
    hero("🍱 วิเคราะห์ตามกลุ่ม HC",
         "เปรียบเทียบกลุ่มอาหารทั้งหมด × ผลการประเมิน 4 เกณฑ์",
         f"📦 {len(f):,} ผลิตภัณฑ์")

    pivot = f.groupby(["HC_Group_TH", "Criteria"]).size().unstack(fill_value=0)
    for c in ["3.1", "3.2", "3.3", "OOS"]:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot = pivot[["3.1", "3.2", "3.3", "OOS"]]
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total")

    with st.container(border=True):
        st.subheader("กลุ่ม HC × Criteria")
        fig = go.Figure()
        for c in ["3.1", "3.2", "3.3", "OOS"]:
            fig.add_trace(go.Bar(
                name=LABEL_TH[c], y=pivot.index, x=pivot[c], orientation="h",
                marker_color=COLORS[c], text=pivot[c].where(pivot[c] > 0, ""),
                textposition="inside", insidetextanchor="middle", textangle=0,
                cliponaxis=False))
        fig.update_layout(barmode="stack", height=max(420, len(pivot) * 36),
                          margin=dict(t=20, b=20, l=20, r=20),
                          xaxis_title="จำนวน", yaxis_title="",
                          uniformtext=dict(mode="show", minsize=11),
                          legend=dict(orientation="h", y=-0.1))
        fig.update_traces(textangle=0)
        show(fig)

    with st.container(border=True):
        st.subheader("ตารางรายละเอียดกลุ่ม HC")
        det = pivot.copy()
        det["Pass Rate (%)"] = (det["3.1"] / det["Total"].replace(0, 1) * 100).round(1)
        det = det.reset_index().rename(columns={
            "HC_Group_TH": "กลุ่ม HC", "3.1": "ผ่าน 3.1", "3.2": "ไม่ผ่าน 3.2",
            "3.3": "ข้อมูลไม่พอ 3.3", "OOS": "OOS", "Total": "รวม"})
        det = det.sort_values("รวม", ascending=False)
        st.dataframe(det, use_container_width=True, hide_index=True)


def page_geo():
    f = FILTERED
    hero("🌏 มุมมองภูมิภาค",
         "การกระจายผลการประเมินตามภูมิภาคและจังหวัด",
         f"📦 {len(f):,} ผลิตภัณฑ์")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.container(border=True):
            st.subheader("ภูมิภาค × Criteria")
            region_pv = f.groupby(["ภูมิภาค", "Criteria"]).size().unstack(fill_value=0)
            for c in ["3.1", "3.2", "3.3", "OOS"]:
                if c not in region_pv.columns:
                    region_pv[c] = 0
            region_pv = region_pv[["3.1", "3.2", "3.3", "OOS"]]
            fig = go.Figure()
            for c in ["3.1", "3.2", "3.3", "OOS"]:
                fig.add_trace(go.Bar(name=LABEL_TH[c], x=region_pv.index, y=region_pv[c],
                                     marker_color=COLORS[c]))
            fig.update_layout(barmode="stack", height=420, margin=dict(t=20, b=20, l=20, r=20),
                              yaxis_title="จำนวน", xaxis_title="",
                              legend=dict(orientation="h", y=-0.18))
            show(fig)
    with col_g2:
        with st.container(border=True):
            st.subheader("Top 10 จังหวัด — Pass Rate (%)")
            ps = f.groupby("จังหวัด").agg(
                Total=("ลำดับ", "count"), Passed=("Passed", "sum"), OOS=("OutOfScope", "sum")
            ).reset_index()
            ps["In_Scope"] = ps["Total"] - ps["OOS"]
            ps["Pass_Rate"] = (ps["Passed"] / ps["Total"].replace(0, 1) * 100).round(1)
            ps = ps[ps["Total"] >= 10].sort_values("Pass_Rate").tail(10)
            if len(ps) > 0:
                fig = px.bar(ps, x="Pass_Rate", y="จังหวัด", orientation="h",
                             text="Pass_Rate", color="Pass_Rate",
                             color_continuous_scale=[COLORS["3.2"], COLORS["3.3"], COLORS["3.1"]],
                             hover_data=["Total", "Passed"])
                fig.update_layout(height=420, margin=dict(t=20, b=20, l=20, r=60),
                                  xaxis_title="% ผ่าน HC", yaxis_title="",
                                  coloraxis_showscale=False,
                                  xaxis_range=[0, max(1, ps["Pass_Rate"].max()) * 1.18])
                fig.update_traces(texttemplate="%{text}%", textposition="outside",
                                  cliponaxis=False)
                show(fig)
            else:
                st.info("จังหวัดที่มี ≥10 ผลิตภัณฑ์ในตัวกรองนี้ไม่เพียงพอ")

    with st.container(border=True):
        st.subheader("Heatmap: ภูมิภาค × กลุ่ม HC (จำนวนผลิตภัณฑ์)")
        heat = f.groupby(["ภูมิภาค", "HC_Group_TH"]).size().unstack(fill_value=0)
        if not heat.empty:
            fig = px.imshow(heat.values, x=heat.columns, y=heat.index,
                            color_continuous_scale=HEAT_GREEN, aspect="auto", text_auto=True)
            fig.update_layout(height=360, margin=dict(t=20, b=20, l=20, r=20))
            show(fig)


def page_zone():
    f = FILTERED
    if "เขตสุขภาพ" not in f.columns:
        st.info("ไม่มีข้อมูลเขตสุขภาพ")
        return
    hero("🏥 วิเคราะห์ตามเขตสุขภาพ",
         "เขตสุขภาพ 1-13 ตามการแบ่งของกระทรวงสาธารณสุข (กทม. = เขต 13)",
         f"📦 {len(f):,} ผลิตภัณฑ์")

    col_z1, col_z2 = st.columns(2)
    with col_z1:
        with st.container(border=True):
            st.subheader("เขตสุขภาพ × Criteria")
            zpv = f.groupby(["เขตสุขภาพ", "Criteria"]).size().unstack(fill_value=0)
            for c in ["3.1", "3.2", "3.3", "OOS"]:
                if c not in zpv.columns:
                    zpv[c] = 0
            zpv = zpv[["3.1", "3.2", "3.3", "OOS"]].sort_index()
            zlabels = [f"เขต {z}" for z in zpv.index]
            fig = go.Figure()
            for c in ["3.1", "3.2", "3.3", "OOS"]:
                fig.add_trace(go.Bar(name=LABEL_TH[c], x=zlabels, y=zpv[c], marker_color=COLORS[c]))
            fig.update_layout(barmode="stack", height=440, margin=dict(t=20, b=20, l=20, r=20),
                              yaxis_title="จำนวน", xaxis_title="",
                              legend=dict(orientation="h", y=-0.18))
            show(fig)
    with col_z2:
        with st.container(border=True):
            st.subheader("Pass Rate (%) แต่ละเขตสุขภาพ")
            zs = f.groupby("เขตสุขภาพ").agg(
                Total=("ลำดับ", "count"), Passed=("Passed", "sum"), OOS=("OutOfScope", "sum")
            ).reset_index()
            zs["In_Scope"] = zs["Total"] - zs["OOS"]
            zs["Pass_Rate"] = (zs["Passed"] / zs["Total"].replace(0, 1) * 100).round(1)
            zs["Zone_Label"] = zs["เขตสุขภาพ"].apply(lambda z: f"เขต {z}")
            zs = zs.sort_values("Pass_Rate")
            fig = px.bar(zs, x="Pass_Rate", y="Zone_Label", orientation="h",
                         text="Pass_Rate", color="Pass_Rate",
                         color_continuous_scale=[COLORS["3.2"], COLORS["3.3"], COLORS["3.1"]],
                         hover_data=["Total", "Passed", "In_Scope"])
            fig.update_layout(height=440, margin=dict(t=20, b=20, l=20, r=60),
                              xaxis_title="% ผ่าน HC (จากทั้งหมด)", yaxis_title="",
                              coloraxis_showscale=False,
                              xaxis_range=[0, max(1, zs["Pass_Rate"].max()) * 1.18])
            fig.update_traces(texttemplate="%{text}%", textposition="outside",
                              cliponaxis=False)
            show(fig)

    with st.container(border=True):
        st.subheader("Heatmap: เขตสุขภาพ × กลุ่ม HC")
        zh = f.groupby(["เขตสุขภาพ", "HC_Group_TH"]).size().unstack(fill_value=0)
        if not zh.empty:
            zh.index = [f"เขต {z}" for z in zh.index]
            fig = px.imshow(zh.values, x=zh.columns, y=zh.index,
                            color_continuous_scale=HEAT_GREEN, aspect="auto", text_auto=True)
            fig.update_layout(height=420, margin=dict(t=20, b=20, l=20, r=20))
            show(fig)

    with st.container(border=True):
        st.subheader("ตารางสรุปเขตสุขภาพ")
        zd = f.groupby("เขตสุขภาพ").agg(
            Total=("ลำดับ", "count"), Passed=("Passed", "sum"), Failed=("Failed", "sum"),
            Insufficient=("Insufficient", "sum"), OOS=("OutOfScope", "sum")).reset_index()
        zd["In_Scope"] = zd["Total"] - zd["OOS"]
        zd["Pass_Rate (%)"] = (zd["Passed"] / zd["Total"].replace(0, 1) * 100).round(1)
        zd = zd.rename(columns={
            "เขตสุขภาพ": "เขต", "Total": "รวม", "Passed": "ผ่าน 3.1", "Failed": "ไม่ผ่าน 3.2",
            "Insufficient": "ข้อมูลไม่พอ 3.3", "OOS": "OOS", "In_Scope": "ในขอบเขต"})
        st.dataframe(zd, use_container_width=True, hide_index=True)


def _nutri_category(n):
    n = str(n).lower()
    if "sugar" in n: return "น้ำตาล"
    if "sodium" in n: return "โซเดียม"
    if "satfat" in n: return "ไขมันอิ่มตัว"
    if "fat" in n: return "ไขมัน"
    if "energy" in n: return "พลังงาน"
    return "อื่นๆ"


def _failed_nutrient_bases(s):
    """แยกชนิดสารอาหารที่ "ตก" ออกจากคอลัมน์ Failed_Nutrients
    เช่น 'sugar>20;sodium>500' -> {'sugar','sodium'}"""
    bases = set()
    for tok in str(s).split(";"):
        t = tok.strip().lower()
        if not t:
            continue
        if t.startswith("satfat"):
            bases.add("satfat")
        elif t.startswith("sodium"):
            bases.add("sodium")
        elif t.startswith("sugar"):
            bases.add("sugar")
        elif t.startswith("energy"):
            bases.add("energy")
        elif t.startswith("fat"):
            bases.add("fat")
    return bases


def _wrap_label(s, width=18):
    """ตัดคำขึ้นบรรทัดใหม่ด้วย <br> ที่ตำแหน่งที่เหมาะสมเท่านั้น —
    ตัดได้ที่เว้นวรรคและหลังเครื่องหมาย '/' (ไม่ตัดกลางคำแปลกๆ)"""
    s = str(s)
    # แตกเป็น token ที่ตัดบรรทัดระหว่างกันได้: หลัง '/' และที่เว้นวรรค
    tokens, buf = [], ""
    for ch in s:
        buf += ch
        if ch == "/":
            tokens.append(buf)
            buf = ""
        elif ch == " ":
            if buf.strip():
                tokens.append(buf.rstrip(" "))
            tokens.append(" ")
            buf = ""
    if buf:
        tokens.append(buf)
    # จัดเรียงเป็นบรรทัดแบบ greedy (ไม่ตัดกลาง token)
    lines, line = [], ""
    for tok in tokens:
        if tok == " ":
            if line and not line.endswith(" "):
                line += " "
            continue
        if line.strip() and len(line) + len(tok) > width:
            lines.append(line.rstrip())
            line = tok
        else:
            line += tok
    if line.strip():
        lines.append(line.rstrip())
    return "<br>".join(lines)


def _merge_per100(tok):
    """รวมฐาน per-100g (token เปล่า) และ per-100ml ให้เป็น '/100' เดียวกัน
    ฐานอื่น (/serving, /pack, /50g, satfat/fat) คงเดิม"""
    t = str(tok).strip()
    for suf in ("/100ml", "/100g"):
        if t.endswith(suf):
            return t[: -len(suf)] + "/100"
    if "/" not in t:           # token เปล่า = ต่อ 100 กรัม
        return t + "/100"
    return t


def page_nutrients():
    f = FILTERED
    fail_df = FAILDF
    hero("🧪 วิเคราะห์สารอาหาร",
         "สารอาหารที่ทำให้ตก HC และการกระจายค่าสารอาหารแยกตามกลุ่มประเภทอาหาร",
         f"📦 {len(f):,} ผลิตภัณฑ์")

    with st.expander("ℹ️ คำอธิบายสารอาหารหลัก (Sugar · Satfat · Sodium · Fat)", expanded=False):
        st.markdown(
            "- **Sugar (น้ำตาล)** — คาร์โบไฮเดรตเชิงเดี่ยวที่ให้รสหวานและพลังงาน "
            "หากบริโภคมากเกินไปเสี่ยงต่อภาวะน้ำหนักเกิน ฟันผุ และเบาหวานชนิดที่ 2 "
            "เกณฑ์ HC จึงจำกัดปริมาณน้ำตาลต่อ 100 ก./มล.\n"
            "- **Sodium (โซเดียม)** — แร่ธาตุหลักในเกลือแกง ช่วยควบคุมสมดุลน้ำในร่างกาย "
            "แต่หากได้รับมากเกินไปเพิ่มความเสี่ยงความดันโลหิตสูง โรคไต และโรคหัวใจ\n"
            "- **Fat (ไขมัน / ไขมันทั้งหมด)** — สารอาหารที่ให้พลังงานสูง (~9 kcal/g) "
            "จำเป็นต่อร่างกาย แต่หากได้รับมากเกินไปทำให้ได้พลังงานเกินและเสี่ยงภาวะอ้วน\n"
            "- **Satfat (ไขมันอิ่มตัว / Saturated fat)** — ไขมันที่พบมากในผลิตภัณฑ์จากสัตว์ "
            "น้ำมันปาล์มและมะพร้าว การบริโภคมากเพิ่มคอเลสเตอรอลชนิดไม่ดี (LDL) "
            "และเสี่ยงต่อโรคหัวใจและหลอดเลือด"
        )

    # join ด้วย key ผสม (ปี, ลำดับ) — ลำดับซ้ำกันข้ามปีได้ ห้ามใช้ ลำดับ เดี่ยวๆ
    f32 = f[f["Criteria"] == "3.2"]
    selected_keys = set(zip(f32["ปี"], f32["ลำดับ"]))
    if selected_keys:
        fail_keys = pd.Series(list(zip(fail_df["ปี"], fail_df["ลำดับ"])), index=fail_df.index)
        ff = fail_df[fail_keys.isin(selected_keys)]
    else:
        ff = fail_df.iloc[0:0]

    col_f1, col_f2 = st.columns([3, 2])
    with col_f1:
        with st.container(border=True):
            st.subheader("Top สารอาหารที่ทำให้ตก")
            if len(ff) > 0:
                merged = ff["Failed_Nutrient"].astype(str).map(_merge_per100)
                top = merged.value_counts().head(15).reset_index()
                top.columns = ["สารอาหาร", "จำนวน"]
                top = top.sort_values("จำนวน")
                fig = px.bar(top, x="จำนวน", y="สารอาหาร", orientation="h", text="จำนวน",
                             color="จำนวน", color_continuous_scale=["#3A1A1C", COLORS["3.2"]])
                fig.update_layout(height=480, margin=dict(t=20, b=20, l=20, r=60),
                                  xaxis_title="จำนวนผลิตภัณฑ์ที่ตก", yaxis_title="",
                                  coloraxis_showscale=False,
                                  xaxis_range=[0, max(1, int(top["จำนวน"].max())) * 1.15])
                fig.update_traces(textposition="outside", cliponaxis=False)
                show(fig)
            else:
                st.info("ไม่มีผลิตภัณฑ์ที่ตก (3.2) ในตัวกรองนี้")
    with col_f2:
        with st.container(border=True):
            st.subheader("สัดส่วนการตกของสารหลัก")
            if len(ff) > 0:
                fc = ff.copy()
                fc["หมวด"] = fc["Failed_Nutrient"].map(_nutri_category)
                cat = fc["หมวด"].value_counts()
                fig = go.Figure(go.Pie(labels=cat.index, values=cat.values, hole=0.5,
                                       textinfo="label+percent",
                                       marker=dict(line=dict(color="#0C2826", width=2))))
                fig.update_layout(height=480, showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                show(fig)
            else:
                st.info("—")

    # ── การกระจายสารอาหาร แยกตามกลุ่มประเภทอาหารย่อย ──
    with st.container(border=True):
        st.subheader("การกระจายค่าสารอาหาร แยกตามกลุ่มประเภทอาหารย่อย")
        nutri_cols = [c for c in ["น้ำตาล/100", "โซเดียม/100", "ไขมัน/100",
                                  "ไขมันอิ่มตัว/100", "พลังงาน/100"] if c in f.columns]
        cc1, cc2 = st.columns([1, 1.3])
        with cc1:
            sel_n = st.selectbox("เลือกสารอาหาร", nutri_cols, key="nutri_box")
        with cc2:
            view_mode = st.segmented_control(
                "มุมมอง", ["ทั้งหมด", "🟢 เฉพาะผ่าน", "🔴 เฉพาะไม่ผ่าน"],
                default="ทั้งหมด", key="nutri_view")

        # แสดงเฉพาะกลุ่มย่อยที่ต้องพิจารณาสารอาหารนี้ตามเกณฑ์ HC
        col_to_nutr = {"น้ำตาล/100": "sugar", "โซเดียม/100": "sodium",
                       "ไขมัน/100": "fat", "ไขมันอิ่มตัว/100": "satfat",
                       "พลังงาน/100": "energy"}
        nutr_th = {"sugar": "น้ำตาล", "sodium": "โซเดียม", "fat": "ไขมัน",
                   "satfat": "ไขมันอิ่มตัว", "energy": "พลังงาน"}
        nmap = load_criteria_nutrient_map_sub(DATA_FILE.stat().st_mtime)
        target = col_to_nutr.get(sel_n)
        th = nutr_th.get(target, sel_n)
        relevant = {u for u, s in nmap.items() if target in s} if (target and nmap) else set()

        pf = f.copy()
        # หน่วย = กลุ่มย่อย ถ้ามี ไม่งั้นใช้กลุ่มใหญ่ (กลุ่มที่ไม่มีกลุ่มย่อย)
        sub = pf["HC_Subgroup_TH"]
        has_sub = sub.notna() & (sub.astype(str).str.strip() != "") & (sub.astype(str) != "nan")
        pf["_unit"] = sub.where(has_sub, pf["HC_Group_TH"])
        if relevant:
            pf = pf[pf["_unit"].isin(relevant)]
        if len(pf) > 0 and sel_n:
            pf["_val"] = pd.to_numeric(pf[sel_n], errors="coerce")
            pf = pf.dropna(subset=["_val"])
        # ตัดสินค้าที่ "ไม่ได้ถูกประเมินกับเกณฑ์" ออก (เช่น เครื่องดื่มชนิดผง/อาหารมื้อหลัก)
        # มิฉะนั้นค่าผงเข้มข้นจะถูกนับเป็น "ผ่าน" ผิด เพราะไม่อยู่ใน Failed_Nutrients
        if len(pf) > 0:
            _note = pf["Note"].astype(str).str.lower()
            _miss = pf["Missing_Nutrients"].astype(str).str.lower()
            _skip = (_note.str.contains("powder") | _note.str.contains("force")
                     | _note.str.contains("out of scope") | _note.str.contains("meal")
                     | _miss.str.contains("powder_form") | _miss.str.contains("group_force_3_3")
                     | _miss.str.contains("calcium") | _miss.str.contains("iron"))
            pf = pf[~_skip]
        if relevant:
            st.caption(f"แสดงเฉพาะกลุ่มย่อยที่มีเกณฑ์ **{th}** ตามเกณฑ์ HC "
                       f"({pf['_unit'].nunique()} กลุ่มย่อย) · สี = ผลเฉพาะ{th} "
                       f"(🟢 ผ่าน / 🔴 ไม่ผ่าน) · ไม่รวมสินค้าที่ประเมินไม่ได้ (เช่น ชนิดผง)")
        if len(pf) > 0 and sel_n and target:
            # ผ่าน/ไม่ผ่าน "เฉพาะสารที่เลือก" (อ่านจาก Failed_Nutrients ของแต่ละสินค้า)
            pf["_nfail"] = pf["Failed_Nutrients"].map(
                lambda s: target in _failed_nutrient_bases(s))
            lbl_pass, lbl_fail = f"ผ่านเกณฑ์ {th}", f"ไม่ผ่านเกณฑ์ {th}"
            pf["ผลสาร"] = pf["_nfail"].map({False: lbl_pass, True: lbl_fail})
            cmap = {lbl_pass: COLORS["3.1"], lbl_fail: COLORS["3.2"]}
            # มุมมองที่เลือก: ทั้งหมด / เฉพาะผ่าน / เฉพาะไม่ผ่าน
            if view_mode == "🟢 เฉพาะผ่าน":
                pf = pf[~pf["_nfail"]]
            elif view_mode == "🔴 เฉพาะไม่ผ่าน":
                pf = pf[pf["_nfail"]]
            if len(pf) == 0:
                st.info("ไม่มีผลิตภัณฑ์ตามมุมมองที่เลือก")
            else:
                # เรียงค่ามัธยฐานมาก→น้อย (แนวตั้ง: มากอยู่ซ้าย) + ตัดคำชื่อยาว
                order_units = (pf.groupby("_unit")["_val"].median()
                               .sort_values(ascending=False).index.tolist())
                wrap_map = {u: _wrap_label(u, 13) for u in order_units}
                pf["_xlab"] = pf["_unit"].map(wrap_map)
                order_labels = [wrap_map[u] for u in order_units]
                n = len(order_units)
                fig = px.box(pf, x="_xlab", y="_val", color="ผลสาร",
                             color_discrete_map=cmap, points="outliers",
                             category_orders={"_xlab": order_labels,
                                              "ผลสาร": [lbl_pass, lbl_fail]})
                # กว้างคงที่ตามจำนวนกลุ่มย่อย (เว้นช่องให้ป้ายไม่ชนกัน) → เลื่อนซ้าย-ขวาได้
                chart_w = max(820, n * 190)
                fig.update_layout(margin=dict(t=50, b=160, l=20, r=20),
                                  xaxis_title="", yaxis_title=sel_n,
                                  boxgap=0.25, boxgroupgap=0.2,
                                  legend=dict(orientation="h", y=1.06, x=0, title=""))
                fig.update_xaxes(tickangle=0, tickfont=dict(size=11))
                show_scrollable(fig, width=chart_w, height=620)
                st.caption(f"กล่อง = การกระจายของ {sel_n} ในแต่ละกลุ่มย่อย "
                           f"แยกสีตามผล**เฉพาะ{th}** · เลื่อนกราฟซ้าย-ขวาเพื่อดูเพิ่ม "
                           f"(เรียงค่ามัธยฐานมาก→น้อย)")
        else:
            st.info("ไม่มีข้อมูลในตัวกรองนี้")


def page_products():
    f = FILTERED
    hero("📋 ตารางรายละเอียดผลิตภัณฑ์",
         "ค้นหา กรอง และดาวน์โหลดข้อมูลผลิตภัณฑ์",
         f"📦 {len(f):,} ผลิตภัณฑ์")

    with st.container(border=True):
        search = st.text_input("🔎 ค้นหาในผลิตภัณฑ์ / ประเภท / จังหวัด",
                               placeholder="พิมพ์คำค้นหา...")
        cols_show = [
            "ปี", "ลำดับ", "ผลิตภัณฑ์", "ประเภท (อย.)", "จังหวัด", "ภูมิภาค", "เขตสุขภาพ",
            "HC_Group_TH", "HC_Subgroup_TH", "Criteria",
            "พลังงาน/100", "น้ำตาล/100", "โซเดียม/100", "ไขมัน/100", "ไขมันอิ่มตัว/100",
            "Failed_Nutrients", "Missing_Nutrients"]
        cols_show = [c for c in cols_show if c in f.columns]
        view = f[cols_show].copy()
        if search:
            s = search.lower()
            mask = (
                view["ผลิตภัณฑ์"].astype(str).str.lower().str.contains(s, na=False) |
                view["ประเภท (อย.)"].astype(str).str.lower().str.contains(s, na=False) |
                view["จังหวัด"].astype(str).str.lower().str.contains(s, na=False))
            view = view[mask]
        st.caption(f"แสดง {len(view):,} จาก {len(f):,} รายการ")
        st.dataframe(view, use_container_width=True, hide_index=True, height=460)
        csv = view.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 ดาวน์โหลด CSV", csv,
                           file_name=f"hc_filtered_{len(view)}_items.csv", mime="text/csv")


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
inject_css()

try:
    DATA, FAILDF = load_data(DATA_FILE.stat().st_mtime)
except FileNotFoundError:
    st.error(f"ไม่พบไฟล์ข้อมูล: {DATA_FILE.name}")
    st.stop()

FILTERED, SELECTED_YEAR, YEAR_TOTAL = build_sidebar_filters(DATA)

nav = st.navigation([
    st.Page(page_overview, title="ภาพรวม", icon=":material/dashboard:", default=True),
    st.Page(page_groups, title="กลุ่ม HC", icon=":material/category:"),
    st.Page(page_geo, title="ภูมิภาค", icon=":material/public:"),
    st.Page(page_zone, title="เขตสุขภาพ", icon=":material/local_hospital:"),
    st.Page(page_nutrients, title="สารอาหาร", icon=":material/science:"),
    st.Page(page_products, title="ผลิตภัณฑ์", icon=":material/table_chart:"),
])
nav.run()

st.caption("© Healthier Choice Evaluation Pipeline — Streamlit + Plotly · ข้อมูล anonymized")
