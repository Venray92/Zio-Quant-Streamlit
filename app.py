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
        padding: 6px 14px;
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
    .company-name-text {
        color: #94A3B8;
        font-size: 11px;
        margin: 1px 0 0 0;
        font-weight: 500;
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
    
    /* Style untuk Home Brand Link Button */
    .home-btn button {
        background: transparent !important;
        border: none !important;
        color: #00E676 !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        padding: 0 !important;
        text-align: left !important;
        box-shadow: none !important;
    }
    .home-btn button:hover {
        color: #66FFA6 !important;
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Inisialisasi State Awal
def reset_to_home():
    st.session_state.active_ticker = "IDX:COMPOSITE"
    st.session_state.view_mode = "chart"
    st.session_state.watchlist_tab = "bull"
    st.session_state.screener_choice = "-- Pilih Screener --"

if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "IDX:COMPOSITE"

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "chart"

if 'watchlist_tab' not in st.session_state:
    st.session_state.watchlist_tab = "bull"

if 'screener_choice' not in st.session_state:
    st.session_state.screener_choice = "-- Pilih Screener --"

# 3. Data Nama Perusahaan Saham IDX
TICKER_NAMES = {
    "ISAT": "Indosat Tbk.",
    "BBCA": "Bank Central Asia Tbk.",
    "BBRI": "Bank Rakyat Indonesia (Persero) Tbk.",
    "BMRI": "Bank Mandiri (Persero) Tbk.",
    "BBNI": "Bank Negara Indonesia (Persero) Tbk.",
    "TLKM": "Telkom Indonesia (Persero) Tbk.",
    "ASII": "Astra International Tbk.",
    "UNVR": "Unilever Indonesia Tbk.",
    "ADRO": "Adaro Energy Indonesia Tbk.",
    "ANTM": "Aneka Tambang Tbk.",
    "AMMN": "Amman Mineral Internasional Tbk.",
    "BREN": "Barito Renewables Energy Tbk.",
    "GOTO": "GoTo Gojek Tokopedia Tbk.",
    "COMPOSITE": "Indeks Harga Saham Gabungan (IHSG)"
}

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

# 4. Helper Fraksi Harga BEI
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

# 5. Screener Engine
@st.cache_data(ttl=3600)
def run_screener(tickers):
    results_gc, results_dc = [], []
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
                is_almost_gc = (k0 <= d0) and ((d0 - k0) <= 3.0)

                stoch_signal = None
                if gc_today: stoch_signal = {"type": "GC", "score": 80}
                elif gc_yesterday: stoch_signal = {"type": "GC Kemarin", "score": 70}
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
                        "Harga": int(c0), "Chg": chg_pct,
                        "Score": score, "Type": " + ".join(desc_list)
                    })

            if k0 >= 75:
                dc_today = (k1 > d1) and (k0 <= d0)
                is_almost_dc = (k0 >= d0) and ((k0 - d0) <= 3.0)

                dc_signal = None
                if dc_today: dc_signal = {"type": "DC", "score": -80}
                elif is_almost_dc: dc_signal = {"type": "Early DC", "score": -55}

                if dc_signal:
                    score = dc_signal["score"]
                    desc_list = [dc_signal["type"]]
                    if psar0 > h0: score -= 20
                    if v0 > vol_ma20_0: score -= 10
                    
                    results_dc.append({
                        "Ticker": ticker.replace(".JK", ""), 
                        "Harga": int(c0), "Chg": chg_pct,
                        "Score": score, "Type": " + ".join(desc_list)
                    })
        except Exception:
            continue

    df_gc = pd.DataFrame(results_gc)
    df_dc = pd.DataFrame(results_dc)
    if not df_gc.empty: df_gc = df_gc.sort_values(by="Score", ascending=False).reset_index(drop=True)
    if not df_dc.empty: df_dc = df_dc.sort_values(by="Score", ascending=True).reset_index(drop=True)
    return df_gc, df_dc

