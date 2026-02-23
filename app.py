"""
NSE Fundamental Stock Scanner — Screener.in style
===================================================
Columns: CMP, P/E, Market Cap, Div Yield, EPS,
         Qtr Profit Var%, Sales Qtr, Qtr Sales Var%, ROE%, 52w High

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSE Stock Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f5f6fa;
    --white:    #ffffff;
    --border:   #dde1ea;
    --accent:   #0052cc;
    --accent2:  #0747a6;
    --green:    #006644;
    --green-bg: #e3fcef;
    --red:      #bf2600;
    --red-bg:   #ffebe6;
    --text:     #172b4d;
    --muted:    #6b778c;
    --hover:    #f4f5f7;
    --head-bg:  #f8f9fb;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.main .block-container { padding: 1rem 2rem 2rem; max-width: 1700px; }

/* Header */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 0 1rem; border-bottom: 2px solid var(--border); margin-bottom: 1rem;
}
.app-header .brand { font-size: 1.4rem; font-weight: 600; color: var(--text); letter-spacing: -0.02em; }
.app-header .brand span { color: var(--accent); }
.app-header .meta { font-size: 0.72rem; color: var(--muted); }
.breadcrumb { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }
.breadcrumb b { color: var(--accent); }

/* Pills */
.pill-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
.pill {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.2rem 0.7rem;
    font-size: 0.7rem; color: var(--muted);
}
.pill strong { color: var(--text); }
.pill.green { background: var(--green-bg); border-color: #abe2c7; color: var(--green); }
.pill.red   { background: var(--red-bg);   border-color: #ffbdad; color: var(--red); }
.pill.blue  { background: #deebff; border-color: #b3d4ff; color: var(--accent2); }

/* Result bar */
.result-bar {
    font-size: 0.8rem; color: var(--muted); padding: 0.4rem 0 0.6rem;
    border-bottom: 1px solid var(--border); margin-bottom: 0.75rem;
}
.result-bar strong { color: var(--text); }

/* Table */
.screen-table {
    width: 100%; border-collapse: collapse; font-size: 0.78rem;
    background: var(--white); border: 1px solid var(--border);
    border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.screen-table thead tr { background: var(--head-bg); border-bottom: 2px solid var(--border); }
.screen-table th {
    padding: 0.55rem 0.8rem; text-align: right;
    font-size: 0.68rem; font-weight: 600; color: var(--muted);
    white-space: nowrap; border-right: 1px solid var(--border);
}
.screen-table th:last-child { border-right: none; }
.screen-table th:nth-child(1),
.screen-table th:nth-child(2) { text-align: left; }
.screen-table tbody tr { border-bottom: 1px solid var(--border); }
.screen-table tbody tr:last-child { border-bottom: none; }
.screen-table tbody tr:hover { background: var(--hover); }
.screen-table td {
    padding: 0.5rem 0.8rem; text-align: right;
    white-space: nowrap; font-family: 'DM Mono', monospace;
    font-size: 0.76rem; border-right: 1px solid #f0f1f4;
}
.screen-table td:last-child { border-right: none; }
.screen-table td:nth-child(1) {
    text-align: left; font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem; color: var(--muted); font-weight: 500; width: 40px;
}
.screen-table td:nth-child(2) { text-align: left; font-family: 'DM Sans', sans-serif; }
.screen-table td:nth-child(2) .sym-name { color: var(--accent); font-weight: 500; font-size: 0.8rem; cursor: pointer; }
.screen-table td:nth-child(2) .sym-name:hover { text-decoration: underline; }
.screen-table td:nth-child(2) .sym-sub { font-size: 0.67rem; color: var(--muted); margin-top: 1px; }

.gv { color: var(--green) !important; font-weight: 500; }
.rv { color: var(--red)   !important; font-weight: 500; }
.na { color: #bbb; font-style: italic; font-size: 0.72rem; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--white) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: var(--bg) !important; border-color: var(--border) !important; font-size: 0.8rem !important;
}
.ss { font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--muted) !important; margin: 0.9rem 0 0.3rem; padding-bottom: 0.3rem; border-bottom: 1px solid var(--border); }

.stButton > button {
    background: var(--white) !important; border: 1px solid var(--border) !important;
    color: var(--accent) !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important; border-radius: 4px !important;
}
.stButton > button:hover { border-color: var(--accent) !important; background: #deebff !important; }
[data-testid="stDownloadButton"] > button {
    background: var(--accent) !important; color: white !important;
    border: none !important; font-size: 0.75rem !important; border-radius: 4px !important;
}

#MainMenu, footer, header { visibility: hidden; }
.live-dot {
    display: inline-block; width: 7px; height: 7px; background: #36b37e;
    border-radius: 50%; margin-right: 4px; animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
</style>
""", unsafe_allow_html=True)

