import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime
import anthropic
from google import genai
from google.genai import types
import warnings
import os
warnings.filterwarnings("ignore")

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockAI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main .block-container { padding: 1rem 2rem; }

/* ── Sidebar white theme ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * {
    color: #334155 !important;
}
[data-testid="stSidebar"] [data-testid="stForm"] {
    border: 1px solid #e2e8f0 !important;
}

/* Hide standard Streamlit header styling & clean up top spacing */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* Custom Navigation */
.nav-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 1.5rem;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 500;
    color: #475569 !important;
    text-decoration: none !important;
    border-left: 3px solid transparent;
    transition: all 0.15s ease;
    border-radius: 0 8px 8px 0;
}
.nav-item:hover {
    background-color: #f1f5f9;
    color: #0b57d0 !important;
}
.nav-item.active {
    background-color: #edf2fa;
    color: #0b57d0 !important;
    font-weight: 600;
    border-left: 3px solid #0b57d0;
}
.nav-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
}
.nav-icon svg {
    stroke: currentColor;
}
.nav-item.active .nav-icon svg {
    stroke: #0b57d0;
}

/* ── Top Index Ticker ── */
.ticker-container {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.ticker-card {
    display: flex;
    flex-direction: column;
    padding: 10px 16px;
    border-radius: 8px;
    min-width: 140px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.ticker-card.positive {
    background-color: #e8f5e9;
    color: #2e7d32 !important;
}
.ticker-card.positive * {
    color: #2e7d32 !important;
}
.ticker-card.negative {
    background-color: #ffebee;
    color: #c62828 !important;
}
.ticker-card.negative * {
    color: #c62828 !important;
}
.ticker-card .label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}
.ticker-card .value {
    font-size: 14px;
    font-weight: 700;
    margin-top: 2px;
}

/* ── Metric cards ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 1.8rem;
}
.metric-card {
    background-color: #fcfcf9;
    border: 1px solid #f2f2ee;
    border-radius: 12px;
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.metric-label {
    font-size: 12px;
    color: #787875;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1.4;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #1c1c1a;
    margin: 8px 0;
    line-height: 1.1;
}
.metric-value.buy {
    color: #15803d;
}
.metric-value.sell {
    color: #b91c1c;
}
.metric-change {
    font-size: 12px;
    font-weight: 500;
    color: #787875;
}
.metric-change.positive {
    color: #16a34a;
}
.metric-change.negative {
    color: #dc2626;
}

/* ── Filters ── */
.filter-section {
    margin-bottom: 1.8rem;
}
.filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}
.filter-label {
    font-size: 15px;
    font-weight: 700;
    color: #1e293b;
    margin-right: 8px;
}
.pill {
    display: inline-flex;
    align-items: center;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    text-decoration: none !important;
    transition: all 0.15s ease;
    border: 1px solid #d1d5db;
}
.pill.active {
    background-color: #0b57d0 !important;
    color: #ffffff !important;
    border-color: #0b57d0 !important;
}
.pill.inactive {
    background-color: #ffffff !important;
    color: #475569 !important;
    border-color: #e2e8f0 !important;
}
.pill.inactive:hover {
    background-color: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
}

/* ── Screener Table ── */
.table-container {
    position: relative;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    text-align: left;
}
.custom-table th {
    background-color: #fafaf8;
    color: #475569;
    font-weight: 600;
    padding: 14px 18px;
    border-bottom: 1px solid #e2e8f0;
}
.custom-table td {
    padding: 14px 18px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
    vertical-align: middle;
}
.custom-table tr:last-child td {
    border-bottom: none;
}
.custom-table tr:hover td {
    background-color: #f8fafc;
}
.symbol-cell {
    color: #0b57d0 !important;
    font-weight: 700;
    text-decoration: none !important;
}
.symbol-cell:hover {
    text-decoration: underline !important;
}
.name-cell {
    font-weight: 500;
    color: #475569;
}
.price-cell {
    font-weight: 600;
    color: #0f172a;
}
.change-cell {
    font-weight: 600;
}
.change-cell.up {
    color: #16a34a;
}
.change-cell.down {
    color: #dc2626;
}
.floating-btn-container {
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
}
.floating-btn {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #64748b;
    transition: all 0.2s;
}
.floating-btn:hover {
    background-color: #f8fafc;
    color: #0f172a;
    transform: translateY(1px);
}

/* ── Section Header ── */
.sec-hdr {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 1.5rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid #f1f5f9;
}

/* ── Signal badges (predictions page etc) ── */
.b-buy  { background:#dcfce7; color:#15803d; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; }
.b-sell { background:#fee2e2; color:#dc2626; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; }
.b-hold { background:#fef9c3; color:#854d0e; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; }

/* ── Pred cards ── */
.rise-card {
    background:#f0fdf4; border:1px solid #bbf7d0;
    border-radius:12px; padding:1.2rem; margin-bottom:0.8rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.fall-card {
    background:#fff5f5; border:1px solid #fecaca;
    border-radius:12px; padding:1.2rem; margin-bottom:0.8rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

/* ── Chat ── */
.msg-user {
    background:#0b57d0; color:#fff; padding:10px 16px;
    border-radius:16px 16px 2px 16px; margin:8px 0;
    max-width:75%; margin-left:auto; font-size:14.5px; line-height:1.5;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.msg-bot {
    background:#f1f5f9; color:#1e293b; padding:10px 16px;
    border-radius:16px 16px 16px 2px; margin:8px 0;
    max-width:82%; font-size:14.5px; line-height:1.6;
    border: 1px solid #e2e8f0;
}

/* ── Rec card ── */
.rec-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:12px;
    padding:1.2rem; margin-bottom:0.8rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    transition: transform 0.15s, border-color 0.15s;
}
.rec-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
INDIA_SYMBOLS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "LT.NS","BAJFINANCE.NS","AXISBANK.NS","MARUTI.NS","SUNPHARMA.NS",
    "TITAN.NS","WIPRO.NS","TATAMOTORS.NS","ONGC.NS","HCLTECH.NS",
    "DIVISLAB.NS","CIPLA.NS","ULTRACEMCO.NS","NESTLEIND.NS","ASIANPAINT.NS",
]
US_SYMBOLS = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA",
    "META","TSLA","JPM","V","JNJ",
    "PG","MA","HD","UNH","BRK-B",
]

# ─── Session state ────────────────────────────────────────────────────────────
if "custom_india" not in st.session_state:
    st.session_state.custom_india = list(INDIA_SYMBOLS)
if "custom_us" not in st.session_state:
    st.session_state.custom_us = list(US_SYMBOLS)
if "market_selection" not in st.session_state:
    st.session_state.market_selection = "India (NSE)"

def add_custom_symbol(ticker_str, market_val="US Markets"):
    clean_ticker = ticker_str.strip().upper()
    if not clean_ticker:
        return False
    
    # Check if it's already in the watchlist
    is_india = clean_ticker.endswith(".NS") or clean_ticker.endswith(".BO")
    
    changed = False
    if is_india:
        full_ticker = clean_ticker if (clean_ticker.endswith(".NS") or clean_ticker.endswith(".BO")) else (clean_ticker + ".NS")
        if full_ticker not in st.session_state.custom_india:
            st.session_state.custom_india.append(full_ticker)
            changed = True
        if market_val == "US Markets" and st.session_state.market_selection != "Both":
            st.session_state.market_selection = "Both"
            changed = True
    else:
        if clean_ticker not in st.session_state.custom_us:
            st.session_state.custom_us.append(clean_ticker)
            changed = True
        if market_val == "India (NSE)" and st.session_state.market_selection != "Both":
            st.session_state.market_selection = "Both"
            changed = True
        
    if changed:
        # Clear caches to force new load
        st.cache_data.clear()
        st.rerun()
    return changed

def search_ticker_by_name(query_str: str) -> list:
    import requests
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query_str}&quotesCount=5&newsCount=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            quotes = r.json().get("quotes", [])
            out = []
            for q in quotes:
                if q.get("quoteType") == "EQUITY":
                    out.append({
                        "symbol": q.get("symbol"),
                        "name": q.get("shortname") or q.get("longname") or q.get("symbol"),
                        "exchange": q.get("exchange")
                    })
            return out
    except Exception:
        pass
    return []

qp = st.query_params
if "page" in qp:
    st.session_state.page = qp["page"]

if "page" not in st.session_state:
    st.session_state.page = "Screener"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content":
         "👋 Hi! I'm your AI stock analyst. Ask me to analyze any stock, predict tomorrow's movement, compare sectors, or suggest picks based on your risk profile."}
    ]
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "RELIANCE.NS": {"qty": 10, "avg_price": 2540},
        "INFY.NS":     {"qty": 20, "avg_price": 1620},
        "TCS.NS":      {"qty":  5, "avg_price": 3800},
        "HDFCBANK.NS": {"qty": 15, "avg_price": 1680},
    }

def clean_html(html_str):
    return "".join(line.strip() for line in html_str.split("\n") if line.strip())

TICKER_NAMES = {
    # India
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "HDFCBANK": "HDFC Bank",
    "INFY": "Infosys",
    "ICICIBANK": "ICICI Bank",
    "HINDUNILVR": "Hindustan Unilever",
    "ITC": "ITC Limited",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel",
    "KOTAKBANK": "Kotak Mahindra Bank",
    "LT": "Larsen & Toubro",
    "BAJFINANCE": "Bajaj Finance",
    "AXISBANK": "Axis Bank",
    "MARUTI": "Maruti Suzuki",
    "SUNPHARMA": "Sun Pharmaceutical",
    "TITAN": "Titan Company",
    "WIPRO": "Wipro Limited",
    "TATAMOTORS": "Tata Motors",
    "ONGC": "Oil & Natural Gas Corp",
    "HCLTECH": "HCL Technologies",
    "DIVISLAB": "Divi's Laboratories",
    "CIPLA": "Cipla Limited",
    "ULTRACEMCO": "UltraTech Cement",
    "NESTLEIND": "Nestlé India",
    "ASIANPAINT": "Asian Paints",
    # US
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com, Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms, Inc.",
    "TSLA": "Tesla, Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "JNJ": "Johnson & Johnson",
    "PG": "Procter & Gamble Co.",
    "MA": "Mastercard Inc.",
    "HD": "Home Depot, Inc.",
    "UNH": "UnitedHealth Group",
    "BRK-B": "Berkshire Hathaway",
}