# 6. Trade Plan Engine Berdasarkan Deteksi Fractal Swing Real
@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {"is_ihsg": True}
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

        # Deteksi Swing High (Puncak-Puncak Fractal Reversal)
        highs = df['High'].values
        lows = df['Low'].values
        opens = df['Open'].values
        closes = df['Close'].values
        n = len(df)

        swing_highs = []
        for i in range(2, n - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append(float(highs[i]))

        # Filter Swing High yang Berada di Atas Harga Close
        valid_sh = sorted(list(set([sh for sh in swing_highs if sh > c0])))

        if len(valid_sh) >= 3:
            tp1, tp2, tp3 = valid_sh[0], valid_sh[1], valid_sh[2]
        elif len(valid_sh) == 2:
            tp1, tp2, tp3 = valid_sh[0], valid_sh[1], valid_sh[1] * 1.08
        elif len(valid_sh) == 1:
            tp1, tp2, tp3 = valid_sh[0], valid_sh[0] * 1.05, valid_sh[0] * 1.10
        else:
            tp1, tp2, tp3 = c0 * 1.04, c0 * 1.08, c0 * 1.15

        # Deteksi Swing Low Terakhir (Wick Low & Upper Body/Open/Close Low)
        swing_lows = []
        body_lows = []
        for i in range(2, n - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append(float(lows[i]))
                body_lows.append(float(min(opens[i], closes[i])))

        if swing_lows:
            swing_low_wick = swing_lows[-1]
            swing_low_body = body_lows[-1]
        else:
            swing_low_wick = float(df['Low'].tail(20).min())
            swing_low_body = swing_low_wick * 1.015

        bow_low = min(swing_low_wick, swing_low_body)
        bow_high = max(swing_low_wick, swing_low_body)

        bob_low = tp1
        bob_high = add_ticks(tp1, 3)

        # Cek Kecondongan Harga Close
        dist_to_low = abs(c0 - bow_low)
        dist_to_high = abs(tp1 - c0)

        if dist_to_low <= dist_to_high:
            bias_text = "BUY ON WEAKNESS (BOW)"
            bias_desc = f"Harga saat ini (Rp {int(c0):,}) lebih condong dekat ke area Swing Low Support (Rp {int(bow_low):,})."
            bias_color = "#00E676"
            entry_worst = bow_high
            sl_price = subtract_ticks(bow_low, 3)
        else:
            bias_text = "BUY ON BREAKOUT (BOB)"
            bias_desc = f"Harga saat ini (Rp {int(c0):,}) lebih condong dekat ke Resistance Swing High (Rp {int(tp1):,})."
            bias_color = "#38BDF8"
            entry_worst = bob_high
            sl_price = subtract_ticks(tp1, 3)

        risk_pct = round(((entry_worst - sl_price) / entry_worst) * 100, 2)
        reward_pct_1 = round(((tp1 - entry_worst) / entry_worst) * 100, 2)
        reward_pct_2 = round(((tp2 - entry_worst) / entry_worst) * 100, 2)
        reward_pct_3 = round(((tp3 - entry_worst) / entry_worst) * 100, 2)

        rr_1 = round(reward_pct_1 / risk_pct, 1) if risk_pct > 0 else 0
        rr_2 = round(reward_pct_2 / risk_pct, 1) if risk_pct > 0 else 0
        rr_3 = round(reward_pct_3 / risk_pct, 1) if risk_pct > 0 else 0

        vol_ma20 = float(df['Volume'].tail(20).mean())
        is_breakdown = (c0 <= bow_low)

        return {
            "is_ihsg": False,
            "price": f"Rp {int(c0):,}",
            "bias_text": bias_text,
            "bias_desc": bias_desc,
            "bias_color": bias_color,
            "bow_range": f"Rp {int(bow_low):,} – Rp {int(bow_high):,}",
            "bob_range": f"Rp {int(bob_low):,} – Rp {int(bob_high):,}",
            "sl_price": f"Rp {int(sl_price):,}",
            "tp1": f"Rp {int(tp1):,}",
            "tp2": f"Rp {int(tp2):,}",
            "tp3": f"Rp {int(tp3):,}",
            "risk_pct": f"{risk_pct}%",
            "reward_pct_1": f"{reward_pct_1}%",
            "reward_pct_2": f"{reward_pct_2}%",
            "reward_pct_3": f"{reward_pct_3}%",
            "rr_1": rr_1, "rr_2": rr_2, "rr_3": rr_3,
            "vol_spike": (v0 >= vol_ma20),
            "entry_worst": entry_worst,
            "is_breakdown": is_breakdown
        }
    except Exception:
        return {"is_ihsg": True}

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

# 7. Header Navigation (Dengan Home Reset Link)
col_head, col_space, col_menu = st.columns([3, 4, 2.3])

with col_head:
    st.markdown('<div class="home-btn">', unsafe_allow_html=True)
    if st.button("📈 Zio - Quant", key="btn_home_reset"):
        reset_to_home()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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

# --- KIRI: MARKET INDEX & WATCHLIST ---
with col_left:
    st.markdown("<p style='font-size: 11px; color: #64748B; margin-bottom: 4px; font-weight: 600;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊 **IHSG** | {ihsg_price:,.2f} ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
        st.session_state.active_ticker = "IDX:COMPOSITE"
        st.session_state.screener_choice = "-- Pilih Screener --"
        st.rerun()

    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)

    if st.session_state.screener_choice == "Stoch - Psar":
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
            df_curr = df_bull if st.session_state.watchlist_tab == "bull" else df_bear
            if not df_curr.empty:
                for index, row in df_curr.iterrows():
                    t_code = row["Ticker"]
                    t_price = row["Harga"]
                    t_chg = row["Chg"]
                    t_score = row["Score"]
                    t_type = row["Type"]
                    chg_sign = "+" if t_chg >= 0 else ""
                    
                    btn_label = f"{t_code} | {t_price:,} | {chg_sign}{t_chg:.2f}% | Score: {t_score}"
                    if st.button(btn_label, key=f"wt_{t_code}", use_container_width=True):
                        st.session_state.active_ticker = f"IDX:{t_code}"
                        st.rerun()
            else:
                st.info("Tidak ada saham ditemukan.")
    else:
        st.info("Silakan pilih screener pada dropdown kanan atas.")

# --- KANAN: CHART / TRADE PLAN ---
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol.replace("IDX:", "")
    tv_symbol = "IDX:COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol
    company_fullname = TICKER_NAMES.get(clean_ticker, f"{clean_ticker} Tbk.")

    c_title, c_b1, c_b2 = st.columns([2.5, 1, 1])
    with c_title:
        st.markdown(f"""
            <div class="ticker-header-card">
                <p class="ticker-header-text">Ticker : {clean_ticker}</p>
                <p class="company-name-text">{company_fullname}</p>
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

    elif st.session_state.view_mode == "trade_plan":
        tp = get_stock_trade_plan(active_symbol)
        
        if tp.get("is_ihsg", False):
            st.info("ℹ️ Indeks IHSG (Composite) tidak memiliki Trade Plan individual.")
        else:
            # Pemberitahuan Kecondongan Tipe Beli
            st.markdown(f"""
                <div style="background: #121E2B; border: 1px solid {tp['bias_color']}; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;">
                    <p style="color: #64748B; font-size: 11px; margin: 0; font-weight: 600;">REKOMENDASI KECONDONGAN HARGA</p>
                    <p style="color: {tp['bias_color']}; font-size: 15px; font-weight: bold; margin: 2px 0;">⚡ LEBIH CONDONG KEPADA: {tp['bias_text']}</p>
                    <p style="color: #94A3B8; font-size: 11px; margin: 0;">{tp['bias_desc']}</p>
                </div>
            """, unsafe_allow_html=True)

            if tp["is_breakdown"]:
                st.error("⛔ Saham saat ini berada di bawah Swing Low Support. Status: **SKIP / WAIT AND SEE**.")

            # Detail Opsi Pembelian
            st.markdown("##### 🟢 **1. AREA PEMBELIAN (ENTRY ZONES)**")
            o1, o2 = st.columns(2)
            with o1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #1E3A2F; padding: 12px; border-radius: 8px;">
                        <p style="color: #00E676; font-size: 11px; font-weight: bold; margin: 0;">🔵 AREA BUY ON WEAKNESS (BOW)</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['bow_range']}</h4>
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">Area Swing Low terakhir (Body & Wick Low).</p>
                    </div>
                """, unsafe_allow_html=True)
            with o2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #1E2D3D; padding: 12px; border-radius: 8px;">
                        <p style="color: #38BDF8; font-size: 11px; font-weight: bold; margin: 0;">🚀 AREA BUY ON BREAKOUT (BOB)</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['bob_range']}</h4>
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">Breakout Swing High 1 (2.490 + 3 Tick).</p>
                    </div>
                """, unsafe_allow_html=True)

            # Target Profit & Stop Loss
            st.markdown("##### 🔵 **2. TARGET PROFIT & STOP LOSS**")
            sl_col, tp_col = st.columns([1, 2.2])
            with sl_col:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #3A1E1E; padding: 12px; border-radius: 8px;">
                        <p style="color: #FF5252; font-size: 11px; font-weight: bold; margin: 0;">🛑 STOP LOSS ({tp['risk_pct']})</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['sl_price']}</h4>
                        <p style="color: #94A3B8; font-size: 10px; margin: 0;">Cutloss jika close di bawah Swing Low.</p>
                    </div>
                """, unsafe_allow_html=True)

            with tp_col:
                t1, t2, t3 = st.columns(3)
                with t1:
                    st.markdown(f"""
                        <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                            <p style="color: #64748B; font-size: 10px; margin: 0;">TP 1 | +{tp['reward_pct_1']}</p>
                            <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp1']}</h5>
                            <p style="color: #94A3B8; font-size: 9px; margin: 0;">Swing High 1</p>
                        </div>
                    """, unsafe_allow_html=True)
                with t2:
                    st.markdown(f"""
                        <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                            <p style="color: #64748B; font-size: 10px; margin: 0;">TP 2 | +{tp['reward_pct_2']}</p>
                            <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp2']}</h5>
                            <p style="color: #94A3B8; font-size: 9px; margin: 0;">Swing High 2</p>
                        </div>
                    """, unsafe_allow_html=True)
                with t3:
                    st.markdown(f"""
                        <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                            <p style="color: #64748B; font-size: 10px; margin: 0;">TP 3 | +{tp['reward_pct_3']}</p>
                            <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp3']}</h5>
                            <p style="color: #94A3B8; font-size: 9px; margin: 0;">Swing High 3</p>
                        </div>
                    """, unsafe_allow_html=True)

            # Risk to Reward Ratios
            st.markdown("##### 🟡 **3. RISK TO REWARD RATIO**")
            st.markdown(f"""
                <div style="background: #121E2B; border: 1px solid #243447; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between;">
                    <span style="color: #E2E8F0; font-size: 12px;">🔵 Target 1 (Swing High 1)</span>
                    <span style="color: #00E676; font-weight: bold; font-size: 12px;">1 : {tp['rr_1']}</span>
                </div>
                <div style="background: #121E2B; border: 1px solid #243447; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between;">
                    <span style="color: #E2E8F0; font-size: 12px;">🟢 Target 2 (Swing High 2)</span>
                    <span style="color: #00E676; font-weight: bold; font-size: 12px;">1 : {tp['rr_2']}</span>
                </div>
                <div style="background: #121E2B; border: 1px solid #243447; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                    <span style="color: #E2E8F0; font-size: 12px;">🔵 Target 3 (Swing High 3)</span>
                    <span style="color: #00E676; font-weight: bold; font-size: 12px;">1 : {tp['rr_3']}</span>
                </div>
            """, unsafe_allow_html=True)