# ── STOCK UNIVERSE ────────────────────────────────────────────────────────────
NSE_STOCKS = {
    "RELIANCE": ("Reliance Industries", "Energy"),
    "TCS": ("Tata Consultancy Services", "IT"),
    "HDFCBANK": ("HDFC Bank", "Banking"),
    "INFY": ("Infosys", "IT"),
    "ICICIBANK": ("ICICI Bank", "Banking"),
    "HINDUNILVR": ("Hindustan Unilever", "FMCG"),
    "ITC": ("ITC", "FMCG"),
    "SBIN": ("State Bank of India", "Banking"),
    "BHARTIARTL": ("Bharti Airtel", "Telecom"),
    "KOTAKBANK": ("Kotak Mahindra Bank", "Banking"),
    "LT": ("Larsen & Toubro", "Infra"),
    "AXISBANK": ("Axis Bank", "Banking"),
    "ASIANPAINT": ("Asian Paints", "Chemicals"),
    "MARUTI": ("Maruti Suzuki", "Auto"),
    "SUNPHARMA": ("Sun Pharmaceutical", "Pharma"),
    "WIPRO": ("Wipro", "IT"),
    "ULTRACEMCO": ("UltraTech Cement", "Cement"),
    "BAJFINANCE": ("Bajaj Finance", "NBFC"),
    "TITAN": ("Titan Company", "Consumer"),
    "NESTLEIND": ("Nestle India", "FMCG"),
    "POWERGRID": ("Power Grid Corp", "Utilities"),
    "NTPC": ("NTPC", "Utilities"),
    "HCLTECH": ("HCL Technologies", "IT"),
    "TECHM": ("Tech Mahindra", "IT"),
    "DRREDDY": ("Dr. Reddy's Labs", "Pharma"),
    "CIPLA": ("Cipla", "Pharma"),
    "ONGC": ("ONGC", "Energy"),
    "COALINDIA": ("Coal India", "Mining"),
    "BPCL": ("BPCL", "Energy"),
    "IOC": ("Indian Oil Corp", "Energy"),
    "HEROMOTOCO": ("Hero MotoCorp", "Auto"),
    "EICHERMOT": ("Eicher Motors", "Auto"),
    "BAJAJFINSV": ("Bajaj Finserv", "NBFC"),
    "JSWSTEEL": ("JSW Steel", "Steel"),
    "TATAMOTORS": ("Tata Motors", "Auto"),
    "TATASTEEL": ("Tata Steel", "Steel"),
    "TATACONSUM": ("Tata Consumer Products", "FMCG"),
    "M&M": ("Mahindra & Mahindra", "Auto"),
    "HINDALCO": ("Hindalco Industries", "Metals"),
    "GRASIM": ("Grasim Industries", "Diversified"),
    "SBILIFE": ("SBI Life Insurance", "Insurance"),
    "HDFCLIFE": ("HDFC Life Insurance", "Insurance"),
    "BRITANNIA": ("Britannia Industries", "FMCG"),
    "APOLLOHOSP": ("Apollo Hospitals", "Healthcare"),
    "ADANIENT": ("Adani Enterprises", "Diversified"),
    "ADANIPORTS": ("Adani Ports", "Infra"),
    "DIVISLAB": ("Divi's Laboratories", "Pharma"),
    "BAJAJ-AUTO": ("Bajaj Auto", "Auto"),
    "UPL": ("UPL", "Chemicals"),
    "LTIM": ("LTIMindtree", "IT"),
}

# ── DATA FETCH ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_all(symbols):
    rows = []
    for sym in symbols:
        name, sector = NSE_STOCKS[sym]
        try:
            tk   = yf.Ticker(f"{sym}.NS")
            info = tk.info

            cmp  = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            prev = info.get("previousClose") or cmp
            chg  = round((cmp - prev) / prev * 100, 2) if prev else 0

            pe      = info.get("trailingPE") or info.get("forwardPE")
            mcap    = info.get("marketCap")
            mcap_cr = round(mcap / 1e7, 2) if mcap else None
            div_yld = info.get("dividendYield")
            div_yld = round(div_yld * 100, 2) if div_yld else 0.0
            eps     = info.get("trailingEps")
            profit_var = info.get("earningsGrowth")
            profit_var = round(profit_var * 100, 2) if profit_var else None
            rev        = info.get("totalRevenue")
            sales_qtr  = round(rev / 4 / 1e7, 2) if rev else None
            rev_growth = info.get("revenueGrowth")
            rev_growth = round(rev_growth * 100, 2) if rev_growth else None
            roe        = info.get("returnOnEquity")
            roe        = round(roe * 100, 2) if roe else None
            high52     = info.get("fiftyTwoWeekHigh")
            high52     = round(high52, 2) if high52 else None

            rows.append({
                "Symbol":         sym,
                "Name":           name,
                "Sector":         sector,
                "CMP":            round(cmp, 2),
                "Chg%":           chg,
                "P/E":            round(pe, 2) if pe else None,
                "Mar Cap (Cr)":   mcap_cr,
                "Div Yld%":       div_yld,
                "EPS (₹)":        round(eps, 2) if eps else None,
                "Profit Var%":    profit_var,
                "Sales Qtr (Cr)": sales_qtr,
                "Sales Var%":     rev_growth,
                "ROE%":           roe,
                "52w High":       high52,
            })
        except Exception:
            continue
    return pd.DataFrame(rows)

