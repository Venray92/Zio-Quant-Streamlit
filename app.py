import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import warnings

warnings.filterwarnings('ignore')

# 1. Konfigurasi Halaman & Custom Theme Stabil
st.set_page_config(
    page_title="Zio - Quant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Global Background & Text */
    .stApp {
        background-color: #0B131D !important;
        color: #E2E8F0;
    }
    
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Box Watchlist dengan Tinggi Pas & Scroll Internal */
    .watchlist-box {
        height: 495px !important;
        overflow-y: auto !important;
        padding-right: 5px;
    }
    
    /* Header Ticker Card Sesuai Warna Logo */
    .ticker-header-card {
        background: linear-gradient(135deg, #121E2B 0%, #1A293B 100%);
        border: 1px solid #243447;
        border-left: 5px solid #00E676;
        padding: 4px 12px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 4px;
    }
    .ticker-header-text {
        color: #00E676;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin: 0;
    }

    /* Kustomisasi Button Streamlit (Tema Hijau Logo Zio) */
    div.stButton > button[kind="primary"] {
        background-color: #00E676 !important;
        color: #0B131D !important;
        border: none !important;
        font-weight: 700 !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #121E2B !important;
        color: #94A3B8 !important;
        border: 1px solid #243447 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00E676 !important;
        color: #00E676 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Daftar Saham IDX
SAHAM_LIST = sorted(list(set([
    "ISAT.JK", "ACES.JK", "ADHI.JK", "ADRO.JK", "AGRO.JK", "AALI.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK",
    "APLN.JK", "ARTO.JK", "ASII.JK", "ASRI.JK", "AUTO.JK", "AVIA.JK", "BBCA.JK", "BBHI.JK", "BBNI.JK", "BBRI.JK",
    "BBTN.JK", "BCIC.JK", "BDMN.JK", "BELI.JK", "BIRD.JK", "BJBR.JK", "BJTM.JK", "BMRI.JK", "BMTR.JK", "BNGA.JK",
    "BREN.JK", "BRIS.JK", "BRPT.JK", "BSDE.JK", "BUKA.JK", "BUMI.JK", "BYAN.JK", "CITA.JK", "CLEO.JK", "CMRY.JK",
    "CPIN.JK", "CTRA.JK", "CUAN.JK", "DCII.JK", "DEWA.JK", "DILD.JK", "DKFT.JK", "DOID.JK", "DRMA.JK", "DSNG.JK",
    "EAST.JK", "EDGE.JK", "ELSA.JK", "EMTK.JK", "ENRG.JK", "ESSA.JK", "EXCL.JK", "FILM.JK", "GEMS.JK", "GJTL.JK",
    "GOTO.JK", "HAIS.JK", "HEAL.JK", "HRUM.JK", "ICBP.JK", "INAF.JK", "INCO.JK", "INDF.JK", "INDY.JK", "INKP.JK",
    "INTP.JK", "IPCC.JK", "IPCM.JK", "IRRA.JK", "ITMG.JK", "JKON.JK", "JPFA.JK", "JSPT.JK", "KAEF.JK", "KEEN.JK",
    "KIJA.JK", "KLBF.JK", "LEAD.JK", "LSIP.JK", "MAIN.JK", "MAPA.JK", "MAPI.JK", "MBAP.JK", "MBMA.JK", "MCAS.JK",
    "MDKA.JK", "MEDC.JK", "MEDS.JK", "MIKA.JK", "MNCN.JK", "MPMX.JK", "MTDL.JK", "MYOR.JK", "NCKL.JK", "NELY.JK",
    "NRCA.JK", "PANI.JK", "PANR.JK", "PGAS.JK", "PGEO.JK", "PNBN.JK", "POWR.JK", "PRDA.JK", "PSAB.JK", "PSSI.JK",
    "PTBA.JK", "PTPP.JK", "PWON.JK", "RAAM.JK", "RALS.JK", "SAME.JK", "SCMA.JK", "SIDO.JK", "SILO.JK", "SMBR.JK",
    "SMDR.JK", "SMGR.JK", "SMRA.JK", "SMSM.JK", "SSIA.JK", "SSMS.JK", "STAA.JK", "TAPG.JK", "TBIG.JK", "TCPI.JK",
    "TINS.JK", "TKIM.JK", "TLKM.JK", "TMAS.JK", "TOBA.JK", "TOTL.JK", "TOWR.JK", "TPIA.JK", "TSPC.JK", "UNTR.JK",
    "UNVR.JK", "WEGE.JK", "WIFI.JK", "WIKA.JK", "WINS.JK", "WOOD.JK"
])))

# 3. Helper Fraksi Harga BEI
def get_tick_size(price):
    if price < 200:
        return 1
    elif price < 500:
        return 2
    elif price < 2000:
        return 5
    elif price < 5000:
        return 10
    else:
        return 25

def subtract_ticks(price, num_ticks):
    curr = price
    for _ in range(num_ticks):
        tick = get_tick_size(curr)
        curr -= tick
    return max(1, curr)

def add_ticks(price, num_ticks):
    curr = price
    for _ in range(num_ticks):
        tick = get_tick_size(curr)
        curr += tick
    return curr

# 4. Engine Screener
@st.cache_data(ttl=3600)
def run_screener(tickers):
    results_gc = []
    results_dc = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="90d", interval="1d", progress=False)
            if df.empty or len(df) < 30:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            c0 = float(df['Close'].iloc[-1])
            v0 = float(df['Volume'].iloc[-1])
            l0 = float(df['Low'].iloc[-1])
            h0 = float(df['High'].iloc[-1])
            val0 = c0 * v0

            if c0 <= 50 or val0 < 1_000_000_000:
                continue

            df['vol_ma20'] = df['Volume'].rolling(window=20).mean()
            vol_ma20_0 = float(df['vol_ma20'].iloc[-1])

            low_min10 = df['Low'].rolling(window=10).min()
            high_max10 = df['High'].rolling(window=10).max()
            fast_k = 100 * ((df['Close'] - low_min10) / (high_max10 - low_min10))
            df['stoch_k'] = fast_k.rolling(window=5).mean()
            df['stoch_d'] = df['stoch_k'].rolling(window=5).mean()

            try:
                psar_ind = ta.trend.PSARIndicator(high=df['High'], low=df['Low'], close=df['Close'], step=0.02, max_step=0.2)
                df['psar'] = psar_ind.psar()
            except:
                df['psar'] = df['Close']

            k0, d0 = float(df['stoch_k'].iloc[-1]), float(df['stoch_d'].iloc[-1])
            k1, d1 = float(df['stoch_k'].iloc[-2]), float(df['stoch_d'].iloc[-2])
            k2, d2 = float(df['stoch_k'].iloc[-3]), float(df['stoch_d'].iloc[-3])
            k3, d3 = float(df['stoch_k'].iloc[-4]), float(df['stoch_d'].iloc[-4])
            k4, d4 = float(df['stoch_k'].iloc[-5]), float(df['stoch_d'].iloc[-5])
            psar0 = float(df['psar'].iloc[-1])

            # Bullish Filter
            if k0 < 35:
                gc_today = (k1 < d1) and (k0 >= d0)
                gc_yesterday = (k2 < d2) and (k1 >= d1) and (k0 >= d0)
                gc_2days_ago = (k3 < d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                gc_3days_ago = (k4 < d4) and (k3 >= d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                is_almost_gc = (k0 <= d0) and ((d0 - k0) <= 3.0)

                stoch_signal = None
                if gc_today: stoch_signal = {"type": "GC Hari Ini", "score": 80}
                elif gc_yesterday: stoch_signal = {"type": "GC Kemarin", "score": 70}
                elif gc_2days_ago: stoch_signal = {"type": "GC 2H Lalu", "score": 70}
                elif gc_3days_ago: stoch_signal = {"type": "GC 3H Lalu", "score": 70}
                elif is_almost_gc: stoch_signal = {"type": "Early Signal", "score": 55}

                if stoch_signal:
                    score = stoch_signal["score"]
                    if psar0 < l0: score += 20
                    if v0 > vol_ma20_0: score += 10

                    results_gc.append({
                        "Ticker": ticker.replace(".JK", ""),
                        "Harga": int(c0),
                        "Score": score,
                        "Type": stoch_signal["type"]
                    })

            # Bearish Filter
            if k0 >= 75:
                dc_today = (k1 > d1) and (k0 <= d0)
                dc_yesterday = (k2 > d2) and (k1 <= d1) and (k0 <= d0)
                dc_2days_ago = (k3 > d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                dc_3days_ago = (k4 < d4) and (k3 >= d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                is_almost_dc = (k0 >= d0) and ((k0 - d0) <= 3.0)

                dc_signal = None
                if dc_today: dc_signal = {"type": "DC Hari Ini", "score": -80}
                elif dc_yesterday: dc_signal = {"type": "DC Kemarin", "score": -70}
                elif dc_2days_ago: dc_signal = {"type": "DC 2H Lalu", "score": -70}
                elif dc_3days_ago: dc_signal = {"type": "DC 3H Lalu", "score": -70}
                elif is_almost_dc: dc_signal = {"type": "Early DC", "score": -55}

                if dc_signal:
                    score = dc_signal["score"]
                    if psar0 > h0: score -= 20
                    if v0 > vol_ma20_0: score -= 10

                    results_dc.append({
                        "Ticker": ticker.replace(".JK", ""),
                        "Harga": int(c0),
                        "Score": score,
                        "Type": dc_signal["type"]
                    })
        except Exception:
            continue

    df_gc = pd.DataFrame(results_gc)
    df_dc = pd.DataFrame(results_dc)

    if not df_gc.empty:
        df_gc = df_gc.sort_values(by="Score", ascending=False).reset_index(drop=True)
    if not df_dc.empty:
        df_dc = df_dc.sort_values(by="Score", ascending=True).reset_index(drop=True)

    return df_gc, df_dc

# 5. Fetch Analisis Historis Saham & Rule Trade Plan
@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {
            "is_ihsg": True, "price": "-", "plan_type": "-", "is_breakdown": False,
            "buy_range": "-", "sl_price": "-", "tp1": "-", "tp2": "-",
            "risk_pct": "-", "reward_pct": "-", "rr_ratio": "-", "max_allowed_risk": "-",
            "vol_spike": False, "entry_worst": 0
        }

    try:
        yf_symbol = f"{symbol.replace('IDX:', '')}.JK"
        df = yf.download(yf_symbol, period="120d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        c0 = float(df['Close'].iloc[-1])
        o0 = float(df['Open'].iloc[-1])
        h0 = float(df['High'].iloc[-1])
        l0 = float(df['Low'].iloc[-1])
        v0 = float(df['Volume'].iloc[-1])

        swing_low_60 = float(df['Low'].tail(60).min())
        swing_high_60 = float(df['High'].tail(60).max())
        swing_high_120 = float(df['High'].max())
        vol_ma20 = float(df['Volume'].tail(20).mean())

        is_marubozu_red = (c0 < o0) and ((o0 - c0) / (h0 - l0 + 1e-5) > 0.85) and ((c0 - l0) / (h0 - l0 + 1e-5) < 0.05)
        is_new_low = c0 <= (swing_low_60 * 1.005)
        is_breakdown = is_marubozu_red or is_new_low

        range_span = max(1.0, swing_high_60 - swing_low_60)
        pos_ratio = (c0 - swing_low_60) / range_span

        lh_terdekat = float(df['High'].tail(20).iloc[:-2].max()) if len(df) >= 22 else swing_high_60

        if pos_ratio < 0.50:
            plan_type = "BOW"
            buy_range_low = swing_low_60
            buy_range_high = min(c0, float(df['Low'].tail(5).mean()))
            sl_price = subtract_ticks(swing_low_60, 3)
            tp1 = lh_terdekat
            tp2 = swing_high_60
            max_allowed_risk = 8.0
        else:
            plan_type = "BOB"
            buy_range_low = c0
            buy_range_high = add_ticks(c0, 3)
            sl_price = subtract_ticks(lh_terdekat, 3) if lh_terdekat < c0 else subtract_ticks(c0, 3)
            tp1 = c0 + (swing_high_60 - swing_low_60)
            tp2 = swing_high_120
            max_allowed_risk = 5.0

        entry_worst = buy_range_high
        risk_pct = round(((entry_worst - sl_price) / entry_worst) * 100, 2)
        reward_pct = round(((tp1 - entry_worst) / entry_worst) * 100, 2)
        rr_ratio = round(reward_pct / risk_pct, 2) if risk_pct > 0 else 0

        vol_spike = (v0 >= vol_ma20)

        return {
            "is_ihsg": False,
            "price": f"Rp {int(c0):,}",
            "plan_type": plan_type,
            "is_breakdown": is_breakdown,
            "buy_range": f"Rp {int(buy_range_low):,} - Rp {int(buy_range_high):,}",
            "sl_price": f"Rp {int(sl_price):,}",
            "tp1": f"Rp {int(tp1):,}",
            "tp2": f"Rp {int(tp2):,}",
            "risk_pct": f"{risk_pct}%",
            "reward_pct": f"{reward_pct}%",
            "rr_ratio": rr_ratio,
            "max_allowed_risk": max_allowed_risk,
            "vol_spike": vol_spike,
            "entry_worst": entry_worst,
            "raw_risk_pct": risk_pct
        }
    except Exception:
        return {
            "is_ihsg": False, "price": "-", "plan_type": "-", "is_breakdown": False,
            "buy_range": "-", "sl_price": "-", "tp1": "-", "tp2": "-",
            "risk_pct": "-", "reward_pct": "-", "rr_ratio": "-", "max_allowed_risk": "-",
            "vol_spike": False, "entry_worst": 0, "raw_risk_pct": 0
        }

@st.cache_data(ttl=600)
def get_ihsg_data():
    try:
        ihsg_df = yf.download("^JKSE", period="5d", interval="1d", progress=False)
        if isinstance(ihsg_df.columns, pd.MultiIndex):
            ihsg_df.columns = ihsg_df.columns.get_level_values(0)
        c_now = float(ihsg_df['Close'].iloc[-1])
        c_prev = float(ihsg_df['Close'].iloc[-2])
        change_pct = ((c_now - c_prev) / c_prev) * 100
        return c_now, change_pct
    except:
        return 7000.0, 0.0

# 6. Header Bar (Rapat & Ringkas)
col_logo, col_title, col_space, col_menu = st.columns([0.3, 2.2, 4.2, 2.3])

with col_logo:
    st.markdown("<h3 style='margin:0; padding-top:0px; color: #00E676;'>Z</h3>", unsafe_allow_html=True)

with col_title:
    st.markdown("<h3 style='margin:0; padding-top:2px; font-size: 17px; color: #E2E8F0; font-weight: 700;'>Zio - Quant</h3>", unsafe_allow_html=True)

with col_menu:
    selected_screener = st.selectbox(
        "Pilih Screener",
        ["-- Pilih Screener --", "Stoch - Psar"],
        index=1,
        label_visibility="collapsed"
    )

st.markdown("<hr style='margin-top: 2px; margin-bottom: 6px; border-color: #1E2D3D;'>", unsafe_allow_html=True)

# Session States Initialization
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "IDX:COMPOSITE"

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "chart"

if 'watchlist_tab' not in st.session_state:
    st.session_state.watchlist_tab = "bull"

# 7. Layout Utama
col_left, col_right = st.columns([1, 2.2], gap="medium")

# --- KIRI: WATCHLIST & SCREENER ---
with col_left:
    st.markdown("<p style='font-size: 11px; color: #64748B; margin-bottom: 4px; font-weight: 600; letter-spacing: 0.5px;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊  **IHSG**  |  {ihsg_price:,.2f}  ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
        st.session_state.active_ticker = "IDX:COMPOSITE"
        st.rerun()

    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)

    if selected_screener == "Stoch - Psar":
        st.markdown("<p style='font-size: 12px; color: #00E676; font-weight: bold; margin-bottom: 4px;'>Screener</p>", unsafe_allow_html=True)
        
        with st.spinner("Memindai pasar..."):
            df_bull, df_bear = run_screener(SAHAM_LIST)
            
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🟢 Bullish", use_container_width=True, type="primary" if st.session_state.watchlist_tab == "bull" else "secondary"):
                st.session_state.watchlist_tab = "bull"
                st.rerun()
        with btn_c2:
            if st.button("🔴 Bearish", use_container_width=True, type="primary" if st.session_state.watchlist_tab == "bear" else "secondary"):
                st.session_state.watchlist_tab = "bear"
                st.rerun()

        st.markdown("<div class='watchlist-box'>", unsafe_allow_html=True)
        if st.session_state.watchlist_tab == "bull":
            if not df_bull.empty:
                for index, row in df_bull.iterrows():
                    t_code = row["Ticker"]
                    t_price = row["Harga"]
                    t_type = row["Type"]
                    if st.button(f"🔹 **{t_code}** | {t_price:,} | *{t_type}*", key=f"bull_{t_code}", use_container_width=True):
                        st.session_state.active_ticker = f"IDX:{t_code}"
                        st.rerun()
            else:
                st.info("Tidak ada saham Bullish.")
        else:
            if not df_bear.empty:
                for index, row in df_bear.iterrows():
                    t_code = row["Ticker"]
                    t_price = row["Harga"]
                    t_type = row["Type"]
                    if st.button(f"🔻 **{t_code}** | {t_price:,} | *{t_type}*", key=f"bear_{t_code}", use_container_width=True):
                        st.session_state.active_ticker = f"IDX:{t_code}"
                        st.rerun()
            else:
                st.info("Tidak ada saham Bearish.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size: 12px; color: #64748B; font-style: italic;'>Pilih menu **Stoch - Psar** di kanan atas untuk menampilkan hasil screening.</p>", unsafe_allow_html=True)

# --- KANAN: DISPLAY CHART / TRADE PLAN ---
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "IHSG" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol.replace("IDX:", "")
    tv_symbol = "IDX:COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol

    # Custom Header Ticker & Switcher
    c_title, c_b1, c_b2 = st.columns([2.5, 1, 1])
    with c_title:
        st.markdown(f"""
            <div class="ticker-header-card">
                <p class="ticker-header-text">Ticker : {clean_ticker}</p>
            </div>
        """, unsafe_allow_html=True)
    with c_b1:
        if st.button("📈 Chart", use_container_width=True, type="primary" if st.session_state.view_mode == "chart" else "secondary"):
            st.session_state.view_mode = "chart"
            st.rerun()
    with c_b2:
        if st.button("📋 Trade Plan", use_container_width=True, type="primary" if st.session_state.view_mode == "trade_plan" else "secondary"):
            st.session_state.view_mode = "trade_plan"
            st.rerun()

    st.markdown("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)

    # VIEW 1: CHART TRADINGVIEW (Tinggi disesuaikan 500px)
    if st.session_state.view_mode == "chart":
        tradingview_html = f"""
        <div class="tradingview-widget-container" style="height:495px;width:100%">
          <div id="tradingview_widget" style="height:100%;width:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
            "autosize": true,
            "symbol": "{tv_symbol}",
            "interval": "D",
            "timezone": "Asia/Jakarta",
            "theme": "dark",
            "style": "1",
            "locale": "id",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "hide_side_toolbar": false,
            "details": false,
            "hotlist": false,
            "calendar": false,
            "container_id": "tradingview_widget"
          }});
          </script>
        </div>
        """
        st.components.v1.html(tradingview_html, height=500)

    # VIEW 2: TRADE PLAN ATURAN MUTLAK
    elif st.session_state.view_mode == "trade_plan":
        tp = get_stock_trade_plan(active_symbol)
        
        st.markdown(f"#### 📋 Modul Trade Plan — `{clean_ticker}`")
        
        if tp["is_ihsg"]:
            st.info("ℹ️ **Indeks IHSG (Composite)** tidak memiliki Trade Plan individual. Silakan pilih salah satu saham dari watchlist sebelah kiri.")
            
            col_tp1, col_tp2, col_tp3 = st.columns(3)
            with col_tp1:
                st.metric("Strategi Plan", "-")
                st.metric("Area Beli (Buy Range)", "-")
                st.metric("Risk (%)", "-")

            with col_tp2:
                st.metric("Stop Loss", "-")
                st.metric("Target Profit 1 (TP1)", "-")
                st.metric("Reward (%)", "-")

            with col_tp3:
                st.metric("Target Profit 2 (TP2)", "-")
                st.metric("Risk to Reward Ratio", "-")
                st.metric("Status Feasibility", "-")
        else:
            if tp["is_breakdown"]:
                st.error("⛔ **RULE PENOLAKAN SYSTEM:** Saham Breakdown Support (Candle Marubozu Merah / New Low 2 Bulan). Status: **SKIP / WAIT AND SEE** sampai membentuk Swing Low baru.")
            
            is_rr_valid = (isinstance(tp["rr_ratio"], (int, float)) and tp["rr_ratio"] >= 2.0)
            is_risk_valid = (isinstance(tp["raw_risk_pct"], (int, float)) and tp["raw_risk_pct"] <= tp["max_allowed_risk"])

            if not is_rr_valid:
                st.warning("⚠️ **TIDAK SESUAI R:R (SKIP):** Risk to Reward kurang dari 1 : 2.")
            if not is_risk_valid:
                st.warning(f"⚠️ **RISK OVER LIMIT:** Toleransi Risiko ({tp['risk_pct']}) melebihi batas maksimal {tp['plan_type']} ({tp['max_allowed_risk']}%).")

            col_tp1, col_tp2, col_tp3 = st.columns(3)
            with col_tp1:
                st.metric("Strategi Plan", tp["plan_type"])
                st.metric("Area Beli (Buy Range)", tp["buy_range"])
                st.metric("Risk (%)", tp["risk_pct"])

            with col_tp2:
                st.metric("Stop Loss (3 Ticks Low)", tp["sl_price"])
                st.metric("Target Profit 1 (TP1)", tp["tp1"])
                st.metric("Reward (%)", tp["reward_pct"])

            with col_tp3:
                st.metric("Target Profit 2 (TP2)", tp["tp2"])
                st.metric("Risk to Reward Ratio", f"1 : {tp['rr_ratio']}" if tp["rr_ratio"] != "-" else "-")
                st.metric("Status Feasibility", "PASS (VALID)" if (is_rr_valid and is_risk_valid and not tp['is_breakdown']) else "REJECT (SKIP)")

            st.markdown("---")
            
            if tp["plan_type"] == "BOW":
                st.info("💡 **Manajemen Porsi BOW:** Entry 50% porsi di area support. Tambah 50% porsi saat konfirmasi CHoCH Bullish (Daily Close di atas LH terdekat).")
            else:
                st.info("💡 **Manajemen Porsi BOB:** Syarat trigger Candle Close di atas LH terdekat + Volume Spike. Max chasing +1 s.d. +3 ticks dari breakout point.")

            st.markdown("##### 💵 Simulasi Alokasi Modal Trading")
            modal = st.number_input("Masukkan Total Capital / Modal (Rp):", min_value=1_000_000, value=10_000_000, step=1_000_000)
            
            entry_price = tp["entry_worst"]
            if entry_price > 0:
                total_lot = int(modal // (entry_price * 100))
                total_buy = total_lot * entry_price * 100
                sl_val = int(tp["sl_price"].replace("Rp ", "").replace(",", "")) if isinstance(tp["sl_price"], str) else 0
                tp1_val = int(tp["tp1"].replace("Rp ", "").replace(",", "")) if isinstance(tp["tp1"], str) else 0
                max_loss_rp = total_lot * 100 * (entry_price - sl_val)
                max_gain_rp = total_lot * 100 * (tp1_val - entry_price)

                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.info(f"**Maksimal Pembelian:**\n\n**{total_lot} Lot** (Rp {int(total_buy):,})")
                c_m2.error(f"**Maksimal Risiko (Loss SL):**\n\n- Rp {int(max_loss_rp):,}")
                c_m3.success(f"**Potensi Profit (TP1):**\n\n+ Rp {int(max_gain_rp):,}")
