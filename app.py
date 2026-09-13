import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import warnings

warnings.filterwarnings('ignore')

# 1. Konfigurasi Halaman & Custom Theme
st.set_page_config(
    page_title="Zio - Quant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
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

# 2. Inisialisasi Session State
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "IDX:COMPOSITE"

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "chart"

if 'watchlist_tab' not in st.session_state:
    st.session_state.watchlist_tab = "bull"

if 'screener_choice' not in st.session_state:
    st.session_state.screener_choice = "-- Pilih Screener --"

# 3. Daftar Saham IDX
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

# 4. Helper Fraksi Harga BEI Sesuai Aturan Mutlak
def get_tick_size(price):
    if price < 200: return 1
    elif price < 500: return 2
    elif price < 2000: return 5
    elif price < 5000: return 10
    else: return 25

def subtract_ticks(price, num_ticks):
    curr = price
    for _ in range(num_ticks):
        curr -= get_tick_size(curr)
    return max(1, curr)

def add_ticks(price, num_ticks):
    curr = price
    for _ in range(num_ticks):
        curr += get_tick_size(curr)
    return curr

# 5. Engine Screener
@st.cache_data(ttl=3600)
def run_screener(tickers):
    results_gc = []
    results_dc = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="90d", interval="1d", progress=False)
            if df.empty or len(df) < 30: continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            c0 = float(df['Close'].iloc[-1])
            c1 = float(df['Close'].iloc[-2])
            chg_pct = ((c0 - c1) / c1) * 100
            v0 = float(df['Volume'].iloc[-1])
            l0 = float(df['Low'].iloc[-1])
            h0 = float(df['High'].iloc[-1])
            val0 = c0 * v0

            if c0 <= 50 or val0 < 1_000_000_000: continue

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

            if k0 < 35:
                gc_today = (k1 < d1) and (k0 >= d0)
                gc_yesterday = (k2 < d2) and (k1 >= d1) and (k0 >= d0)
                gc_2days_ago = (k3 < d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                gc_3days_ago = (k4 < d4) and (k3 >= d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                is_almost_gc = (k0 <= d0) and ((d0 - k0) <= 3.0)

                stoch_signal = None
                if gc_today: stoch_signal = {"type": "GC", "score": 80}
                elif gc_yesterday: stoch_signal = {"type": "GC Kemarin", "score": 70}
                elif gc_2days_ago: stoch_signal = {"type": "GC 2H Lalu", "score": 70}
                elif gc_3days_ago: stoch_signal = {"type": "GC 3H Lalu", "score": 70}
                elif is_almost_gc: stoch_signal = {"type": "Early Signal", "score": 55}

                if stoch_signal:
                    score = stoch_signal["score"]
                    desc_list = [stoch_signal["type"]]
                    if psar0 < l0: score += 20
                    if v0 > vol_ma20_0: 
                        score += 10
                        desc_list.append("Vol Spike")
                    
                    results_gc.append({
                        "Ticker": ticker.replace(".JK", ""), 
                        "Harga": int(c0), 
                        "Chg": chg_pct,
                        "Score": score, 
                        "Type": " + ".join(desc_list)
                    })

            if k0 >= 75:
                dc_today = (k1 > d1) and (k0 <= d0)
                dc_yesterday = (k2 > d2) and (k1 <= d1) and (k0 <= d0)
                dc_2days_ago = (k3 > d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                dc_3days_ago = (k4 < d4) and (k3 >= d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                is_almost_dc = (k0 >= d0) and ((k0 - d0) <= 3.0)

                dc_signal = None
                if dc_today: dc_signal = {"type": "DC", "score": -80}
                elif dc_yesterday: dc_signal = {"type": "DC Kemarin", "score": -70}
                elif dc_2days_ago: dc_signal = {"type": "DC 2H Lalu", "score": -70}
                elif dc_3days_ago: dc_signal = {"type": "DC 3H Lalu", "score": -70}
                elif is_almost_dc: dc_signal = {"type": "Early DC", "score": -55}

                if dc_signal:
                    score = dc_signal["score"]
                    desc_list = [dc_signal["type"]]
                    if psar0 > h0: score -= 20
                    if v0 > vol_ma20_0: 
                        score -= 10
                        desc_list.append("Vol Spike")
                    
                    results_dc.append({
                        "Ticker": ticker.replace(".JK", ""), 
                        "Harga": int(c0), 
                        "Chg": chg_pct,
                        "Score": score, 
                        "Type": " + ".join(desc_list)
                    })
        except Exception:
            continue

    df_gc = pd.DataFrame(results_gc)
    df_dc = pd.DataFrame(results_dc)
    if not df_gc.empty: df_gc = df_gc.sort_values(by="Score", ascending=False).reset_index(drop=True)
    if not df_dc.empty: df_dc = df_dc.sort_values(by="Score", ascending=True).reset_index(drop=True)
    return df_gc, df_dc

# 6. Trade Plan Engine Berdasarkan Kedekatan Swing Low vs Swing High
@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {
            "is_ihsg": True, "price": "-", "plan_type": "-", "is_breakdown": False,
            "buy_range": "-", "sl_price": "-", "tp1": "-", "tp2": "-", "tp3": "-",
            "risk_pct": "-", "reward_pct_1": "-", "reward_pct_2": "-", "reward_pct_3": "-",
            "rr_1": 0, "rr_2": 0, "rr_3": 0, "max_allowed_risk": 0,
            "vol_spike": False, "entry_worst": 0, "technical_score": 50
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

        swing_low = float(df['Low'].tail(60).min())
        swing_high_60 = float(df['High'].tail(60).max())
        swing_high_120 = float(df['High'].max())

        # Ambil daftar swing high di atas harga sekarang secara berurutan untuk TP1, TP2, TP3
        unique_highs = sorted(list(set(df['High'].tail(60))))
        tp_candidates = [h for h in unique_highs if h > c0]
        
        if len(tp_candidates) >= 3:
            tp1, tp2, tp3 = tp_candidates[0], tp_candidates[1], tp_candidates[2]
        elif len(tp_candidates) == 2:
            tp1, tp2, tp3 = tp_candidates[0], tp_candidates[1], swing_high_120
        elif len(tp_candidates) == 1:
            tp1, tp2, tp3 = tp_candidates[0], swing_high_60, swing_high_120
        else:
            tp1, tp2, tp3 = swing_high_60, swing_high_120, swing_high_120 * 1.05

        # Rule Penolakan: Breakdown Support
        is_marubozu_red = (c0 < o0) and ((o0 - c0) / (h0 - l0 + 1e-5) > 0.85) and ((c0 - l0) / (h0 - l0 + 1e-5) < 0.05)
        is_new_low = c0 <= (swing_low * 1.005)
        is_breakdown = is_marubozu_red or is_new_low

        # Perbandingan jarak harga close ke swing low vs swing high terdekat (TP1)
        dist_to_low = c0 - swing_low
        dist_to_high = tp1 - c0

        # Penentuan Tipe Beli (BOW atau BOB) berdasarkan kedekatan
        if dist_to_low <= dist_to_high:
            plan_type = "BUY ON WEAKNESS (BOW)"
            buy_range_low = swing_low
            buy_range_high = min(c0, float(df['Low'].tail(5).mean()))
            sl_price = subtract_ticks(swing_low, 3) # 2-3 tick di bawah swing low
            max_allowed_risk = 8.0
        else:
            plan_type = "BUY ON BREAKOUT (BOB)"
            buy_range_low = c0
            buy_range_high = add_ticks(c0, 3) # Maksimal chasing 1-3 tick
            sl_price = subtract_ticks(tp1, 3) if tp1 > c0 else subtract_ticks(c0, 3)
            max_allowed_risk = 5.0

        entry_worst = buy_range_high
        risk_pct = round(((entry_worst - sl_price) / entry_worst) * 100, 2)
        
        reward_pct_1 = round(((tp1 - entry_worst) / entry_worst) * 100, 2)
        reward_pct_2 = round(((tp2 - entry_worst) / entry_worst) * 100, 2)
        reward_pct_3 = round(((tp3 - entry_worst) / entry_worst) * 100, 2)

        rr_1 = round(reward_pct_1 / risk_pct, 1) if risk_pct > 0 else 0
        rr_2 = round(reward_pct_2 / risk_pct, 1) if risk_pct > 0 else 0
        rr_3 = round(reward_pct_3 / risk_pct, 1) if risk_pct > 0 else 0

        vol_ma20 = float(df['Volume'].tail(20).mean())

        return {
            "is_ihsg": False,
            "price": f"Rp {int(c0):,}",
            "plan_type": plan_type,
            "is_breakdown": is_breakdown,
            "buy_range": f"Rp {int(buy_range_low):,} – Rp {int(buy_range_high):,}",
            "sl_price": f"Rp {int(sl_price):,}",
            "tp1": f"Rp {int(tp1):,}",
            "tp2": f"Rp {int(tp2):,}",
            "tp3": f"Rp {int(tp3):,}",
            "risk_pct": f"{risk_pct}%",
            "reward_pct_1": f"{reward_pct_1}%",
            "reward_pct_2": f"{reward_pct_2}%",
            "reward_pct_3": f"{reward_pct_3}%",
            "rr_1": rr_1,
            "rr_2": rr_2,
            "rr_3": rr_3,
            "max_allowed_risk": max_allowed_risk,
            "vol_spike": (v0 >= vol_ma20),
            "entry_worst": entry_worst,
            "raw_risk_pct": risk_pct,
            "technical_score": 85 if not is_breakdown else 40
        }
    except Exception:
        return {
            "is_ihsg": False, "price": "-", "plan_type": "-", "is_breakdown": False,
            "buy_range": "-", "sl_price": "-", "tp1": "-", "tp2": "-", "tp3": "-",
            "risk_pct": "-", "reward_pct_1": "-", "reward_pct_2": "-", "reward_pct_3": "-",
            "rr_1": 0, "rr_2": 0, "rr_3": 0, "max_allowed_risk": 0,
            "vol_spike": False, "entry_worst": 0, "raw_risk_pct": 0, "technical_score": 50
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

# 7. Header Navigation
col_logo, col_title, col_space, col_menu = st.columns([0.3, 2.2, 4.2, 2.3])

with col_logo:
    st.markdown("<h3 style='margin:0; padding-top:0px; color: #00E676;'>Z</h3>", unsafe_allow_html=True)

with col_title:
    st.markdown("<h3 style='margin:0; padding-top:2px; font-size: 17px; color: #E2E8F0; font-weight: 700;'>Zio - Quant</h3>", unsafe_allow_html=True)

with col_menu:
    selected_screener = st.selectbox(
        "Pilih Screener",
        ["-- Pilih Screener --", "Stoch - Psar"],
        key="screener_choice",
        label_visibility="collapsed"
    )

st.markdown("<hr style='margin-top: 2px; margin-bottom: 6px; border-color: #1E2D3D;'>", unsafe_allow_html=True)

# 8. Layout Utama (2 Kolom)
col_left, col_right = st.columns([1, 2.2], gap="medium")

# --- KIRI: MARKET INDEX & LIST SAHAM ---
with col_left:
    st.markdown("<p style='font-size: 11px; color: #64748B; margin-bottom: 4px; font-weight: 600; letter-spacing: 0.5px;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊 **IHSG** | {ihsg_price:,.2f} ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
        st.session_state.active_ticker = "IDX:COMPOSITE"
        st.session_state.screener_choice = "-- Pilih Screener --"
        st.rerun()

    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)

    if st.session_state.screener_choice == "Stoch - Psar":
        st.markdown("<p style='font-size: 12px; color: #00E676; font-weight: bold; margin-bottom: 4px;'>Screener: Stoch - Psar</p>", unsafe_allow_html=True)
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🟢 Bullish", use_container_width=True, type="primary" if st.session_state.watchlist_tab == "bull" else "secondary"):
                st.session_state.watchlist_tab = "bull"
                st.rerun()
        with btn_c2:
            if st.button("🔴 Bearish", use_container_width=True, type="primary" if st.session_state.watchlist_tab == "bear" else "secondary"):
                st.session_state.watchlist_tab = "bear"
                st.rerun()

        with st.spinner("Memindai pasar..."):
            df_bull, df_bear = run_screener(SAHAM_LIST)

        with st.container(height=435):
            if st.session_state.watchlist_tab == "bull":
                if not df_bull.empty:
                    for index, row in df_bull.iterrows():
                        t_code = row["Ticker"]
                        t_price = row["Harga"]
                        t_chg = row["Chg"]
                        t_score = row["Score"]
                        t_type = row["Type"]
                        chg_sign = "+" if t_chg >= 0 else ""
                        chg_formatted = f"{chg_sign}{t_chg:.2f}%"
                        
                        btn_label = f"{t_code} | {t_price:,} | {chg_formatted} | Score: {t_score} ({t_type})"
                        if st.button(btn_label, key=f"bull_{t_code}", use_container_width=True):
                            st.session_state.active_ticker = f"IDX:{t_code}"
                            st.rerun()
                else:
                    st.info("Tidak ada saham Bullish.")
            else:
                if not df_bear.empty:
                    for index, row in df_bear.iterrows():
                        t_code = row["Ticker"]
                        t_price = row["Harga"]
                        t_chg = row["Chg"]
                        t_score = row["Score"]
                        t_type = row["Type"]
                        chg_sign = "+" if t_chg >= 0 else ""
                        chg_formatted = f"{chg_sign}{t_chg:.2f}%"
                        
                        btn_label = f"{t_code} | {t_price:,} | {chg_formatted} | Score: {t_score} ({t_type})"
                        if st.button(btn_label, key=f"bear_{t_code}", use_container_width=True):
                            st.session_state.active_ticker = f"IDX:{t_code}"
                            st.rerun()
                else:
                    st.info("Tidak ada saham Bearish.")
    else:
        st.info("Silakan pilih strategi screener pada dropdown kanan atas untuk menampilkan daftar rekomendasi saham.")

# --- KANAN: CHART / TRADE PLAN ---
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "IHSG" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol.replace("IDX:", "")
    tv_symbol = "IDX:COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol

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

    # VIEW 1: TRADINGVIEW CHART
    if st.session_state.view_mode == "chart":
        tradingview_html = f"""
        <div class="tradingview-widget-container" style="height:535px;width:100%">
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
        st.components.v1.html(tradingview_html, height=540)

    # VIEW 2: TRADE PLAN MODUL
    elif st.session_state.view_mode == "trade_plan":
        tp = get_stock_trade_plan(active_symbol)
        
        if tp["is_ihsg"]:
            st.info("ℹ️ **Indeks IHSG (Composite)** tidak memiliki Trade Plan individual. Silakan pilih salah satu saham dari watchlist sebelah kiri.")
        else:
            # Bagian 1: Status Chart
            st.markdown("##### 🟢 **1. STATUS CHART**")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 12px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 11px; margin: 0;">Ticker IDX</p>
                        <h3 style="color: #E2E8F0; margin: 2px 0; font-size: 20px;">{clean_ticker}</h3>
                        <p style="color: #00E676; font-size: 11px; margin: 0;">🟢 Papan Utama</p>
                    </div>
                """, unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 12px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 11px; margin: 0;">Last Price</p>
                        <h3 style="color: #E2E8F0; margin: 2px 0; font-size: 20px;">{tp['price']}</h3>
                        <p style="color: #00E676; font-size: 11px; margin: 0;">⚡ Volume Spike: {"Ya" if tp['vol_spike'] else "Normal"}</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: #121E2B; border: 1px solid #243447; padding: 10px 14px; border-radius: 8px; margin-top: 8px;">
                    <p style="color: #64748B; font-size: 11px; margin: 0;">Rekomendasi Tipe Beli (Setup Aktif)</p>
                    <p style="color: #00E676; font-size: 14px; font-weight: bold; margin: 2px 0;">⚡ {tp['plan_type']}</p>
                    <p style="color: #94A3B8; font-size: 11px; margin: 0;">Ditentukan berdasarkan kedekatan harga close ke Swing Low / Swing High</p>
                </div>
            """, unsafe_allow_html=True)

            if tp["is_breakdown"]:
                st.error("⛔ **RULE PENOLAKAN:** Saham Breakdown Support (Marubozu Merah / New Low 2 Bulan). Status: **SKIP / WAIT AND SEE**.")

            # Bagian 2: Trading Plan Detail
            st.markdown("##### 🔵 **2. TRADING PLAN DETAIL**")
            
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #1E3A2F; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #00E676; font-size: 11px; font-weight: bold; margin: 0;">🟢 AREA ENTRY (BUY ZONE)</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['buy_range']}</h4>
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">Akumulasi di support / breakout point.</p>
                    </div>
                """, unsafe_allow_html=True)
            with d2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #3A1E1E; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #FF5252; font-size: 11px; font-weight: bold; margin: 0;">🛑 STOP LOSS ({tp['risk_pct']})</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['sl_price']}</h4>
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">Cut loss disiplin bila closing di bawah level ini.</p>
                    </div>
                """, unsafe_allow_html=True)

            t1, t2, t3 = st.columns(3)
            with t1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 1 (Terdekat 1) | +{tp['reward_pct_1']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp1']}</h5>
                        <p style="color: #94A3B8; font-size: 9px; margin: 0;">Target profit pertama.</p>
                    </div>
                """, unsafe_allow_html=True)
            with t2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 2 (Terdekat 2) | +{tp['reward_pct_2']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp2']}</h5>
                        <p style="color: #94A3B8; font-size: 9px; margin: 0;">Target profit kedua.</p>
                    </div>
                """, unsafe_allow_html=True)
            with t3:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 3 (Terdekat 3) | +{tp['reward_pct_3']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp3']}</h5>
                        <p style="color: #94A3B8; font-size: 9px; margin: 0;">Target runner profit.</p>
                    </div>
                """, unsafe_allow_html=True)

            # Bagian 3: Rasio R:R tiap target
            st.markdown("##### 🟡 **3. RASIO R:R TIAP TARGET**")
            
            rr1_status = f"1 : {tp['rr_1']}" if tp['rr_1'] >= 2.0 else f"1 : {tp['rr_1']} (TIDAK SESUAI R:R - SKIP)"
            st.markdown(f"""
                <div style="background: #121E2B; border: 1px solid #243447; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between;">
                    <span style="color: #E2E8F0; font-size: 12px;">🔵 Target 1 (Konservatif)</span>
                    <span style="color: {'#00E676' if tp['rr_1'] >= 2.0 else '#FF5252'}; font-weight: bold; font-size: 12px;">{rr1_status}</span>
                </div>
                <div style="background: #121E2B; border: 1px solid #243447; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between;">
                    <span style="color: #E2E8F0; font-size: 12px;">🟢 Target 2 (Swing Utama)</span>
                    <span style="color: #00E676; font-weight: bold; font-size: 12px;">1 : {tp['rr_2']}</span>
                </div>
                <div style="background: #121E2B; border: 1px solid #243447; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                    <span style="color: #E2E8F0; font-size: 12px;">🔵 Target 3 (Runner Profit)</span>
                    <span style="color: #00E676; font-weight: bold; font-size: 12px;">1 : {tp['rr_3']}</span>
                </div>
            """, unsafe_allow_html=True)

            st.info("💡 **Tips Money Management:** Jika R:R minimal 1:2 tercapai pada TP1, Anda hanya membutuhkan win rate 40% untuk tetap menghasilkan profit jangka panjang yang konsisten!")

            # Simulasi Alokasi Modal Trading
            st.markdown("##### 💵 **Simulasi Alokasi Modal Trading**")
            modal = st.number_input("Masukkan Total Capital / Modal (Rp):", min_value=1_000_000, value=10_000_000, step=1_000_000)
            
            entry_price = tp["entry_worst"]
            if entry_price > 0:
                total_lot = int(modal // (entry_price * 100))
                total_buy = total_lot * entry_price * 100
                sl_val = int(tp["sl_price"].replace("Rp ", "").replace(".", "").replace(",", "")) if isinstance(tp["sl_price"], str) else 0
                tp1_val = int(tp["tp1"].replace("Rp ", "").replace(".", "").replace(",", "")) if isinstance(tp["tp1"], str) else 0
                max_loss_rp = total_lot * 100 * (entry_price - sl_val)
                max_gain_rp = total_lot * 100 * (tp1_val - entry_price)

                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.info(f"**Maksimal Pembelian:**\n\n**{total_lot} Lot** (Rp {int(total_buy):,})")
                c_m2.error(f"**Maksimal Risiko (Loss SL):**\n\n- Rp {int(max_loss_rp):,}")
                c_m3.success(f"**Potensi Profit (TP1):**\n\n+ Rp {int(max_gain_rp):,}")