STATIC_STOCK_INFO = {
    # India (NSE)
    "RELIANCE": {"sector": "Energy", "div": 0.38, "roe": 9.1},
    "TCS": {"sector": "Technology", "div": 1.15, "roe": 45.3},
    "HDFCBANK": {"sector": "Financial Services", "div": 1.10, "roe": 15.2},
    "INFY": {"sector": "Technology", "div": 2.10, "roe": 30.1},
    "ICICIBANK": {"sector": "Financial Services", "div": 0.90, "roe": 16.8},
    "HINDUNILVR": {"sector": "Consumer Defensive", "div": 1.65, "roe": 28.5},
    "ITC": {"sector": "Consumer Defensive", "div": 2.75, "roe": 29.2},
    "SBIN": {"sector": "Financial Services", "div": 1.20, "roe": 17.5},
    "BHARTIARTL": {"sector": "Communication Services", "div": 0.60, "roe": 12.0},
    "KOTAKBANK": {"sector": "Financial Services", "div": 0.85, "roe": 14.1},
    "LT": {"sector": "Industrials", "div": 0.75, "roe": 13.5},
    "BAJFINANCE": {"sector": "Financial Services", "div": 0.50, "roe": 21.0},
    "AXISBANK": {"sector": "Financial Services", "div": 0.40, "roe": 15.0},
    "MARUTI": {"sector": "Consumer Cyclical", "div": 1.10, "roe": 14.8},
    "SUNPHARMA": {"sector": "Healthcare", "div": 0.90, "roe": 15.5},
    "TITAN": {"sector": "Consumer Cyclical", "div": 0.35, "roe": 23.5},
    "WIPRO": {"sector": "Technology", "div": 0.20, "roe": 16.0},
    "TATAMOTORS": {"sector": "Consumer Cyclical", "div": 0.70, "roe": 18.0},
    "ONGC": {"sector": "Energy", "div": 4.50, "roe": 12.8},
    "HCLTECH": {"sector": "Technology", "div": 3.20, "roe": 22.0},
    "DIVISLAB": {"sector": "Healthcare", "div": 0.75, "roe": 11.2},
    "CIPLA": {"sector": "Healthcare", "div": 0.65, "roe": 14.5},
    "ULTRACEMCO": {"sector": "Materials", "div": 0.35, "roe": 11.8},
    "NESTLEIND": {"sector": "Consumer Defensive", "div": 1.25, "roe": 105.0},
    "ASIANPAINT": {"sector": "Consumer Defensive", "div": 1.10, "roe": 27.5},
    # US Markets
    "AAPL": {"sector": "Technology", "div": 0.52, "roe": 150.0},
    "MSFT": {"sector": "Technology", "div": 0.72, "roe": 38.5},
    "GOOGL": {"sector": "Technology", "div": 0.40, "roe": 29.5},
    "AMZN": {"sector": "Consumer Cyclical", "div": 0.00, "roe": 20.2},
    "NVDA": {"sector": "Technology", "div": 0.02, "roe": 115.0},
    "META": {"sector": "Communication Services", "div": 0.45, "roe": 31.0},
    "TSLA": {"sector": "Consumer Cyclical", "div": 0.00, "roe": 10.5},
    "JPM": {"sector": "Financial Services", "div": 2.20, "roe": 16.5},
    "V": {"sector": "Financial Services", "div": 0.75, "roe": 21.5},
    "JNJ": {"sector": "Healthcare", "div": 2.90, "roe": 18.5},
    "PG": {"sector": "Consumer Defensive", "div": 2.40, "roe": 31.5},
    "MA": {"sector": "Financial Services", "div": 0.55, "roe": 52.0},
    "HD": {"sector": "Consumer Cyclical", "div": 2.30, "roe": 105.0},
    "UNH": {"sector": "Healthcare", "div": 1.45, "roe": 25.0},
    "BRK-B": {"sector": "Financial Services", "div": 0.00, "roe": 8.5},
}

def render_pill(label, param_key, param_value, active_condition):
    target_params = dict(st.query_params)
    if active_condition:
        target_params.pop(param_key, None)
    else:
        target_params[param_key] = str(param_value)
    
    from urllib.parse import urlencode
    query_str = urlencode(target_params)
    url = f"/?{query_str}" if query_str else "/"
    cls = "pill active" if active_condition else "pill inactive"
    return f'<a href="{url}" target="_self" class="{cls}">{label}</a>'

def render_custom_table(df_to_render, curr):
    if df_to_render.empty:
        return '<div style="padding: 20px; text-align: center; color: #64748b;">No stocks match your current filters.</div>'
    
    html = """
    <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Price</th>
                    <th>Change</th>
                    <th>Vol</th>
                    <th>PE</th>
                    <th>Mkt Cap</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df_to_render.iterrows():
        sym = row["Symbol"]
        name = row.get("Name") or TICKER_NAMES.get(sym, sym)
        price_val = row["Price"]
        chg_val = row["Chg%"]
        vol_val = row["Volume"]
        pe_val = row["PE"]
        mcap_lbl = row["MktCap_Lbl"]
        
        chg_cls = "up" if chg_val >= 0 else "down"
        arrow = "+" if chg_val >= 0 else ""
        
        if curr == "₹":
            formatted_price = f"₹{price_val:,.0f}"
        else:
            formatted_price = f"${price_val:,.2f}"
            
        formatted_chg = f"{arrow}{chg_val:.1f}%"
        formatted_pe = f"{pe_val:.1f}" if pe_val > 0 else "—"
        
        html += f"""
        <tr>
            <td><a href="?page=Screener&select={sym}" target="_self" class="symbol-cell">{sym}</a></td>
            <td class="name-cell">{name}</td>
            <td class="price-cell">{formatted_price}</td>
            <td class="change-cell {chg_cls}">{formatted_chg}</td>
            <td class="vol-cell">{vol_val}</td>
            <td class="pe-cell">{formatted_pe}</td>
            <td class="mcap-cell" style="color: #4b5563;">{mcap_lbl}</td>
        </tr>
        """
        
    html += """
            </tbody>
        </table>
        <div class="floating-btn-container">
            <div class="floating-btn" onclick="window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M19 12l-7 7-7-7"/>
                </svg>
            </div>
        </div>
    </div>
    """
    return html

def render_portfolio_table(pf, curr):
    if pf.empty:
        return '<div style="padding: 20px; text-align: center; color: #64748b;">No holdings found.</div>'
    html = """
    <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Qty</th>
                    <th>Avg Buy</th>
                    <th>LTP</th>
                    <th>Value</th>
                    <th>Cost</th>
                    <th>P&L</th>
                    <th>P&L%</th>
                </tr>
            </thead>
            <tbody>
    """
    for _, row in pf.iterrows():
        sym = row["Symbol"]
        qty = row["Qty"]
        avg = row["Avg"]
        ltp = row["LTP"]
        val = row["Value"]
        cost = row["Cost"]
        pnl = row["P&L"]
        pnl_pct = row["P&L%"]
        
        pnl_cls = "up" if pnl >= 0 else "down"
        arrow = "+" if pnl >= 0 else ""
        
        formatted_avg = f"{curr}{avg:,.2f}"
        formatted_ltp = f"{curr}{ltp:,.2f}"
        formatted_val = f"{curr}{val:,.0f}"
        formatted_cost = f"{curr}{cost:,.0f}"
        formatted_pnl = f"{curr}{pnl:,.0f}" if pnl >= 0 else f"-{curr}{abs(pnl):,.0f}"
        
        if curr == "₹":
            formatted_avg = f"₹{avg:,.0f}"
            formatted_ltp = f"₹{ltp:,.0f}"
        
        html += f"""
        <tr>
            <td><span class="symbol-cell">{sym}</span></td>
            <td>{qty}</td>
            <td>{formatted_avg}</td>
            <td>{formatted_ltp}</td>
            <td>{formatted_val}</td>
            <td>{formatted_cost}</td>
            <td class="change-cell {pnl_cls}">{formatted_pnl}</td>
            <td class="change-cell {pnl_cls}">{arrow}{pnl_pct:.2f}%</td>
        </tr>
        """
    html += "</tbody></table></div>"
    return html

def fetch_reddit_posts(symbol: str) -> list:
    import requests
    import xml.etree.ElementTree as ET
    import re
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = f"https://www.reddit.com/r/stocks/search.rss?q={symbol}&restrict_sr=1&sort=new&limit=5"
    posts = []
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                title = title_elem.text if title_elem is not None else ""
                
                content_elem = entry.find("atom:content", ns)
                content = content_elem.text if content_elem is not None else ""
                
                text_content = re.sub(r'<[^>]+>', ' ', content)
                text_content = " ".join(text_content.split())[:300]
                
                author_elem = entry.find("atom:author/atom:name", ns)
                author = author_elem.text if author_elem is not None else "u/unknown"
                
                link_elem = entry.find("atom:link", ns)
                link = link_elem.attrib.get("href", "") if link_elem is not None else ""
                
                posts.append({
                    "title": title,
                    "content": text_content,
                    "author": author,
                    "link": link
                })
    except Exception:
        pass
    return posts

def fetch_stock_news(symbol: str) -> list:
    news_list = []
    try:
        sym_full = symbol
        if not sym_full.endswith(".NS") and symbol in TICKER_NAMES:
            for ind_sym in INDIA_SYMBOLS:
                if ind_sym.replace(".NS", "") == symbol:
                    sym_full = ind_sym
                    break
        
        tk = yf.Ticker(sym_full)
        raw_news = tk.news
        if raw_news:
            for item in raw_news[:5]:
                content = item.get("content", {})
                title = content.get("title", "")
                summary = content.get("summary", "")
                publisher = content.get("provider", {}).get("displayName", "Yahoo Finance")
                link = content.get("canonicalUrl", {}).get("url", "")
                
                news_list.append({
                    "title": title,
                    "summary": summary,
                    "publisher": publisher,
                    "link": link
                })
    except Exception:
        pass
    return news_list

@st.cache_data(ttl=600, show_spinner=False)
def analyze_stock_sentiment(symbol: str, news: list, reddit: list, api_key: str) -> dict:
    if not api_key:
        return {
            "sentiment": "NEUTRAL",
            "summary_news": "Enter your OpenAI API key in the sidebar to enable AI sentiment summaries.",
            "summary_reddit": "Enter your OpenAI API key in the sidebar to enable AI sentiment summaries."
        }
    
    news_text = ""
    for i, item in enumerate(news):
        news_text += f"[{i+1}] {item['title']} (Source: {item['publisher']})\nSummary: {item['summary']}\n\n"
    
    reddit_text = ""
    for i, item in enumerate(reddit):
        reddit_text += f"[{i+1}] {item['title']} (Author: {item['author']})\nContent: {item['content']}\n\n"
        
    prompt = f"""You are an expert financial analyst. Analyze the sentiment of the following news articles and Reddit community posts for the stock {symbol}.

NEWS ARTICLES:
{news_text if news_text else "No recent news found."}

REDDIT DISCUSSION POSTS:
{reddit_text if reddit_text else "No recent discussions found."}

Based on this data, provide:
1. A single overall sentiment word: either 'BULLISH', 'BEARISH', or 'NEUTRAL'.
2. A 2-sentence summary of the professional news sentiment.
3. A 2-sentence summary of the retail Reddit public opinion.

Return your response strictly in the following raw format (no markdown code blocks, just plain text):
SENTIMENT: [BULLISH/BEARISH/NEUTRAL]
NEWS SUMMARY: [Your 2-sentence news summary]
REDDIT SUMMARY: [Your 2-sentence reddit summary]"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        import time
        max_retries = 3
        resp = None
        for attempt in range(max_retries):
            try:
                resp = client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.2
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1.5 * (attempt + 1))
                
        if resp is None:
            raise Exception("Empty response from OpenAI")
            
        text = resp.choices[0].message.content
        
        sentiment = "NEUTRAL"
        news_summary = "No news summary generated."
        reddit_summary = "No Reddit summary generated."
        
        for line in text.split("\n"):
            if line.startswith("SENTIMENT:"):
                sentiment = line.split(":", 1)[1].strip().upper()
            elif line.startswith("NEWS SUMMARY:"):
                news_summary = line.split(":", 1)[1].strip()
            elif line.startswith("REDDIT SUMMARY:"):
                reddit_summary = line.split(":", 1)[1].strip()
                
        if sentiment not in ["BULLISH", "BEARISH", "NEUTRAL"]:
            if "BULLISH" in sentiment: sentiment = "BULLISH"
            elif "BEARISH" in sentiment: sentiment = "BEARISH"
            else: sentiment = "NEUTRAL"
            
        return {
            "sentiment": sentiment,
            "summary_news": news_summary,
            "summary_reddit": reddit_summary
        }
    except Exception as e:
        return {
            "sentiment": "NEUTRAL",
            "summary_news": f"Failed to analyze: {e}",
            "summary_reddit": "Failed to analyze."
        }

# ─── Data functions ───────────────────────────────────────────────────────────
POSITIVE_KEYWORDS = {
    "bullish", "buy", "up", "rise", "grow", "growth", "high", "gain", "profit",
    "beat", "outperform", "success", "successful", "positive", "strong", "surpass",
    "boost", "rally", "upgrade", "expansion", "soar", "record", "optimistic",
    "bull", "undervalued", "good", "breakout", "accumulate", "long", "bulls"
}
NEGATIVE_KEYWORDS = {
    "bearish", "sell", "down", "fall", "drop", "sink", "low", "loss", "lose",
    "miss", "underperform", "fail", "failure", "negative", "weak", "decline",
    "slump", "crash", "downgrade", "shrink", "plunge", "plummet", "pessimistic",
    "bear", "overvalued", "bad", "scam", "dump", "short", "debt", "lawsuit", "risk", "bears"
}