# ── FORMAT HELPERS ────────────────────────────────────────────────────────────
def f(v, pre="", suf="", dec=2):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return '<span class="na">—</span>'
    return f"{pre}{v:,.{dec}f}{suf}"

def fp(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return '<span class="na">—</span>'
    c = "gv" if v > 0 else ("rv" if v < 0 else "")
    s = "+" if v > 0 else ""
    return f'<span class="{c}">{s}{v:.2f}%</span>'

def fc(cmp, chg):
    c = "gv" if chg > 0 else ("rv" if chg < 0 else "")
    s = "+" if chg > 0 else ""
    return f'₹{cmp:,.2f}&nbsp;<span class="{c}" style="font-size:0.68rem">({s}{chg:.2f}%)</span>'

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 NSE Screener")
    st.markdown('<div class="ss">🔍 Search</div>', unsafe_allow_html=True)
    search = st.text_input("Company / Symbol", placeholder="e.g. HDFC, Infosys…")

    st.markdown('<div class="ss">🏭 Sector</div>', unsafe_allow_html=True)
    all_sec = ["All"] + sorted({v[1] for v in NSE_STOCKS.values()})
    sector  = st.selectbox("Sector", all_sec)

    st.markdown('<div class="ss">📈 Market</div>', unsafe_allow_html=True)
    mkt = st.selectbox("Show", [
        "All Stocks", "Gainers Only (>0%)", "Losers Only (<0%)",
        "Strong Gainers (>2%)", "Strong Losers (<-2%)"
    ])

    st.markdown('<div class="ss">🔃 Sort</div>', unsafe_allow_html=True)
    sort_by  = st.selectbox("Sort by", ["Mar Cap (Cr)", "CMP", "Chg%", "P/E", "Div Yld%", "ROE%", "52w High", "Profit Var%", "Sales Var%"])
    sort_asc = st.radio("Order", ["Descending ↓", "Ascending ↑"], horizontal=True) == "Ascending ↑"

    st.markdown('<div class="ss">⚙️ Filters</div>', unsafe_allow_html=True)
    pe_max  = st.slider("Max P/E",        0,   200, 200)
    roe_min = st.slider("Min ROE %",      0,   100,   0)
    div_min = st.slider("Min Div Yld %", 0.0, 10.0, 0.0, 0.1)

    st.markdown('<div class="ss">🔄 Auto-Refresh</div>', unsafe_allow_html=True)
    auto_ref      = st.toggle("Refresh every 2 min", True)
    rows_per_page = st.selectbox("Rows/page", [25, 50, 100])
    if st.button("⟳ Refresh Now"):
        st.cache_data.clear()
        st.rerun()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <div class="brand">NSE <span>Screener</span></div>
        <div class="breadcrumb">Screens › <b>Nifty 50 — Fundamental Scanner</b></div>
    </div>
    <div class="meta"><span class="live-dot"></span>Live · Yahoo Finance</div>
</div>
""", unsafe_allow_html=True)

# ── LOAD ─────────────────────────────────────────────────────────────────────
with st.spinner("Fetching live fundamental data…"):
    df = fetch_all(list(NSE_STOCKS.keys()))

if df.empty:
    st.error("Could not load data. Check your internet connection.")
    st.stop()

last_upd = datetime.now().strftime("%d %b %Y, %H:%M:%S")

# ── FILTER ───────────────────────────────────────────────────────────────────
fdf = df.copy()
if search:
    q   = search.upper()
    fdf = fdf[fdf["Symbol"].str.contains(q, na=False) | fdf["Name"].str.upper().str.contains(q, na=False)]
if sector != "All":
    fdf = fdf[fdf["Sector"] == sector]
if "Gainers Only" in mkt:
    fdf = fdf[fdf["Chg%"] > 0]
elif "Losers Only" in mkt:
    fdf = fdf[fdf["Chg%"] < 0]
elif "Strong Gainers" in mkt:
    fdf = fdf[fdf["Chg%"] > 2]
elif "Strong Losers" in mkt:
    fdf = fdf[fdf["Chg%"] < -2]
if pe_max  < 200: fdf = fdf[fdf["P/E"].notna() & (fdf["P/E"] <= pe_max)]
if roe_min >   0: fdf = fdf[fdf["ROE%"].notna() & (fdf["ROE%"] >= roe_min)]
if div_min >   0: fdf = fdf[fdf["Div Yld%"] >= div_min]

fdf = fdf.sort_values(sort_by, ascending=sort_asc, na_position="last").reset_index(drop=True)

total   = len(fdf)
gainers = int((fdf["Chg%"] > 0).sum())
losers  = int((fdf["Chg%"] < 0).sum())
avg_pe  = fdf["P/E"].dropna().mean()
avg_roe = fdf["ROE%"].dropna().mean()

# ── SUMMARY BAR ──────────────────────────────────────────────────────────────
page_count = max(1, (total - 1) // rows_per_page + 1)
st.markdown(f"""
<div class="result-bar">
    <strong>{total} results found</strong> · Showing page 1 of {page_count} · Updated: {last_upd}
</div>
<div class="pill-row">
    <div class="pill"><strong>{total}</strong> Total</div>
    <div class="pill green">▲ <strong>{gainers}</strong> Gainers</div>
    <div class="pill red">▼ <strong>{losers}</strong> Losers</div>
    <div class="pill blue">Avg P/E <strong>{avg_pe:.1f}</strong></div>
    <div class="pill blue">Avg ROE <strong>{avg_roe:.1f}%</strong></div>
</div>
""", unsafe_allow_html=True)

# Export buttons
c1, c2, _ = st.columns([1.2, 1, 9])
with c1:
    st.download_button(
        "⬇ Export CSV",
        fdf.to_csv(index=False).encode(),
        f"nse_screen_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
    )
with c2:
    if st.button("⟳ Refresh"):
        st.cache_data.clear(); st.rerun()

# ── PAGINATION ────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = 1
if st.session_state.page > page_count:
    st.session_state.page = 1

start  = (st.session_state.page - 1) * rows_per_page
page_df = fdf.iloc[start : start + rows_per_page]

# ── TABLE ─────────────────────────────────────────────────────────────────────
rows_html = ""
for i, row in page_df.iterrows():
    rows_html += f"""
    <tr>
      <td>{i+1}</td>
      <td>
        <div class="sym-name">{row['Name']}</div>
        <div class="sym-sub">{row['Symbol']} · {row['Sector']}</div>
      </td>
      <td>{fc(row['CMP'], row['Chg%'])}</td>
      <td>{f(row['P/E'])}</td>
      <td>{f(row['Mar Cap (Cr)'])}</td>
      <td>{f(row['Div Yld%'], suf='%')}</td>
      <td>{f(row['EPS (₹)'])}</td>
      <td>{fp(row['Profit Var%'])}</td>
      <td>{f(row['Sales Qtr (Cr)'])}</td>
      <td>{fp(row['Sales Var%'])}</td>
      <td>{f(row['ROE%'], suf='%')}</td>
      <td>{f(row['52w High'], pre='₹')}</td>
    </tr>"""

st.markdown(f"""
<table class="screen-table">
<thead><tr>
  <th>S.No.</th><th>Name</th><th>CMP ₹</th><th>P/E</th>
  <th>Mar Cap ₹Cr.</th><th>Div Yld %</th><th>EPS ₹</th>
  <th>Qtr Profit Var %</th><th>Sales Qtr ₹Cr.</th>
  <th>Qtr Sales Var %</th><th>ROE %</th><th>52w High ₹</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)

# ── PAGE CONTROLS ─────────────────────────────────────────────────────────────
if page_count > 1:
    st.markdown("---")
    cols = st.columns(min(page_count + 2, 13))
    if cols[0].button("◀"):
        if st.session_state.page > 1:
            st.session_state.page -= 1; st.rerun()
    for p in range(1, min(page_count + 1, 12)):
        label = f"**{p}**" if p == st.session_state.page else str(p)
        if cols[p].button(label):
            st.session_state.page = p; st.rerun()
    if cols[min(page_count + 1, 12)].button("▶"):
        if st.session_state.page < page_count:
            st.session_state.page += 1; st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="font-size:0.68rem;color:#aab;text-align:center;
  padding:1rem 0;border-top:1px solid #dde1ea;margin-top:1.5rem">
  NSE Screener · Data via Yahoo Finance (15-min delay) ·
  Not financial advice · For educational use only · {last_upd}
</div>
""", unsafe_allow_html=True)

# ── AUTO REFRESH ──────────────────────────────────────────────────────────────
if auto_ref:
    time.sleep(120)
    st.rerun()
