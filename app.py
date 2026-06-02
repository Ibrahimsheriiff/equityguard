import streamlit as st
import yfinance as yf
import re
from agent import run_agent

st.set_page_config(page_title="EquityGuard", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #080c18; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 2rem 2rem; max-width: 1100px; margin: auto; }
#MainMenu, footer { visibility: hidden; }

.hero { text-align: center; padding: 2.5rem 0 1.5rem; }
.hero h1 { font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #00d4aa, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
.hero p { color: #5a6a80; font-size: 0.85rem; letter-spacing: 0.1em; margin-top: 0.4rem; }

.search-wrap { max-width: 480px; margin: 0 auto 1.5rem auto; }
[data-testid="stTextInput"] input {
    background: #0f1626 !important;
    border: 1px solid #1a2540 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.2rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #00d4aa !important;
    box-shadow: 0 0 0 2px rgba(0,212,170,0.12) !important;
}

.stock-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; margin: 0.5rem 0 1.5rem; }
.stock-card { background: #0f1626; border: 1px solid #1a2540; border-radius: 12px; padding: 1rem; text-align: left; }
.stock-card.selected { border-color: #00d4aa; background: #0a1e1a; box-shadow: 0 0 0 1px #00d4aa; }
.stock-ticker { font-size: 1rem; font-weight: 700; color: #e2e8f0; }
.stock-name { font-size: 0.7rem; color: #5a6a80; margin: 0.2rem 0; }
.stock-price { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-top: 0.4rem; }
.chg-pos { font-size: 0.8rem; color: #00d4aa; }
.chg-neg { font-size: 0.8rem; color: #ff4d6a; }

/* Run agent button */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #00d4aa 0%, #0099ff 100%) !important;
    color: #080c18 !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2.5rem !important;
    width: 100% !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 24px rgba(0,212,170,0.25) !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] button:hover {
    box-shadow: 0 6px 32px rgba(0,212,170,0.4) !important;
    transform: translateY(-1px) !important;
}

.section-title { font-size: 0.72rem; color: #5a6a80; letter-spacing: 0.1em; text-transform: uppercase; margin: 1.2rem 0 0.6rem; }

.score-header { display: flex; align-items: center; gap: 2rem; background: #0f1626; border: 1px solid #1a2540; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1rem; }
.score-ring { width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 900; flex-shrink: 0; }
.ring-low    { border: 5px solid #00d4aa; color: #00d4aa; background: #061a14; }
.ring-medium { border: 5px solid #f5a623; color: #f5a623; background: #1a1206; }
.ring-high   { border: 5px solid #ff4d6a; color: #ff4d6a; background: #1a0610; }

.badge { display: inline-block; padding: 0.3rem 1rem; border-radius: 999px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; }
.badge-low    { background: #061a14; color: #00d4aa; border: 1px solid #00d4aa; }
.badge-medium { background: #1a1206; color: #f5a623; border: 1px solid #f5a623; }
.badge-high   { background: #1a0610; color: #ff4d6a; border: 1px solid #ff4d6a; }

.signals-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin: 1rem 0; }
.signal-box { background: #0f1626; border: 1px solid #1a2540; border-radius: 12px; padding: 1rem; }
.signal-label { font-size: 0.7rem; color: #5a6a80; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.3rem; }
.signal-val { font-size: 0.9rem; font-weight: 600; color: #e2e8f0; }
.sig-bad  { color: #ff4d6a; }
.sig-warn { color: #f5a623; }
.sig-good { color: #00d4aa; }

.reasoning-box { background: #0f1626; border: 1px solid #1a2540; border-radius: 16px; padding: 1.5rem 2rem; color: #a0aec0; line-height: 1.9; font-size: 0.93rem; }
.reasoning-box h2, .reasoning-box h3 { color: #00d4aa; font-size: 1rem; margin-top: 1.2rem; }
.reasoning-box strong { color: #e2e8f0; }
.reasoning-box td, .reasoning-box th { padding: 0.5rem 0.75rem; border-bottom: 1px solid #1a2540; font-size: 0.88rem; }
.reasoning-box th { color: #5a6a80; }
</style>
""", unsafe_allow_html=True)

WATCHLIST = [
    {"ticker": "CBA.AX", "name": "Commonwealth Bank"},
    {"ticker": "BHP.AX", "name": "BHP Group"},
    {"ticker": "NAB.AX", "name": "National Aust. Bank"},
    {"ticker": "WBC.AX", "name": "Westpac Banking"},
    {"ticker": "ANZ.AX", "name": "ANZ Group"},
    {"ticker": "AAPL",   "name": "Apple Inc."},
    {"ticker": "NVDA",   "name": "NVIDIA"},
    {"ticker": "TSLA",   "name": "Tesla"},
    {"ticker": "MSFT",   "name": "Microsoft"},
    {"ticker": "GOOGL",  "name": "Alphabet"},
]

@st.cache_data(ttl=60)
def fetch_price(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev  = info.get("previousClose", price)
        chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
        return {"price": round(price, 2), "change": chg}
    except:
        return {"price": 0, "change": 0}

# ── HERO ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🛡️ EquityGuard</h1>
    <p>AI RISK ASSESSMENT · CUSTOM ReAct AGENT · LIVE MARKET DATA</p>
</div>
""", unsafe_allow_html=True)

# ── SEARCH ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Search any stock</div>', unsafe_allow_html=True)
st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
search = st.text_input("", placeholder="Type any ticker e.g. WES.AX, AMZN, META...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if search:
    search_ticker = search.strip().upper()
    data = fetch_price(search_ticker)
    if data["price"] > 0:
        chg_class = "chg-pos" if data["change"] >= 0 else "chg-neg"
        chg_sign  = "+" if data["change"] >= 0 else ""
        is_sel    = st.session_state.get("selected") == search_ticker
        card_cls  = "stock-card selected" if is_sel else "stock-card"
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"""
            <div class="{card_cls}" style="margin-bottom:0.5rem">
                <div class="stock-ticker">{search_ticker}</div>
                <div class="stock-price">${data['price']}</div>
                <div class="{chg_class}">{chg_sign}{data['change']}%</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {search_ticker}", key="search_select"):
                st.session_state.selected = search_ticker
                st.session_state.result = None
                st.rerun()
    else:
        st.warning(f"Could not find data for `{search_ticker}`. Check the ticker symbol.")

# ── WATCHLIST GRID ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Watchlist — ASX & US markets</div>', unsafe_allow_html=True)

if "selected" not in st.session_state:
    st.session_state.selected = None

cols = st.columns(5)
for i, stock in enumerate(WATCHLIST):
    data = fetch_price(stock["ticker"])
    chg_class = "chg-pos" if data["change"] >= 0 else "chg-neg"
    chg_sign  = "+" if data["change"] >= 0 else ""
    is_sel    = st.session_state.selected == stock["ticker"]
    card_cls  = "stock-card selected" if is_sel else "stock-card"

    with cols[i % 5]:
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="stock-ticker">{stock['ticker']}</div>
            <div class="stock-name">{stock['name']}</div>
            <div class="stock-price">${data['price']}</div>
            <div class="{chg_class}">{chg_sign}{data['change']}%</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select", key=f"btn_{stock['ticker']}"):
            st.session_state.selected = stock["ticker"]
            st.session_state.result = None
            st.rerun()

# ── RUN AGENT BUTTON ───────────────────────────────────────────────────────
if st.session_state.get("selected"):
    ticker = st.session_state.selected
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:0.75rem;">
            <span style="color:#5a6a80; font-size:0.82rem;">Ready to assess</span>
            <span style="color:#00d4aa; font-weight:700; font-size:1rem;"> {ticker}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔍  Run Agent — Assess {ticker}", type="primary"):
            with st.spinner(f"Agent investigating {ticker}..."):
                result = run_agent(f"Assess the current risk level of {ticker}", verbose=False)
                st.session_state.result = result
else:
    st.markdown("""
    <div style="text-align:center; color:#2a3a52; font-size:0.9rem; margin:1.5rem 0;">
        Select a stock above or search any ticker to begin
    </div>
    """, unsafe_allow_html=True)

# ── RESULTS ────────────────────────────────────────────────────────────────
if st.session_state.get("result"):
    result = st.session_state.result
    ticker = st.session_state.selected

    score = 5
    m = re.search(r'(\d+)/10', result)
    if m:
        score = int(m.group(1))
    risk_level = "low" if score <= 3 else "high" if score >= 7 else "medium"
    risk_label = {"low": "LOW RISK", "medium": "MEDIUM RISK", "high": "HIGH RISK"}[risk_level]

    def extract(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip()[:70] if m else "—"

    def sig_class(txt):
        t = txt.lower()
        if any(w in t for w in ["high","elevated","negative","overbought","red","bearish","bad"]): return "sig-bad"
        if any(w in t for w in ["low","good","positive","bullish","green","unknown"]): return "sig-good"
        return "sig-warn"

    vol_val  = extract(r'[Vv]olatility[:\*⚠️✅🔴🟡]+\s*(.+?)(?:\n|$)', result)
    tech_val = extract(r'[Tt]echnical[:\*⚠️✅🔴🟡]+\s*(.+?)(?:\n|$)', result)
    news_val = extract(r'[Nn]ews[:\*⚠️✅🔴🟡]+\s*(.+?)(?:\n|$)', result)
    earn_val = extract(r'[Ee]arnings[:\*⚠️✅🔴🟡]+\s*(.+?)(?:\n|$)', result)

    import datetime
    now = datetime.datetime.now().strftime('%d %b %Y %H:%M')

    st.markdown('<div class="section-title">Risk assessment result</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-header">
        <div class="score-ring ring-{risk_level}">{score}/10</div>
        <div>
            <div style="font-size:1.5rem;font-weight:800;color:#e2e8f0;margin-bottom:0.5rem">{ticker}</div>
            <span class="badge badge-{risk_level}">{risk_label}</span>
            <div style="color:#5a6a80;font-size:0.8rem;margin-top:0.6rem">Live assessment · Custom ReAct agent · {now}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Signal summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="signals-row">
        <div class="signal-box">
            <div class="signal-label">Volatility</div>
            <div class="signal-val {sig_class(vol_val)}">{vol_val}</div>
        </div>
        <div class="signal-box">
            <div class="signal-label">Technical</div>
            <div class="signal-val {sig_class(tech_val)}">{tech_val}</div>
        </div>
        <div class="signal-box">
            <div class="signal-label">News</div>
            <div class="signal-val {sig_class(news_val)}">{news_val}</div>
        </div>
        <div class="signal-box">
            <div class="signal-label">Earnings</div>
            <div class="signal-val {sig_class(earn_val)}">{earn_val}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Agent reasoning</div>', unsafe_allow_html=True)
    st.markdown('<div class="reasoning-box">', unsafe_allow_html=True)
    st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin-top:3rem;color:#1e2d45;font-size:0.78rem;">
    EquityGuard · Claude API · yfinance · Streamlit · Custom ReAct Agent
</div>
""", unsafe_allow_html=True)