def calculate_sentiment_score(news_list: list, reddit_list: list) -> float:
    score = 0.0
    pos_set = POSITIVE_KEYWORDS
    neg_set = NEGATIVE_KEYWORDS
    
    def clean_text(text):
        if not text:
            return ""
        return text.lower()
        
    for item in news_list:
        title = clean_text(item.get("title", ""))
        summary = clean_text(item.get("summary", ""))
        
        # Check title (weight = 2.0)
        for word in title.split():
            w = "".join(c for c in word if c.isalnum())
            if w in pos_set:
                score += 2.0
            elif w in neg_set:
                score -= 2.0
                
        # Check summary (weight = 1.0)
        for word in summary.split():
            w = "".join(c for c in word if c.isalnum())
            if w in pos_set:
                score += 1.0
            elif w in neg_set:
                score -= 1.0
                
    for item in reddit_list:
        title = clean_text(item.get("title", ""))
        content = clean_text(item.get("content", ""))
        
        # Check title (weight = 1.5)
        for word in title.split():
            w = "".join(c for c in word if c.isalnum())
            if w in pos_set:
                score += 1.5
            elif w in neg_set:
                score -= 1.5
                
        # Check content (weight = 0.5)
        for word in content.split():
            w = "".join(c for c in word if c.isalnum())
            if w in pos_set:
                score += 0.5
            elif w in neg_set:
                score -= 0.5
                
    if score > 0:
        return min(score, 15.0)
    elif score < 0:
        return max(score, -10.0)
    return 0.0

def fetch_single_stock_data(sym: str) -> dict:
    try:
        tk   = yf.Ticker(sym)
        info = tk.fast_info          # faster than .info
        hist = tk.history(period="45d", auto_adjust=True)
        if hist.empty or len(hist) < 2:
            return None
        close  = hist["Close"].dropna()
        price  = round(float(close.iloc[-1]), 2)
        prev   = round(float(close.iloc[-2]), 2)
        chg    = round((price - prev) / prev * 100, 2)
        vol    = int(hist["Volume"].iloc[-1])
        vol_s  = f"{vol/1e6:.1f}M" if vol > 1_000_000 else f"{vol/1e3:.0f}K"

        # fundamentals — fast_info has subset; fall back gracefully
        pe      = round(getattr(info, "pe_ratio", None) or 0, 1)
        mktcap  = getattr(info, "market_cap", None) or 0
        beta    = round(getattr(info, "beta3_year", None) or 1.0, 2)
        hi52    = round(getattr(info, "year_high", None) or 0, 1)
        lo52    = round(getattr(info, "year_low",  None) or 0, 1)

        # sector / div need full .info — try with static lookup to prevent rate limiting, fall back to .info for custom symbols
        sym_clean = sym.replace(".NS", "")
        company_name = None
        if sym_clean in STATIC_STOCK_INFO:
            s_info = STATIC_STOCK_INFO[sym_clean]
            sector = s_info["sector"]
            div_y  = s_info["div"]
            roe    = s_info["roe"]
            company_name = TICKER_NAMES.get(sym_clean, sym_clean)
        else:
            try:
                full  = tk.info
                sector = full.get("sector") or "—"
                div_y  = round((full.get("dividendYield") or 0) * 100, 2)
                roe    = round((full.get("returnOnEquity") or 0) * 100, 1)
                company_name = full.get("longName") or full.get("shortName") or sym_clean
            except Exception:
                sector, div_y, roe = "—", 0.0, 0.0
                company_name = sym_clean

        if not company_name:
            company_name = sym_clean

        # RSI (14-day)
        if len(close) < 15:
            rsi_val = 50.0
        else:
            d = close.diff()
            g = d.clip(lower=0).rolling(14).mean()
            l = (-d.clip(upper=0)).rolling(14).mean()
            rs = g / l.replace(0, np.nan)
            val = 100 - 100 / (1 + rs.iloc[-1])
            rsi_val = round(float(val), 1) if not np.isnan(val) else 50.0

        # Fetch news and reddit posts in backend
        news_list = fetch_stock_news(sym_clean)
        reddit_list = fetch_reddit_posts(sym_clean)
        sentiment_score = calculate_sentiment_score(news_list, reddit_list)

        # Signal
        if rsi_val < 40 or (chg > 1.0 and rsi_val < 65):
            signal = "BUY"
        elif rsi_val > 72 or chg < -2.0:
            signal = "SELL"
        else:
            signal = "HOLD"

        # AI Score
        sig_map = {"BUY": 15, "SELL": -10, "HOLD": 0}
        sig_val = sig_map.get(signal, 0)
        
        pe_bonus = 10 if (pe > 0 and pe < 25) else (5 if pe < 35 else -5)
        chg_bonus = 10 if chg > 1.0 else (-5 if chg < -1.5 else 0)
        rsi_bonus = 5 if (rsi_val > 40 and rsi_val < 60) else 0
        
        import random
        noise = random.randint(-4, 4)
        
        ai_score = max(0, min(100, int(50 + sig_val + pe_bonus + chg_bonus + rsi_bonus + noise + sentiment_score)))

        return {
            "Symbol":  sym.replace(".NS", ""),
            "_sym":    sym,
            "Name":    company_name,
            "Price":   price,
            "Chg%":    chg,
            "Volume":  vol_s,
            "PE":      pe,
            "MktCap":  mktcap,
            "52H":     hi52,
            "52L":     lo52,
            "Sector":  sector,
            "Div%":    div_y,
            "Beta":    beta,
            "ROE":     roe,
            "RSI":     rsi_val,
            "Sentiment_Score": sentiment_score,
            "Signal":  signal,
            "AI_Score": ai_score,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(symbols: tuple, cache_key: int = 0) -> pd.DataFrame:
    import concurrent.futures
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_stock_data, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res is not None:
                rows.append(res)
                
    if not rows:
        raise ValueError("Live market feeds are currently unresponsive or rate-limited")

    df = pd.DataFrame(rows)

    # ── MktCap label ──
    def _cap(v):
        if v > 1e12: return f"₹{v/1e12:.1f}T"
        if v > 1e9:  return f"₹{v/1e9:.1f}B"
        if v > 1e6:  return f"₹{v/1e6:.0f}M"
        return "—"
    df["MktCap_Lbl"] = df["MktCap"].apply(_cap)

    return df.reset_index(drop=True)


@st.cache_data(ttl=60, show_spinner=False)
def fetch_ohlcv(symbol: str, period: str = "6mo") -> pd.DataFrame:
    df = yf.Ticker(symbol).history(period=period, auto_adjust=True)
    df.index = pd.to_datetime(df.index)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def fetch_indices(cache_key: int = 0) -> dict:
    MAP = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "NASDAQ": "^IXIC", "S&P 500": "^GSPC"}
    out = {}
    for name, sym in MAP.items():
        try:
            h = yf.Ticker(sym).history(period="2d")["Close"].dropna()
            if len(h) >= 2:
                p, pp = float(h.iloc[-1]), float(h.iloc[-2])
                out[name] = {"price": p, "chg": round((p - pp) / pp * 100, 2)}
        except Exception:
            pass
    return out


def ai_prediction(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    d = df.copy()
    mom      = d["Chg%"].clip(-5, 5) / 5
    rsi_sig  = (50 - d["RSI"]) / 50
    beta_sig = 1 - d["Beta"].clip(0, 3) / 3
    ai_sig   = (d["AI_Score"] - 50) / 50
    
    # Map Sentiment_Score to [-1.0, 1.0]
    sentiment_sig = np.where(d["Sentiment_Score"] >= 0, d["Sentiment_Score"] / 15.0, d["Sentiment_Score"] / 10.0)
    
    # Update confidence formula to use sentiment signal
    d["conf"] = (0.35 * mom + 0.30 * rsi_sig + 0.10 * beta_sig + 0.15 * ai_sig + 0.10 * sentiment_sig) * 100
    
    rise = d[d["conf"] >  10].sort_values("conf", ascending=False).head(8)
    fall = d[d["conf"] < -10].sort_values("conf").head(6)
    return rise, fall


def portfolio_value() -> pd.DataFrame:
    rows = []
    for sym, info in st.session_state.portfolio.items():
        try:
            price = float(yf.Ticker(sym).history(period="1d")["Close"].iloc[-1])
            qty, avg = info["qty"], info["avg_price"]
            val  = round(price * qty, 2)
            cost = round(avg * qty, 2)
            pnl  = round(val - cost, 2)
            rows.append({
                "Symbol": sym.replace(".NS", ""), "_sym": sym,
                "Qty": qty, "Avg": avg, "LTP": round(price, 2),
                "Value": val, "Cost": cost,
                "P&L": pnl, "P&L%": round(pnl / cost * 100, 2),
            })
        except Exception:
            pass
    return pd.DataFrame(rows)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 15px 0; border-bottom: 1px solid #f1f5f9; margin-bottom: 10px;">
        <h2 style="margin: 0; font-size: 22px; font-weight: 700; color: #0f172a;">StockAI</h2>
        <p style="margin: 2px 0 0 0; font-size: 12px; color: #64748b; font-weight: 500;">Continuous intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    pages_nav = [
        {
            "label": "Screener", 
            "key": "Screener", 
            "icon": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>"""
        },
        {
            "label": "AI Predictions", 
            "key": "Predictions", 
            "icon": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 0 0-7.75 16.33L3 21l2.67-1.25A10 10 0 1 0 12 2z"/><path d="M12 6v6h6"/></svg>"""
        },
        {
            "label": "Portfolio", 
            "key": "Portfolio", 
            "icon": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>"""
        },
        {
            "label": "For You", 
            "key": "ForYou", 
            "icon": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>"""
        },
        {
            "label": "AI Chatbot", 
            "key": "Chatbot", 
            "icon": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""
        },
    ]

    active_page = st.session_state.page
    
    nav_html = '<div class="nav-container">'
    for item in pages_nav:
        is_active = active_page == item["key"]
        active_cls = "active" if is_active else ""
        
        target_params = dict(st.query_params)
        target_params["page"] = item["key"]
        
        from urllib.parse import urlencode
        query_str = urlencode(target_params)
        url = f"/?{query_str}"
        
        nav_html += f"""
        <a href="{url}" target="_self" class="nav-item {active_cls}">
            <span class="nav-icon">{item['icon']}</span>
            <span>{item['label']}</span>
        </a>
        """
    nav_html += '</div>'
    
    st.markdown(clean_html(nav_html), unsafe_allow_html=True)
    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

    market = st.selectbox(
        "Market",
        options=["India (NSE)", "US Markets", "Both"],
        key="market_selection",
        label_visibility="visible"
    )
    
    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin: 0; font-size: 14px; font-weight: 700; color: #0f172a;'>🔄 Real-Time Feed</h3>", unsafe_allow_html=True)
    refresh_enabled = st.toggle("Auto-Refresh Data", value=True, help="Periodically updates the stock indices and dashboard data automatically.")
    
    if refresh_enabled:
        interval_choice = st.selectbox(
            "Update Interval",
            options=["10s", "30s", "1m", "5m"],
            index=1,  # Default to 30s
            help="Select how often the dashboard data should refresh."
        )
        interval_map = {"10s": 10, "30s": 30, "1m": 60, "5m": 300}
        refresh_seconds = interval_map[interval_choice]
    else:
        refresh_seconds = None

    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin: 0; font-size: 14px; font-weight: 700; color: #0f172a;'>➕ Add Custom Ticker</h3>", unsafe_allow_html=True)
    custom_ticker = st.text_input("Ticker Symbol", key="custom_ticker_input", placeholder="e.g. AMD or TATAMOTORS.NS", label_visibility="collapsed")
    if st.button("Add Ticker", use_container_width=True):
        if custom_ticker:
            add_custom_symbol(custom_ticker, market)
            
    with st.expander("🗑 Manage Screener Stocks"):
        current_watchlist = st.session_state.custom_india if market == "India (NSE)" else (st.session_state.custom_us if market == "US Markets" else st.session_state.custom_india + st.session_state.custom_us)
        to_remove = st.selectbox("Select symbol to remove", [""] + current_watchlist)
        if st.button("Remove Selected Ticker", use_container_width=True):
            if to_remove:
                if to_remove in st.session_state.custom_india:
                    st.session_state.custom_india.remove(to_remove)
                if to_remove in st.session_state.custom_us:
                    st.session_state.custom_us.remove(to_remove)
                st.sidebar.success(f"Removed {to_remove}")
                st.cache_data.clear()
                st.rerun()

    env_key = ""
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        env_key = line.split("=", 1)[1].strip()
        except Exception:
            pass

    default_key = st.session_state.get("openai_key", "") or env_key or os.environ.get("OPENAI_API_KEY", "")

    api_key = st.text_input("OpenAI API Key", type="password",
                            placeholder="sk-...",
                            value=default_key,
                            help="Required only for AI Chatbot tab. Saved locally in .env")
    if api_key:
        st.session_state.openai_key = api_key
        if api_key != default_key:
            try:
                with open(".env", "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key}\n")
            except Exception:
                pass
    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Data: Yahoo Finance · AI: Gemini")

# ─── Symbol set ───────────────────────────────────────────────────────────────
if market == "India (NSE)":
    symbols = st.session_state.custom_india
elif market == "US Markets":
    symbols = st.session_state.custom_us
else:
    symbols = st.session_state.custom_india + st.session_state.custom_us

currency = "₹" if market == "India (NSE)" else "$"


# ─── Dynamic Fragment Definition ──────────────────────────────────────────────
page = st.session_state.page
fragment_interval = refresh_seconds if page != "Chatbot" else None

@st.fragment(run_every=fragment_interval)
def render_live_dashboard():
    import time
    
    if refresh_seconds:
        cache_key = int(time.time() // refresh_seconds)
    else:
        cache_key = 0

    # ─── Market index bar ─────────────────────────────────────────────────────────
    with st.spinner("Loading indices..."):
        indices = fetch_indices(cache_key)
    
    if indices:
        ticker_cards_html = '<div class="ticker-container">'
        for name, d in indices.items():
            is_up = d["chg"] >= 0
            cls = "positive" if is_up else "negative"
            arrow = "↗" if is_up else "↘"
            
            # Format name
            lbl_name = "NIFTY" if "NIFTY" in name else ("SENSEX" if "SENSEX" in name else ("NASDAQ" if "NASDAQ" in name else "S&P500"))
            formatted_price = f"{d['price']:,.0f}"
            formatted_chg = f"{d['chg']:+.2f}%" if is_up else f"{d['chg']:.2f}%"
            
            ticker_cards_html += f"""
            <div class="ticker-card {cls}">
                <span class="label" style="font-size: 13px; font-weight: 600;">{arrow if "NIFTY" in lbl_name else ""} {lbl_name} {formatted_price}</span>
                <span class="value" style="font-size: 11px; font-weight: 500; opacity: 0.95; margin-top: 2px;">{formatted_chg}</span>
            </div>
            """
        # Let's add a clean search button / placeholder box on the right of the ticker bar to match the screenshot
        ticker_cards_html += """
            <div style="flex-grow: 1;"></div>
            <div style="width: 38px; height: 38px; border-radius: 8px; border: 1px solid #e2e8f0; background: #ffffff; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </div>
        </div>
        """
        st.markdown(clean_html(ticker_cards_html), unsafe_allow_html=True)
    if fragment_interval:
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin-top: -10px; margin-bottom: 15px; font-size: 11px; color: #64748b; font-weight: 500;'>
                <span style='display: inline-block; width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; animation: pulse 1.5s infinite;'></span>
                <span>Live updates active ({interval_choice}) · Last updated: {time.strftime('%H:%M:%S')}</span>
            </div>
            <style>
            @keyframes pulse {{
                0% {{ transform: scale(0.95); opacity: 0.5; }}
                50% {{ transform: scale(1.15); opacity: 1; }}
                100% {{ transform: scale(0.95); opacity: 0.5; }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    
    page = st.session_state.page
    
    # ══════════════════════════════════════════════════════════════════════════════
    #  PAGE: SCREENER
    # ══════════════════════════════════════════════════════════════════════════════
    if page == "Screener":
        selected_ticker = st.query_params.get("select", "")
        
        if selected_ticker:
            # ─── DRILL DOWN DETAIL VIEW ───
            # Resolving full symbol
            selected_ticker_full = selected_ticker
            if selected_ticker + ".NS" in symbols:
                selected_ticker_full = selected_ticker + ".NS"
            elif selected_ticker in symbols:
                selected_ticker_full = selected_ticker
                
            with st.spinner(f"Loading details for {selected_ticker}..."):
                stock_data = fetch_single_stock_data(selected_ticker_full)
                tk = yf.Ticker(selected_ticker_full)
                try:
                    info = tk.info
                except Exception:
                    info = {}
                
            if st.button("⬅ Back to Stock List", key="back_btn"):
                if "select" in st.query_params:
                    del st.query_params["select"]
                st.rerun()
                
            if not stock_data:
                st.error(f"Could not load details for {selected_ticker}. The symbol may be invalid or rate-limited.")
            else:
                # Resolve details using info with fallbacks to stock_data
                sym = stock_data["Symbol"]
                name = info.get("longName") or TICKER_NAMES.get(sym, sym)
                price = stock_data["Price"]
                chg = stock_data["Chg%"]
                sector = stock_data["Sector"]
                
                # Fetch key ratios
                pe = info.get("trailingPE") or stock_data["PE"] or 0
                beta = info.get("beta") or stock_data["Beta"] or 1.0
                div = (info.get("dividendYield") or 0) * 100 if info.get("dividendYield") else stock_data["Div%"]
                roe = (info.get("returnOnEquity") or 0) * 100 if info.get("returnOnEquity") else stock_data["ROE"]
                rsi = stock_data["RSI"]
                ai_score = stock_data["AI_Score"]
                signal = stock_data["Signal"]
                
                hi52 = info.get("fiftyTwoWeekHigh") or stock_data["52H"] or price
                lo52 = info.get("fiftyTwoWeekLow") or stock_data["52L"] or price
                book_val = info.get("bookValue") or (price / 1.5) # estimate book value if missing
                debt_equity = info.get("debtToEquity") # in percent (e.g. 80 means 0.8)
                face_val = info.get("faceValue") or (1.0 if currency == "₹" else 1.0)
                mkt_cap = info.get("marketCap") or stock_data["MktCap"] or 0

                # Formatted Market Cap
                is_inr = currency == "₹"
                if is_inr:
                    mcap_lbl = f"₹{mkt_cap/1e7:,.1f} Cr." if mkt_cap > 0 else "—"
                else:
                    mcap_lbl = f"${mkt_cap/1e6:,.1f} M" if mkt_cap > 0 else "—"

                chg_color = "#16a34a" if chg >= 0 else "#dc2626"
                chg_bg = "#e8f5e9" if chg >= 0 else "#ffebee"
                arrow = "+" if chg >= 0 else ""
                
                sig_color = "#15803d" if signal == "BUY" else ("#dc2626" if signal == "SELL" else "#854d0e")
                sig_bg = "#dcfce7" if signal == "BUY" else ("#fee2e2" if signal == "SELL" else "#fef9c3")

                # Layout: Left Header, Right Chart
                st.markdown(f"""
                <div style="margin-bottom: 25px; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px;">
                    <div style="font-size: 14px; font-weight: 600; color: #0b57d0; text-transform: uppercase; letter-spacing: 0.5px;">{sector}</div>
                    <h2 style="margin: 0; font-size: 34px; font-weight: 800; color: #0f172a; line-height: 1.2;">{name}</h2>
                    <div style="display: flex; align-items: baseline; gap: 14px; margin-top: 8px;">
                        <span style="font-size: 32px; font-weight: 800; color: #1e293b;">{currency}{price:,.2f}</span>
                        <span style="background: {chg_bg}; color: {chg_color}; padding: 3px 10px; border-radius: 6px; font-size: 14px; font-weight: 700;">{arrow}{chg:.2f}%</span>
                        <span style="font-size: 12px; color: #64748b; font-weight: 500;">Live Quote ({datetime.now().strftime('%d %b')})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Key Points Ratios Table (Screener.in format)
                st.markdown("### 📊 Key Statistics")
                st.markdown(f"""
                <div class="metrics-grid" style="grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 25px;">
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Market Cap</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{mcap_lbl}</span>
                        <span class="metric-change" style="font-size: 10px;">Total Valuation</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Current Price</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{currency}{price:,.2f}</span>
                        <span class="metric-change" style="font-size: 10px;">CMP</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">High / Low</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0; font-weight: 700;">{currency}{hi52:,.1f} / {lo52:,.1f}</span>
                        <span class="metric-change" style="font-size: 10px;">52-Week Range</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Stock P/E</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{f"{pe:.1f}" if pe > 0 else "—"}</span>
                        <span class="metric-change" style="font-size: 10px;">Price-to-earnings</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Book Value</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{currency}{book_val:,.1f}</span>
                        <span class="metric-change" style="font-size: 10px;">Net Asset Value</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Dividend Yield</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{div:.2f}%</span>
                        <span class="metric-change" style="font-size: 10px;">Annual dividend payout</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Return on Equity (ROE)</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{roe:.1f}%</span>
                        <span class="metric-change" style="font-size: 10px; color: {"#16a34a" if roe >= 15 else "#64748b"}">{ "Excellent (>15%)" if roe >= 15 else "Standard" }</span>
                    </div>
                    <div class="metric-card" style="padding: 14px 18px;">
                        <span class="metric-label" style="font-size: 11px;">Face Value</span>
                        <span class="metric-value" style="font-size: 20px; margin: 4px 0;">{currency}{face_val:.1f}</span>
                        <span class="metric-change" style="font-size: 10px;">Par Value</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # About / Business Segment Overview
                desc = info.get("longBusinessSummary")
                if desc:
                    st.markdown("### 📖 About")
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; margin-bottom: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); font-size: 13.5px; color: #334155; line-height: 1.6;">
                        <div style="font-weight: 700; font-size: 15px; color: #0f172a; margin-bottom: 8px;">Company Profile</div>
                        {desc}
                    </div>
                    """, unsafe_allow_html=True)

                # Splitting Chart & Pros/Cons in 2 columns
                col_c1, col_c2 = st.columns([6, 5])
                
                with col_c1:
                    st.markdown("#### 📈 Price Chart")
                    chart_period = st.selectbox("Chart Period", ["1mo","3mo","6mo","1y"], index=2, key="detail_period")
                    
                    with st.spinner("Loading chart data…"):
                        ohlcv = fetch_ohlcv(selected_ticker_full, chart_period)
                        
                    if not ohlcv.empty:
                        ohlcv["MA20"] = ohlcv["Close"].rolling(20).mean()
                        ohlcv["MA50"] = ohlcv["Close"].rolling(50).mean()
                        
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                            row_heights=[0.72, 0.28], vertical_spacing=0.04)
                        fig.add_trace(go.Candlestick(
                            x=ohlcv.index, open=ohlcv["Open"], high=ohlcv["High"],
                            low=ohlcv["Low"],  close=ohlcv["Close"], name="OHLC",
                            increasing_line_color="#16a34a", decreasing_line_color="#dc2626",
                        ), row=1, col=1)
                        fig.add_trace(go.Scatter(x=ohlcv.index, y=ohlcv["MA20"],
                                                  name="MA20", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=ohlcv.index, y=ohlcv["MA50"],
                                                  name="MA50", line=dict(color="#8b5cf6", width=1.5)), row=1, col=1)
                        fig.add_trace(go.Bar(x=ohlcv.index, y=ohlcv["Volume"],
                                              name="Volume", marker_color="#93c5fd"), row=2, col=1)
                        fig.update_layout(height=400, template="plotly_white",
                                           xaxis_rangeslider_visible=False,
                                           margin=dict(l=0, r=0, t=10, b=0),
                                           legend=dict(orientation="h", y=1.02))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Chart data not available for this ticker.")
                        
                with col_c2:
                    st.markdown("#### ⚖ Pros & Cons")
                    
                    # Generate Pros & Cons
                    def generate_pros_cons(price, book_val, pe, roe, debt_equity):
                        pros = []
                        cons = []
                        if debt_equity is not None:
                            if debt_equity < 15:
                                pros.append("Company is virtually debt free.")
                            elif debt_equity < 35:
                                pros.append("Company maintains a low debt-to-equity ratio.")
                        else:
                            pros.append("Company maintains almost debt-free operations.")
                            
                        if roe >= 15:
                            pros.append(f"Company has delivered a high return on equity (ROE) of {roe:.1f}%.")
                        if pe > 0 and pe < 20:
                            pros.append(f"Stock is trading at a reasonable valuation of {pe:.1f}x P/E.")
                            
                        # Cons
                        pb = price / book_val if book_val > 0 else 1.0
                        if pb > 8.0:
                            cons.append(f"Stock is trading at {pb:.1f} times its book value.")
                        elif pb > 4.0:
                            cons.append(f"Stock is trading at a premium book multiplier of {pb:.1f}x.")
                            
                        if pe > 40:
                            cons.append(f"Stock is trading at a high valuation multiple (P/E {pe:.1f}x).")
                        if roe < 8:
                            cons.append("ROE metrics are relatively low compared to benchmark.")
                            
                        if not pros:
                            pros.append("Company maintains stable, cash-flow generative operations.")
                        if not cons:
                            cons.append("Growth is dependent on overall segment capital expenditure.")
                            
                        return pros, cons

                    pros, cons = generate_pros_cons(price, book_val, pe, roe, debt_equity)
                    
                    pros_list = "".join(f"<li style='color:#16a34a; margin-bottom:8px;'><b>Pros:</b> {p}</li>" for p in pros)
                    cons_list = "".join(f"<li style='color:#dc2626; margin-bottom:8px;'><b>Cons:</b> {c}</li>" for c in cons)
                    
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; min-height: 400px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                        <div style="font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 12px;">Automated Analysis</div>
                        <ul style="padding-left: 15px; margin: 0; font-size: 13px; line-height: 1.5;">
                            {pros_list}
                            {cons_list}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                # Peer Comparison (Screener.in format)
                st.markdown("### 👥 Peer Comparison")
                try:
                    all_stocks_df = fetch_stock_data(tuple(symbols), cache_key)
                    peers_df = all_stocks_df[all_stocks_df["Sector"] == sector]
                except Exception:
                    peers_df = pd.DataFrame()
                    
                if not peers_df.empty:
                    html_peers = """
                    <div class="table-container" style="margin-bottom: 25px;">
                        <table class="custom-table" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Price</th>
                                    <th>P/E</th>
                                    <th>ROE%</th>
                                    <th>Div Yld%</th>
                                    <th>RSI</th>
                                    <th>Rating</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    for _, prow in peers_df.iterrows():
                        psym = prow["Symbol"]
                        pname = TICKER_NAMES.get(psym, psym)
                        pprice = prow["Price"]
                        ppe = prow["PE"]
                        proe = prow["ROE"]
                        pdiv = prow["Div%"]
                        prsi = prow["RSI"]
                        pcomp = prow["AI_Score"]
                        
                        f_price = f"₹{pprice:,.1f}" if is_inr else f"${pprice:,.2f}"
                        f_pe = f"{ppe:.1f}" if ppe > 0 else "—"
                        f_roe = f"{proe:.1f}%"
                        f_div = f"{pdiv:.2f}%"
                        
                        active_style = "background-color: #edf2fa; font-weight:700;" if psym == sym else ""
                        
                        html_peers += f"""
                        <tr style="{active_style}">
                            <td><a href="?page=Screener&select={psym}" target="_self" class="symbol-cell">{psym}</a></td>
                            <td class="price-cell">{f_price}</td>
                            <td>{f_pe}</td>
                            <td>{f_roe}</td>
                            <td>{f_div}</td>
                            <td>{prsi}</td>
                            <td style="font-weight:700; color:#0b57d0;">{pcomp}/100</td>
                        </tr>
                        """
                    html_peers += "</tbody></table></div>"
                    st.markdown(clean_html(html_peers), unsafe_allow_html=True)
                else:
                    st.info("No peer comparison data available for this sector.")

                # Quarterly Results Table
                st.markdown("### 📅 Quarterly Results")
                
                def get_quarterly_results_html(tk):
                    try:
                        qf = tk.quarterly_financials
                        if qf is None or qf.empty:
                            return '<div style="padding: 15px; color: #64748b;">Quarterly results are currently unavailable for this stock.</div>'
                            
                        # Rename columns
                        formatted_cols = []
                        for col in qf.columns:
                            if isinstance(col, datetime) or hasattr(col, "strftime"):
                                formatted_cols.append(col.strftime("%b %y"))
                            else:
                                formatted_cols.append(str(col))
                        
                        df_display = qf.copy()
                        df_display.columns = formatted_cols
                        df_display = df_display.iloc[:, :5]
                        df_display = df_display.iloc[:, ::-1]
                        
                        divisor = 1e7 if is_inr else 1e6
                        unit_lbl = "Crores" if is_inr else "Millions"
                        
                        rows_to_show = []
                        if "Total Revenue" in df_display.index:
                            sales = df_display.loc["Total Revenue"].apply(lambda x: f"{x/divisor:.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Sales", sales))
                        if "Operating Income" in df_display.index:
                            op = df_display.loc["Operating Income"].apply(lambda x: f"{x/divisor:.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Operating Profit", op))
                            if "Total Revenue" in df_display.index:
                                opm = []
                                for col in df_display.columns:
                                    rev_val = df_display.loc["Total Revenue", col]
                                    op_val = df_display.loc["Operating Income", col]
                                    if rev_val and op_val and not pd.isna(rev_val) and not pd.isna(op_val) and rev_val > 0:
                                        opm.append(f"{op_val / rev_val * 100:.0f}%")
                                    else:
                                        opm.append("—")
                                rows_to_show.append(("OPM %", opm))
                        if "Pretax Income" in df_display.index:
                            pbt = df_display.loc["Pretax Income"].apply(lambda x: f"{x/divisor:.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Profit before tax", pbt))
                        if "Net Income" in df_display.index:
                            np_row = df_display.loc["Net Income"].apply(lambda x: f"{x/divisor:.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Net Profit", np_row))
                        eps_row_name = "Basic EPS" if "Basic EPS" in df_display.index else ("Diluted EPS" if "Diluted EPS" in df_display.index else None)
                        if eps_row_name:
                            eps = df_display.loc[eps_row_name].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("EPS in Rs" if is_inr else "EPS", eps))
                            
                        html = '<div class="table-container"><table class="custom-table" style="width:100%; border-collapse:collapse; font-size:13px;"><thead><tr><th style="padding:10px; text-align:left;">Metrics</th>'
                        for col in df_display.columns:
                            html += f'<th style="padding:10px; text-align:right;">{col}</th>'
                        html += '</tr></thead><tbody>'
                        for name, vals in rows_to_show:
                            html += f'<tr><td style="padding:10px; font-weight:600; color:#334155;">{name}</td>'
                            for val in vals:
                                html += f'<td style="padding:10px; text-align:right; color:#1e293b;">{val}</td>'
                            html += '</tr>'
                        html += '</tbody></table></div>'
                        html += f'<div style="font-size:11px; color:#64748b; margin-top:8px; text-align:right; font-weight:500;">* Figures in {unit_lbl} (except EPS)</div>'
                        return html
                    except Exception as e:
                        return f'<div style="padding: 15px; color: #dc2626;">Error parsing quarterly results: {e}</div>'
                
                st.markdown(get_quarterly_results_html(tk), unsafe_allow_html=True)

                # Balance Sheet
                st.markdown("### ⚖ Balance Sheet")
                
                def get_balance_sheet_html(tk):
                    try:
                        bs = tk.balance_sheet
                        if bs is None or bs.empty:
                            return '<div style="padding: 15px; color: #64748b;">Balance sheet data is currently unavailable for this stock.</div>'
                            
                        formatted_cols = []
                        for col in bs.columns:
                            if isinstance(col, datetime) or hasattr(col, "strftime"):
                                formatted_cols.append(col.strftime("%b %y"))
                            else:
                                formatted_cols.append(str(col))
                                
                        df_display = bs.copy()
                        df_display.columns = formatted_cols
                        df_display = df_display.iloc[:, :4]
                        df_display = df_display.iloc[:, ::-1]
                        
                        divisor = 1e7 if is_inr else 1e6
                        unit_lbl = "Crores" if is_inr else "Millions"
                        
                        rows_to_show = []
                        if "Common Stock" in df_display.index:
                            cap = df_display.loc["Common Stock"].apply(lambda x: f"{x/divisor:,.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Share Capital", cap))
                        if "Retained Earnings" in df_display.index:
                            res = df_display.loc["Retained Earnings"].apply(lambda x: f"{x/divisor:,.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Reserves", res))
                        if "Total Debt" in df_display.index:
                            debt = df_display.loc["Total Debt"].apply(lambda x: f"{x/divisor:,.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Borrowings", debt))
                            
                        if "Total Liabilities Net Minority Interest" in df_display.index:
                            other_liab = []
                            for col in df_display.columns:
                                tot = df_display.loc["Total Liabilities Net Minority Interest", col]
                                dbt = df_display.loc["Total Debt", col] if "Total Debt" in df_display.index else 0
                                val = tot - dbt if not pd.isna(tot) and not pd.isna(dbt) else 0
                                other_liab.append(f"{val/divisor:,.1f}" if val > 0 else "—")
                            rows_to_show.append(("Other Liabilities", other_liab))
                            
                        if "Total Assets" in df_display.index:
                            tot_assets = df_display.loc["Total Assets"].apply(lambda x: f"{x/divisor:,.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Total Liabilities", tot_assets))
                            
                        if "Net PPE" in df_display.index:
                            fa = df_display.loc["Net PPE"].apply(lambda x: f"{x/divisor:,.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Fixed Assets", fa))
                            
                        inv_row_name = "Investments And Advances" if "Investments And Advances" in df_display.index else ("Other Investments" if "Other Investments" in df_display.index else None)
                        if inv_row_name:
                            inv = df_display.loc[inv_row_name].apply(lambda x: f"{x/divisor:,.1f}" if not pd.isna(x) else "—")
                            rows_to_show.append(("Investments", inv))
                            
                        if "Total Assets" in df_display.index:
                            other_assets = []
                            for col in df_display.columns:
                                tot = df_display.loc["Total Assets", col]
                                fa_val = df_display.loc["Net PPE", col] if "Net PPE" in df_display.index else 0
                                inv_val = df_display.loc[inv_row_name, col] if inv_row_name else 0
                                val = tot - fa_val - inv_val if not pd.isna(tot) and not pd.isna(fa_val) and not pd.isna(inv_val) else 0
                                other_assets.append(f"{val/divisor:,.1f}" if val > 0 else "—")
                            rows_to_show.append(("Other Assets", other_assets))
                            
                        if "Total Assets" in df_display.index:
                            rows_to_show.append(("Total Assets", tot_assets))
                            
                        html = '<div class="table-container"><table class="custom-table" style="width:100%; border-collapse:collapse; font-size:13px;"><thead><tr><th style="padding:10px; text-align:left;">Sources & Application</th>'
                        for col in df_display.columns:
                            html += f'<th style="padding:10px; text-align:right;">{col}</th>'
                        html += '</tr></thead><tbody>'
                        for name, vals in rows_to_show:
                            is_bold = name in ["Total Liabilities", "Total Assets"]
                            font_wt = "700" if is_bold else "500"
                            bg_col = "#fafaf8" if is_bold else "transparent"
                            html += f'<tr style="background-color: {bg_col};"><td style="padding:10px; font-weight:{font_wt}; color:#334155;">{name}</td>'
                            for val in vals:
                                html += f'<td style="padding:10px; text-align:right; font-weight:{font_wt}; color:#1e293b;">{val}</td>'
                            html += '</tr>'
                        html += '</tbody></table></div>'
                        html += f'<div style="font-size:11px; color:#64748b; margin-top:8px; text-align:right; font-weight:500;">* Figures in {unit_lbl}</div>'
                        return html
                    except Exception as e:
                        return f'<div style="padding: 15px; color: #dc2626;">Error parsing balance sheet: {e}</div>'
                
                st.markdown(get_balance_sheet_html(tk), unsafe_allow_html=True)

                # Shareholding Pattern
                st.markdown("### 📈 Shareholding Pattern")
                try:
                    mh = tk.major_holders
                    if mh is not None and not mh.empty:
                        insiders = mh.loc["insidersPercentHeld", "Value"] * 100 if "insidersPercentHeld" in mh.index else 0
                        institutions = mh.loc["institutionsPercentHeld", "Value"] * 100 if "institutionsPercentHeld" in mh.index else 0
                        public = max(0.0, 100.0 - (insiders + institutions))
                    else:
                        insiders, institutions, public = 59.1, 7.5, 33.4
                except Exception:
                    insiders, institutions, public = 59.1, 7.5, 33.4
                    
                html_shareholders = f"""
                <div class="table-container" style="margin-bottom: 25px;">
                    <table class="custom-table" style="width:100%;">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th style="text-align:right;">Holding Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><b>Promoters / Insiders</b></td>
                                <td style="text-align:right; font-weight:700; color:#1e293b;">{insiders:.2f}%</td>
                            </tr>
                            <tr>
                                <td><b>Institutions (FIIs + DIIs)</b></td>
                                <td style="text-align:right; font-weight:700; color:#0b57d0;">{institutions:.2f}%</td>
                            </tr>
                            <tr>
                                <td><b>Public Shareholders</b></td>
                                <td style="text-align:right; font-weight:700; color:#475569;">{public:.2f}%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """
                st.markdown(clean_html(html_shareholders), unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 🤖 Social & News AI Sentiment Summary")
                
                news = fetch_stock_news(sym)
                reddit = fetch_reddit_posts(sym)
                
                openai_key = st.session_state.get("openai_key", "") or env_key or os.environ.get("OPENAI_API_KEY", "")
                
                if openai_key:
                    with st.spinner("Analyzing news and retail discussion..."):
                        sentiment_data = analyze_stock_sentiment(sym, news, reddit, openai_key)
                        
                    s_val = sentiment_data.get("sentiment", "NEUTRAL")
                    s_badge_color = "#15803d" if s_val == "BULLISH" else ("#dc2626" if s_val == "BEARISH" else "#854d0e")
                    s_badge_bg = "#dcfce7" if s_val == "BULLISH" else ("#fee2e2" if s_val == "BEARISH" else "#fef9c3")
                    
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; margin-bottom: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                            <span style="font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase;">AI Sentiment Assessment</span>
                            <span style="background: {s_badge_bg}; color: {s_badge_color}; padding: 4px 16px; border-radius: 20px; font-size: 13px; font-weight: 700; text-transform: uppercase;">{s_val}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div>
                                <h5 style="margin: 0 0 6px 0; font-size: 13.5px; font-weight: 700; color: #0b57d0;">Professional News Analysis</h5>
                                <p style="margin: 0; font-size: 13px; color: #334155; line-height: 1.5;">{sentiment_data.get('summary_news', '')}</p>
                            </div>
                            <div style="border-left: 1px solid #f1f5f9; padding-left: 20px;">
                                <h5 style="margin: 0 0 6px 0; font-size: 13.5px; font-weight: 700; color: #8b5cf6;">Retail Social Media Sentiment (Reddit)</h5>
                                <p style="margin: 0; font-size: 13px; color: #334155; line-height: 1.5;">{sentiment_data.get('summary_reddit', '')}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 22px; text-align: center; margin-bottom: 25px;">
                        <h4 style="margin: 0 0 6px 0; font-size: 16px; font-weight: 700; color: #1e293b;">Unlock AI-Powered Sentiment Summaries</h4>
                        <p style="margin: 0 auto; max-width: 500px; font-size: 13px; color: #64748b; line-height: 1.5;">
                            Provide your OpenAI API key in the sidebar to run semantic summaries of recent Yahoo Finance news and Reddit discussions for {sym}.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                col_news, col_reddit = st.columns(2)
                
                with col_news:
                    st.markdown("#### 📰 Recent News Feed")
                    if news:
                        for item in news[:4]:
                            st.markdown(f"""
                            <div class="rec-card" style="margin-bottom: 10px; padding: 12px 16px;">
                                <div style="font-size: 11px; font-weight: 600; color: #0b57d0; text-transform: uppercase;">{item['publisher']}</div>
                                <h5 style="margin: 4px 0 6px 0; font-size: 14px; font-weight: 700;"><a href="{item['link']}" target="_blank" style="color: #1e293b; text-decoration: none;">{item['title']}</a></h5>
                                <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">{item['summary'][:160]}...</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No recent news found for this stock.")
                        
                with col_reddit:
                    st.markdown("#### 💬 Reddit Discussions")
                    if reddit:
                        for item in reddit[:4]:
                            st.markdown(f"""
                            <div class="rec-card" style="margin-bottom: 10px; padding: 12px 16px;">
                                <div style="font-size: 11px; font-weight: 600; color: #8b5cf6;">{item['author']}</div>
                                <h5 style="margin: 4px 0 6px 0; font-size: 14px; font-weight: 700;"><a href="{item['link']}" target="_blank" style="color: #1e293b; text-decoration: none;">{item['title']}</a></h5>
                                <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">{item['content'][:160]}...</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No recent Reddit discussions found for this stock.")
        else:
            # ─── STANDARD SCREENER TABLE VIEW ───
            st.markdown('<div class="sec-hdr">🔍 Stock Screener — Live Data</div>', unsafe_allow_html=True)
    
            df = pd.DataFrame()
            try:
                with st.spinner("Fetching live market data…"):
                    df = fetch_stock_data(tuple(symbols), cache_key)
            except Exception as e:
                st.error(f"Could not fetch stock data: {e}. Check your internet connection and try refreshing.")
                st.stop()
        
            # ── Summary metrics cards ──
            stocks_screened = f"{len(df):,}"
            buy_signals_count = len(df[df["Signal"] == "BUY"]) if not df.empty else 0
            sell_signals_count = len(df[df["Signal"] == "SELL"]) if not df.empty else 0
            
            total_mcap = df["MktCap"].sum() if not df.empty else 0
            if total_mcap > 1e12:
                mcap_text = f"₹{total_mcap/1e12:.2f}T" if currency == "₹" else f"${total_mcap/1e12:.2f}T"
            elif total_mcap > 1e9:
                mcap_text = f"₹{total_mcap/1e9:.2f}B" if currency == "₹" else f"${total_mcap/1e9:.2f}B"
            else:
                mcap_text = f"₹{total_mcap/1e6:.1f}M" if currency == "₹" else f"${total_mcap/1e6:.1f}M"
                
            avg_chg = df["Chg%"].mean() if not df.empty else 0.0
            mcap_chg = f"{avg_chg:+.2f}%"

            # Determine color and arrow classes for average change
            avg_chg_cls = "positive" if avg_chg >= 0 else "negative"
            avg_chg_arr = "↑" if avg_chg >= 0 else "↓"
            buy_pct = (buy_signals_count / len(df) * 100) if len(df) > 0 else 0
            sell_pct = (sell_signals_count / len(df) * 100) if len(df) > 0 else 0
            
            metrics_html = f"""
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-label">Market Cap<br>(Total)</span>
                    <span class="metric-value">{mcap_text}</span>
                    <span class="metric-change {avg_chg_cls}">{avg_chg_arr} {mcap_chg} avg change</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Stocks<br>Screened</span>
                    <span class="metric-value">{stocks_screened}</span>
                    <span class="metric-change" style="color: #64748b;">active screener stocks</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Buy Signals</span>
                    <span class="metric-value buy">{buy_signals_count}</span>
                    <span class="metric-change positive">↑ {buy_pct:.0f}% of active stocks</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Sell Signals</span>
                    <span class="metric-value sell">{sell_signals_count}</span>
                    <span class="metric-change negative">↓ {sell_pct:.0f}% of active stocks</span>
                </div>
            </div>
            """
            st.markdown(clean_html(metrics_html), unsafe_allow_html=True)
        
            # ── Custom URL Query Param Filters ──
            qp = st.query_params
            active_cap = qp.get("cap", "")
            active_pe20 = qp.get("pe20", "") == "true"
            active_roe = qp.get("roe", "") == "true"
            active_signal = qp.get("signal", "")
            active_dividend = qp.get("dividend", "") == "true"
            active_sector = qp.get("sector", "")
        
            pills_r1 = []
            pills_r1.append(render_pill("Large Cap", "cap", "Large", active_cap == "Large"))
            pills_r1.append(render_pill("Mid Cap", "cap", "Mid", active_cap == "Mid"))
            pills_r1.append(render_pill("Small Cap", "cap", "Small", active_cap == "Small"))
            pills_r1.append(render_pill("PE &lt; 20", "pe20", "true", active_pe20))
            pills_r1.append(render_pill("High ROE", "roe", "true", active_roe))
        
            pills_r2 = []
            pills_r2.append(render_pill("Buy Signal", "signal", "BUY", active_signal == "BUY"))
            pills_r2.append(render_pill("Dividend", "dividend", "true", active_dividend))
            pills_r2.append(render_pill("IT Sector", "sector", "IT", active_sector == "IT"))
            pills_r2.append(render_pill("Banking", "sector", "Banking", active_sector == "Banking"))
        
            filters_html = f"""
            <div class="filter-section">
                <div class="filter-row">
                    <span class="filter-label">Filters:</span>
                    {" ".join(pills_r1)}
                </div>
                <div class="filter-row" style="margin-top: 10px; padding-left: 64px;">
                    {" ".join(pills_r2)}
                </div>
            </div>
            """
            st.markdown(clean_html(filters_html), unsafe_allow_html=True)
        
            # ── Search Input ──
            search = st.text_input("🔍 Search symbol", "", label_visibility="collapsed", placeholder="🔍 Search symbol...")
        
            # ── Apply Filters in Python ──
            fdf = df.copy()
        
            if active_cap == "Large":
                threshold = 5e11 if currency == "₹" else 1e10
                fdf = fdf[fdf["MktCap"] >= threshold]
            elif active_cap == "Mid":
                lower = 5e10 if currency == "₹" else 2e9
                upper = 5e11 if currency == "₹" else 1e10
                fdf = fdf[(fdf["MktCap"] >= lower) & (fdf["MktCap"] < upper)]
            elif active_cap == "Small":
                threshold = 5e10 if currency == "₹" else 2e9
                fdf = fdf[fdf["MktCap"] < threshold]
        
            if active_pe20:
                fdf = fdf[(fdf["PE"] > 0) & (fdf["PE"] < 20)]
        
            if active_roe:
                fdf = fdf[fdf["ROE"] >= 15]
        
            if active_signal == "BUY":
                fdf = fdf[fdf["Signal"] == "BUY"]
        
            if active_dividend:
                fdf = fdf[fdf["Div%"] >= 1.5]
        
            if active_sector == "IT":
                fdf = fdf[fdf["Sector"].str.contains("Technology|Tech|Software", case=False, na=False)]
            elif active_sector == "Banking":
                fdf = fdf[fdf["Sector"].str.contains("Financial|Bank", case=False, na=False)]
        
            if search:
                search_clean = search.strip().lower()
                
                # Check if it matches anything in the unfiltered database `df`
                matched_unfiltered = df[
                    df["Symbol"].str.lower().str.contains(search_clean, na=False) |
                    df["Name"].str.lower().str.contains(search_clean, na=False)
                ]
                
                if matched_unfiltered.empty:
                    # Not found in database. Search and auto-add from global exchanges.
                    with st.spinner(f"Fetching '{search}' from global exchanges…"):
                        suggestions = search_ticker_by_name(search)
                    
                    if suggestions:
                        best_match = suggestions[0]
                        sym_to_add = best_match["symbol"]
                        
                        sym_upper = sym_to_add.upper()
                        in_india_list = any(s.upper() == sym_upper for s in st.session_state.custom_india)
                        in_us_list = any(s.upper() == sym_upper for s in st.session_state.custom_us)
                        already_in_lists = in_india_list or in_us_list
                        
                        is_in_active_symbols = any(s.upper() == sym_upper for s in symbols)
                        
                        if not already_in_lists:
                            st.toast(f"Adding {sym_to_add} to screener stocks...")
                            add_custom_symbol(sym_to_add, market)
                        elif not is_in_active_symbols:
                            st.toast(f"Switching market view to show {sym_to_add}...")
                            add_custom_symbol(sym_to_add, market)
                        else:
                            st.warning(f"Stock '{sym_to_add}' is already in your screener list but could not be loaded. Please check if the ticker symbol is valid on Yahoo Finance.")
                    else:
                        st.markdown(f"""
                        <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 22px; text-align: center; margin-bottom: 20px;">
                            <h4 style="margin: 0 0 6px 0; font-size: 15px; font-weight: 700; color: #1e293b;">No results found for '{search}'</h4>
                            <p style="margin: 0 auto 15px auto; max-width: 400px; font-size: 12.5px; color: #64748b; line-height: 1.5;">
                                Could not resolve any ticker symbols for this name on global exchanges. Try typing a direct ticker symbol (e.g., TSLA, AMD, WIPRO.NS).
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Found in unfiltered database `df`.
                    # Let's search inside the filtered dataframe `fdf`.
                    matched_fdf = fdf[
                        fdf["Symbol"].str.lower().str.contains(search_clean, na=False) |
                        fdf["Name"].str.lower().str.contains(search_clean, na=False)
                    ]
                    
                    if matched_fdf.empty:
                        # Hidden by active filters!
                        st.info(f"💡 '{search}' is already in your screener stocks database, but is hidden by your active filters.")
                        if st.button("Clear active filters to show search results", use_container_width=True):
                            for k in ["cap", "pe20", "roe", "signal", "dividend", "sector"]:
                                st.query_params.pop(k, None)
                            st.rerun()
                    else:
                        fdf = matched_fdf

            # ── Render custom HTML table ──
            st.markdown(f"<div style='font-size: 13px; color: #64748b; font-weight: 500; margin-bottom: 8px;'>Showing {len(fdf)} stocks</div>", unsafe_allow_html=True)
            st.markdown(clean_html(render_custom_table(fdf, currency)), unsafe_allow_html=True)
        
            # ── Candlestick chart ──
            st.markdown("---")
            st.markdown("#### 📈 Candlestick Chart")
            sym_opts = fdf["_sym"].tolist() if not fdf.empty else df["_sym"].tolist()
            if sym_opts:
                col_s, col_p = st.columns([3, 1])
                
                selected_ticker = qp.get("select", "")
                selected_ticker_full = selected_ticker + ".NS" if market == "India (NSE)" else selected_ticker
                
                default_sel_idx = 0
                if selected_ticker_full in sym_opts:
                    default_sel_idx = sym_opts.index(selected_ticker_full)
                elif selected_ticker in sym_opts:
                    default_sel_idx = sym_opts.index(selected_ticker)
                    
                sel = col_s.selectbox("Select stock", sym_opts, index=default_sel_idx,
                                       format_func=lambda x: x.replace(".NS", ""))
                period = col_p.selectbox("Period", ["1mo","3mo","6mo","1y"], index=1)
                with st.spinner("Loading chart…"):
                    ohlcv = fetch_ohlcv(sel, period)
                if not ohlcv.empty:
                    ohlcv["MA20"] = ohlcv["Close"].rolling(20).mean()
                    ohlcv["MA50"] = ohlcv["Close"].rolling(50).mean()
                    
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        row_heights=[0.75, 0.25], vertical_spacing=0.03)
                    fig.add_trace(go.Candlestick(
                        x=ohlcv.index, open=ohlcv["Open"], high=ohlcv["High"],
                        low=ohlcv["Low"],  close=ohlcv["Close"], name="OHLC",
                        increasing_line_color="#16a34a", decreasing_line_color="#dc2626",
                    ), row=1, col=1)
                    fig.add_trace(go.Scatter(x=ohlcv.index, y=ohlcv["MA20"],
                                              name="MA20", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=ohlcv.index, y=ohlcv["MA50"],
                                              name="MA50", line=dict(color="#8b5cf6", width=1.5)), row=1, col=1)
                    fig.add_trace(go.Bar(x=ohlcv.index, y=ohlcv["Volume"],
                                          name="Volume", marker_color="#93c5fd"), row=2, col=1)
                    fig.update_layout(height=450, template="plotly_white",
                                       xaxis_rangeslider_visible=False,
                                       margin=dict(l=0, r=0, t=30, b=0),
                                       legend=dict(orientation="h", y=1.02))
                    st.plotly_chart(fig, use_container_width=True)    # ══════════════════════════════════════════════════════════════════════════════
    #  PAGE: AI PREDICTIONS
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Predictions":
        st.markdown('<div class="sec-hdr">🤖 AI Predictions — Tomorrow\'s Movement</div>', unsafe_allow_html=True)
        st.info("Model uses RSI momentum, price action, beta & AI composite score. **Not financial advice.**")
    
        df = pd.DataFrame()
        rise, fall = pd.DataFrame(), pd.DataFrame()
        try:
            with st.spinner("Running prediction models on live data…"):
                df = fetch_stock_data(tuple(symbols), cache_key)
                rise, fall = ai_prediction(df)
        except Exception as e:
            st.error(f"No prediction data available: {e}.")
            st.stop()
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown("### 📈 Likely to Rise")
            if rise.empty:
                st.info("No strong rise predictions today.")
            for _, r in rise.iterrows():
                conf = min(abs(float(r["conf"])), 95)
                st.markdown(f"""
                <div class="rise-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <div>
                      <span style="font-weight:700;font-size:16px;color:#15803d">{r['Symbol']}</span>
                      <span style="font-size:11px;color:#64748b;margin-left:8px">{r['Sector']}</span>
                    </div>
                    <span style="font-size:20px;font-weight:700;color:#15803d">{conf:.0f}%</span>
                  </div>
                  <div style="background:#bbf7d0;border-radius:4px;height:5px;margin-bottom:6px">
                    <div style="width:{conf}%;background:#16a34a;height:100%;border-radius:4px"></div>
                  </div>
                  <div style="display:flex;gap:16px;font-size:12px;color:#374151">
                    <span>RSI <b>{r['RSI']}</b></span>
                    <span>Score <b>{r['AI_Score']}/100</b></span>
                    <span>Today <b style="color:{'#16a34a' if r['Chg%']>0 else '#dc2626'}">{r['Chg%']:+.2f}%</b></span>
                    <span>β <b>{r['Beta']}</b></span>
                  </div>
                </div>""", unsafe_allow_html=True)
    
        with col2:
            st.markdown("### 📉 Likely to Fall")
            if fall.empty:
                st.info("No strong fall predictions today.")
            for _, r in fall.iterrows():
                conf = min(abs(float(r["conf"])), 95)
                st.markdown(f"""
                <div class="fall-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <div>
                      <span style="font-weight:700;font-size:16px;color:#dc2626">{r['Symbol']}</span>
                      <span style="font-size:11px;color:#64748b;margin-left:8px">{r['Sector']}</span>
                    </div>
                    <span style="font-size:20px;font-weight:700;color:#dc2626">{conf:.0f}%</span>
                  </div>
                  <div style="background:#fecaca;border-radius:4px;height:5px;margin-bottom:6px">
                    <div style="width:{conf}%;background:#dc2626;height:100%;border-radius:4px"></div>
                  </div>
                  <div style="display:flex;gap:16px;font-size:12px;color:#374151">
                    <span>RSI <b>{r['RSI']}</b></span>
                    <span>Score <b>{r['AI_Score']}/100</b></span>
                    <span>Today <b style="color:{'#16a34a' if r['Chg%']>0 else '#dc2626'}">{r['Chg%']:+.2f}%</b></span>
                    <span>β <b>{r['Beta']}</b></span>
                  </div>
                </div>""", unsafe_allow_html=True)
    
        # Sector chart
        st.markdown("---")
        st.markdown("#### Sector Confidence")
        grp = df.groupby("Sector")["AI_Score"].mean().reset_index().sort_values("AI_Score", ascending=False)
        grp = grp[grp["Sector"] != "—"]
        fig = px.bar(grp, x="Sector", y="AI_Score",
                     color="AI_Score", color_continuous_scale=["#dc2626","#f59e0b","#16a34a"],
                     range_color=[30, 80], template="plotly_white",
                     labels={"AI_Score": "Avg AI Score"})
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
        # RSI histogram
        st.markdown("#### RSI Distribution")
        fig2 = px.histogram(df, x="RSI", nbins=20, color_discrete_sequence=["#3b82f6"], template="plotly_white")
        fig2.add_vline(x=30, line_dash="dash", line_color="#16a34a", annotation_text="Oversold (30)")
        fig2.add_vline(x=70, line_dash="dash", line_color="#dc2626", annotation_text="Overbought (70)")
        fig2.update_layout(height=240, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)
    
    # ══════════════════════════════════════════════════════════════════════════════
    #  PAGE: PORTFOLIO
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Portfolio":
        st.markdown('<div class="sec-hdr">💼 Portfolio Dashboard</div>', unsafe_allow_html=True)
    
        with st.expander("➕ Add / Remove Holding"):
            a1, a2, a3, a4 = st.columns(4)
            new_sym = a1.text_input("Symbol (e.g. RELIANCE.NS)")
            new_qty = a2.number_input("Qty", 1, 100000, 10)
            new_avg = a3.number_input("Avg Buy Price", 0.01, 1e7, 100.0, format="%.2f")
            a4.write("")
            a4.write("")
            if a4.button("➕ Add"):
                if new_sym.strip():
                    st.session_state.portfolio[new_sym.strip().upper()] = {
                        "qty": new_qty, "avg_price": new_avg}
                    st.success(f"Added {new_sym.upper()}")
                    st.rerun()
            rem_sym = st.selectbox("Remove", [""] + list(st.session_state.portfolio.keys()))
            if st.button("🗑 Remove") and rem_sym:
                del st.session_state.portfolio[rem_sym]
                st.rerun()
    
        with st.spinner("Fetching live prices…"):
            pf = portfolio_value()
    
        if pf.empty:
            st.warning("No holdings or could not fetch prices.")
            st.stop()
    
        total_val  = pf["Value"].sum()
        total_cost = pf["Cost"].sum()
        total_pnl  = pf["P&L"].sum()
        pnl_pct    = round(total_pnl / total_cost * 100, 2) if total_cost else 0
    
        metrics_pf_html = f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-label">Total Value</span>
                <span class="metric-value">{currency}{total_val:,.0f}</span>
                <span class="metric-change" style="color: #64748b;">Current value</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Invested</span>
                <span class="metric-value">{currency}{total_cost:,.0f}</span>
                <span class="metric-change" style="color: #64748b;">Total cost basis</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Unrealised P&L</span>
                <span class="metric-value {'buy' if total_pnl >= 0 else 'sell'}">{currency}{total_pnl:,.0f}</span>
                <span class="metric-change {'positive' if total_pnl >= 0 else 'negative'}">{"↑" if total_pnl >= 0 else "↓"} {pnl_pct:+.2f}%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Holdings</span>
                <span class="metric-value">{len(pf)}</span>
                <span class="metric-change" style="color: #64748b;">Active positions</span>
            </div>
        </div>
        """
        st.markdown(clean_html(metrics_pf_html), unsafe_allow_html=True)
    
        st.markdown("---")
        cl, cr = st.columns([3, 2])
    
        with cl:
            st.markdown("#### Holdings")
            st.markdown(clean_html(render_portfolio_table(pf, currency)), unsafe_allow_html=True)
    
            # Portfolio history for top holding
            top_sym = list(st.session_state.portfolio.keys())[0]
            hist_pf = fetch_ohlcv(top_sym, "6mo")
            if not hist_pf.empty:
                st.markdown(f"#### 6-month: {top_sym.replace('.NS','')}")
                qty = st.session_state.portfolio[top_sym]["qty"]
                fig = go.Figure(go.Scatter(
                    x=hist_pf.index, y=(hist_pf["Close"] * qty).round(0),
                    fill="tozeroy", fillcolor="rgba(59,130,246,0.1)",
                    line=dict(color="#3b82f6", width=2), name="Value"
                ))
                fig.update_layout(height=220, template="plotly_white",
                                   margin=dict(l=0,r=0,t=10,b=0),
                                   yaxis_title="Value (₹)")
                st.plotly_chart(fig, use_container_width=True)
    
        with cr:
            st.markdown("#### Allocation")
            fig_d = go.Figure(go.Pie(
                labels=pf["Symbol"], values=pf["Value"],
                hole=0.6, textinfo="percent+label",
                marker=dict(colors=px.colors.qualitative.Set2),
            ))
            fig_d.update_layout(height=260, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
            st.plotly_chart(fig_d, use_container_width=True)
    
            st.markdown("#### P&L per Holding")
            colors = ["#16a34a" if v > 0 else "#dc2626" for v in pf["P&L"]]
            fig_b = go.Figure(go.Bar(
                x=pf["Symbol"], y=pf["P&L"], marker_color=colors,
                text=pf["P&L%"].apply(lambda x: f"{x:+.1f}%"), textposition="outside"
            ))
            fig_b.update_layout(height=220, template="plotly_white",
                                 margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_b, use_container_width=True)
    
    # ══════════════════════════════════════════════════════════════════════════════
    #  PAGE: FOR YOU
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "ForYou":
        st.markdown('<div class="sec-hdr">⭐ Personalised Stock Picks</div>', unsafe_allow_html=True)
    
        r1, r2 = st.columns(2)
        risk     = r1.select_slider("Risk appetite", ["Conservative","Moderate","Aggressive"], "Moderate")
        horizon  = r2.selectbox("Horizon", ["Short (1–4 wks)","Medium (1–6 mo)","Long (1+ yr)"])
        sec_pref = st.multiselect("Preferred sectors (optional)",
                                   ["Technology","Financial Services","Healthcare",
                                    "Energy","Consumer Defensive","Industrials"],
                                   default=[])
    
        df = pd.DataFrame()
        try:
            with st.spinner("Screening live data for your profile…"):
                df = fetch_stock_data(tuple(symbols), cache_key)
        except Exception as e:
            st.error(f"No recommendation data available: {e}.")
            st.stop()
    
        # Filter by risk
        if risk == "Conservative":
            rec = df[(df["Beta"] < 0.9) & (df["Signal"] == "BUY") & (df["AI_Score"] >= 58)]
        elif risk == "Moderate":
            rec = df[(df["Beta"] < 1.4) & (df["AI_Score"] >= 62) & (df["Signal"].isin(["BUY","HOLD"]))]
        else:
            rec = df[df["AI_Score"] >= 65]
    
        if sec_pref:
            filtered_sec = rec[rec["Sector"].isin(sec_pref)]
            rec = filtered_sec if not filtered_sec.empty else rec
    
        rec = rec.sort_values("AI_Score", ascending=False).head(10)
    
        st.markdown(f"### Top picks · **{risk}** · {horizon}")
        st.markdown(f"*{len(rec)} stocks match your criteria*")
    
        if rec.empty:
            st.info("No stocks match. Try relaxing your risk or sector filters.")
        else:
            for _, row in rec.iterrows():
                sc  = int(row["AI_Score"])
                sc_col = "#15803d" if sc >= 70 else "#854d0e" if sc >= 55 else "#dc2626"
                cc  = "#16a34a" if row["Chg%"] > 0 else "#dc2626"
                sig_badge = f'<span class="b-{row["Signal"].lower()}">{row["Signal"]}</span>'
                st.markdown(f"""
                <div class="rec-card">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                      <span style="font-weight:700;font-size:16px">{row['Symbol']}</span>
                      &nbsp;{sig_badge}&nbsp;
                      <span style="background:#eff6ff;color:#1d4ed8;padding:2px 7px;border-radius:4px;
                            font-size:11px;font-weight:500">{row['Sector']}</span>
                      <br>
                      <span style="font-size:12px;color:#64748b">
                        PE: {row['PE']} · RSI: {row['RSI']} · Beta: {row['Beta']} · Div: {row['Div%']:.1f}%
                      </span>
                    </div>
                    <div style="text-align:right">
                      <div style="font-weight:700;font-size:18px">{currency}{row['Price']:,.2f}</div>
                      <div style="color:{cc};font-weight:600">{row['Chg%']:+.2f}%</div>
                      <div style="color:{sc_col};font-size:22px;font-weight:700">
                        {sc}<span style="font-size:12px;color:#94a3b8">/100</span>
                      </div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════════════════════════════════════
    #  PAGE: AI CHATBOT
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Chatbot":
        st.markdown('<div class="sec-hdr">💬 AI Stock Analyst — OpenAI Powered</div>', unsafe_allow_html=True)
    
        openai_key = st.session_state.get("openai_key", "") or os.environ.get("OPENAI_API_KEY", "")
        
        if not openai_key:
            st.warning("Enter your OpenAI API key in the sidebar to use the chatbot (or set the OPENAI_API_KEY environment variable).")
            st.markdown("Get a key at [platform.openai.com](https://platform.openai.com)")
            st.stop()
    
        df = pd.DataFrame()
        rise, fall = pd.DataFrame(), pd.DataFrame()
        try:
            with st.spinner("Loading live context for OpenAI…"):
                df   = fetch_stock_data(tuple(symbols[:15]), cache_key)
                rise, fall = ai_prediction(df)
        except Exception:
            pass
    
        # Build context for OpenAI
        ctx = ""
        if not df.empty:
            top5      = df.nlargest(5, "AI_Score")[["Symbol","Price","Chg%","RSI","Signal","AI_Score"]].to_string(index=False)
            rise_syms = ", ".join(rise["Symbol"].head(4).tolist()) if not rise.empty else "none"
            fall_syms = ", ".join(fall["Symbol"].head(3).tolist()) if not fall.empty else "none"
            portfolio_syms = ", ".join(s.replace(".NS","") for s in st.session_state.portfolio)
            ctx = f"""
    LIVE MARKET DATA ({datetime.now().strftime('%Y-%m-%d %H:%M')}):
    Top AI-scored stocks:
    {top5}
    
    Predicted RISE tomorrow: {rise_syms}
    Predicted FALL tomorrow: {fall_syms}
    User's portfolio: {portfolio_syms}
    """
    
        system_prompt = f"""You are an expert AI stock analyst on the StockAI platform.
    
    {ctx}
    
    Capabilities: analyze stocks (technical + fundamental), predict short-term movements, explain ratios (PE/RSI/Beta/ROE), recommend stocks by risk profile, compare sectors, review portfolios.
    
    Rules:
    - Be concise, data-driven, specific. Use the live data above when relevant.
    - Use bullet points for lists.
    - Use ₹ for Indian stocks, $ for US stocks.
    - Always end with a brief disclaimer that this is educational, not financial advice.
    """
    
        # Display history
        for msg in st.session_state.chat_history:
            cls = "msg-user" if msg["role"] == "user" else "msg-bot"
            st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)
    
        st.markdown("---")
    
        # Quick prompts
        st.markdown("**Quick asks:**")
        q1, q2, q3, q4 = st.columns(4)
        quick_map = {
            "Which stocks rise tomorrow?": q1,
            "Analyze my portfolio":        q2,
            "Best IT stocks right now":    q3,
            "Explain RSI for beginners":   q4,
        }
        trigger = None
        for label, col in quick_map.items():
            if col.button(label, key=f"qk_{label[:8]}"):
                trigger = label
    
        user_input = st.chat_input("Ask about any stock, sector, or your portfolio…")
        if trigger:
            user_input = trigger
    
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.markdown(f'<div class="msg-user">{user_input}</div>', unsafe_allow_html=True)
    
            with st.spinner("GPT is analysing…"):
                try:
                    # Check for mentioned stock symbols in user query
                    mentioned_symbols = []
                    import re
                    for sym in symbols:
                        clean_sym = sym.replace(".NS", "")
                        if re.search(r'\b' + re.escape(clean_sym) + r'\b', user_input, re.IGNORECASE):
                            mentioned_symbols.append(sym)
                    
                    # Fetch live news, stock data, and social sentiment if stocks are mentioned
                    dynamic_context = ""
                    for sym in mentioned_symbols:
                        clean_sym = sym.replace(".NS", "")
                        
                        # Fetch live stock info
                        stock_info = fetch_single_stock_data(sym)
                        
                        dynamic_context += f"\nLATEST REAL-TIME DATA FOR {clean_sym}:\n"
                        if stock_info:
                            dynamic_context += (
                                f"Price: {currency}{stock_info['Price']:,.2f} | "
                                f"Daily Change: {stock_info['Chg%']:+.2f}% | "
                                f"RSI: {stock_info['RSI']} | "
                                f"PE: {stock_info['PE']} | "
                                f"Sector: {stock_info['Sector']} | "
                                f"AI Score: {stock_info['AI_Score']}/100\n"
                            )
                        
                        news_data = fetch_stock_news(clean_sym)
                        reddit_data = fetch_reddit_posts(clean_sym)
                        
                        if news_data:
                            dynamic_context += "PROFESSIONAL NEWS:\n"
                            for item in news_data[:3]:
                                dynamic_context += f"- {item['title']} (Publisher: {item['publisher']}). Summary: {item['summary']}\n"
                        if reddit_data:
                            dynamic_context += "REDDIT RETAIL DISCUSSION:\n"
                            for item in reddit_data[:3]:
                                dynamic_context += f"- {item['title']} (Author: {item['author']}). Post: {item['content']}\n"
                    
                    active_system_prompt = system_prompt
                    if dynamic_context:
                        active_system_prompt += f"\n\nUse this real-time news and retail social media sentiment data to formulate your answers for the mentioned stocks:\n{dynamic_context}"
                        active_system_prompt += "\nCorrelate any stock price movements or trends with actual events described in the news feeds (e.g., earnings results, product updates, regulatory updates) and retail sentiment from Reddit posts, explaining the 'why' behind stock price actions with high accuracy."
                    
                    from openai import OpenAI
                    client = OpenAI(api_key=openai_key)
                    
                    # Format conversation history for OpenAI:
                    messages = [{"role": "system", "content": active_system_prompt}]
                    for msg in st.session_state.chat_history[-12:]:
                        role = "assistant" if msg["role"] == "assistant" else "user"
                        messages.append({"role": role, "content": msg["content"]})
                    
                    import time
                    max_retries = 3
                    resp = None
                    for attempt in range(max_retries):
                        try:
                            resp = client.chat.completions.create(
                                model='gpt-4o-mini',
                                messages=messages,
                                max_tokens=1000,
                            )
                            break
                        except Exception as e:
                            if attempt == max_retries - 1:
                                raise e
                            time.sleep(1.5 * (attempt + 1))
                            
                    if resp is None:
                        raise Exception("Empty response from OpenAI")
                        
                    reply = resp.choices[0].message.content
                except Exception as e:
                    err_str = str(e)
                    if "503" in err_str or "rate limit" in err_str.lower() or "insufficient_quota" in err_str.lower():
                        reply = "⚠️ The OpenAI API is currently rate-limited or experiencing high demand. Please verify your billing/quota or try again in a few seconds."
                    else:
                        reply = f"❌ Error: {e}"
    
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.markdown(f'<div class="msg-bot">{reply}</div>', unsafe_allow_html=True)
            st.rerun()

# ─── Call the fragment ────────────────────────────────────────────────────────
render_live_dashboard()
