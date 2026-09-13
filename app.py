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
    
    /* Header Ticker Card Sesuai Warna Logo */
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
    .ticker-company-name {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 0 0 0;
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

# 2. Database Nama Panjang Perusahaan IDX
COMPANY_NAMES = {
    "ISAT": "PT Indosat Tbk", "BBCA": "PT Bank Central Asia Tbk", "BBRI": "PT Bank Rakyat Indonesia Tbk",
    "BMRI": "PT Bank Mandiri Tbk", "BBNI": "PT Bank Negara Indonesia Tbk", "TLKM": "PT Telkom Indonesia Tbk",
    "ASII": "PT Astra International Tbk", "AMMN": "PT Amman Mineral Internasional Tbk", "ANTM": "PT Aneka Tambang Tbk",
    "ADRO": "PT Adaro Energy Indonesia Tbk", "GOTO": "PT GoTo Gojek Tokopedia Tbk", "PGAS": "PT Perusahaan Gas Negara Tbk",
    "PTBA": "PT Bukit Asam Tbk", "UNVR": "PT Unilever Indonesia Tbk", "ACES": "PT Aspirasi Hidup Indonesia Tbk",
    "AKRA": "PT AKR Corporindo Tbk", "BRIS": "PT Bank Syariah Indonesia Tbk", "CPIN": "PT Charoen Pokphand Indonesia Tbk",
    "ICBP": "PT Indofood CBP Sukses Makmur Tbk", "INDF": "PT Indofood Sukses Makmur Tbk", "KLBF": "PT Kalbe Farma Tbk",
    "MEDC": "PT Medco Energi Internasional Tbk", "MDKA": "PT Merdeka Copper Gold Tbk", "TINS": "PT Timah Tbk"
}

def get_company_name(ticker_code):
    clean = ticker_code.replace("IDX:", "").replace(".JK", "").upper()
    return COMPANY_NAMES.get(clean, f"PT {clean} Tbk")

# 3. Inisialisasi Session State
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "IDX:ISAT"

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "trade_plan"

if 'watchlist_tab' not in st.session_state:
    st.session_state.watchlist_tab = "bull"

if 'screener_choice' not in st.session_state:
    st.session_state.screener_choice = "Stoch - Psar"

# 4. Daftar Saham IDX
SAHAM_LIST = sorted(list(set([
    "ISAT.JK", "ACES.JK", "ADHI.JK", "ADRO.JK", "AGRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK",
    "ARTO.JK", "ASII.JK", "AUTO.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK",
    "BRPT.JK", "BSDE.JK", "BUKA.JK", "BUMI.JK", "CPIN.JK", "CTRA.JK", "ELSA.JK", "EMTK.JK", "EXCL.JK",
    "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "ITMG.JK", "KLBF.JK", "MDKA.JK",
    "MEDC.JK", "MYOR.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK", "PTPP.JK", "SIDO.JK", "SMGR.JK", "TINS.JK",
    "TKIM.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK"
])))

# 5. Helper Fraksi Harga BEI & Tick Logic
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

def round_to_valid_tick(price):
    tick = get_tick_size(price)
    return int(round(price / tick) * tick)

# 6. Helper Badge R:R Warna
def get_rr_badge(rr_ratio):
    if isinstance(rr_ratio, str) or rr_ratio is None or rr_ratio <= 0:
        return "🔴"
    if rr_ratio < 2.0:
        return "🔴"
    elif rr_ratio <= 3.0:
        return "🟡"
    else:
        return "🟢"

# 7. Engine Screener
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
            v0 = float(df['Volume'].iloc[-1])
            l0 = float(df['Low'].iloc[-1])
            h0 = float(df['High'].iloc[-1])
            val0 = c0 * v0
            chg_pct = ((c0 - c1) / c1) * 100

            if c0 <= 50 or val0 < 1_000_000_000: continue

            df['vol_ma20'] = df['Volume'].rolling(window=20).mean()
            vol_ma20_0 = float(df['vol_ma20'].iloc[-1])

            low_min10 = df['Low'].rolling(window=10).min()
            high_max10 = df['High'].rolling(window=10).max()
            fast_k = 100 * ((df['Close'] - low_min10) / (high_max10 - low_min10 + 1e-5))
            df['stoch_k'] = fast_k.rolling(window=5).mean()
            df['stoch_d'] = df['stoch_k'].rolling(window=5).mean()

            try:
                psar_ind = ta.trend.PSARIndicator(high=df['High'], low=df['Low'], close=df['Close'], step=0.02, max_step=0.2)
                df['psar'] = psar_ind.psar()
            except:
                df['psar'] = df['Close']

            k0, d0 = float(df['stoch_k'].iloc[-1]), float(df['stoch_d'].iloc[-1])
            k1, d1 = float(df['stoch_k'].iloc[-2]), float(df['stoch_d'].iloc[-2])
            psar0 = float(df['psar'].iloc[-1])

            # Bullish Filter
            if k0 < 45:
                gc_today = (k1 < d1) and (k0 >= d0)
                is_almost_gc = (k0 <= d0) and ((d0 - k0) <= 3.0)

                stoch_signal = None
                if gc_today: stoch_signal = {"type": "GC + Vol Spike" if v0 > vol_ma20_0 else "Golden Cross", "score": 75}
                elif is_almost_gc: stoch_signal = {"type": "Early Signal", "score": 55}

                if stoch_signal:
                    score = stoch_signal["score"]
                    if psar0 < l0: score += 15
                    if v0 > vol_ma20_0: score += 10
                    sign = "+" if chg_pct >= 0 else ""
                    results_gc.append({
                        "Ticker": ticker.replace(".JK", ""),
                        "Harga": int(c0),
                        "Chg": f"{sign}{chg_pct:.2f}%",
                        "Score": score,
                        "Type": stoch_signal["type"]
                    })

            # Bearish Filter
            if k0 >= 70:
                dc_today = (k1 > d1) and (k0 <= d0)
                dc_signal = {"type": "Death Cross", "score": -75} if dc_today else None

                if dc_signal:
                    score = dc_signal["score"]
                    if psar0 > h0: score -= 15
                    if v0 > vol_ma20_0: score -= 10
                    sign = "+" if chg_pct >= 0 else ""
                    results_dc.append({
                        "Ticker": ticker.replace(".JK", ""),
                        "Harga": int(c0),
                        "Chg": f"{sign}{chg_pct:.2f}%",
                        "Score": abs(score),
                        "Type": dc_signal["type"]
                    })
        except Exception:
            continue

    df_gc = pd.DataFrame(results_gc)
    df_dc = pd.DataFrame(results_dc)
    if not df_gc.empty: df_gc = df_gc.sort_values(by="Score", ascending=False).reset_index(drop=True)
    if not df_dc.empty: df_dc = df_dc.sort_values(by="Score", ascending=False).reset_index(drop=True)
    return df_gc, df_dc

# 8. Engine Trade Plan Presisi Presets
@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    clean_sym = symbol.replace("IDX:", "").replace(".JK", "").upper()
    if clean_sym in ["COMPOSITE", "^JKSE"]:
        return {"is_ihsg": True}

    try:
        yf_symbol = f"{clean_sym}.JK"
        df = yf.download(yf_symbol, period="120d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        c0 = round_to_valid_tick(float(df['Close'].iloc[-1]))
        swing_low_60 = round_to_valid_tick(float(df['Low'].tail(60).min()))
        swing_high_60 = round_to_valid_tick(float(df['High'].tail(60).max()))

        # Khusus Preset Presisi ISAT Sesuai Diskusi Level Swing Visual
        if clean_sym == "ISAT":
            bow_buy_low = 2320
            bow_buy_high = 2360
            bow_sl = 2290
            bow_tp1, bow_tp2, bow_tp3 = 2490, 2610, 2820

            bob_buy_low = 2490
            bob_buy_high = 2520
            bob_sl = 2430
            bob_tp1, bob_tp2, bob_tp3 = 2610, 2820, 3000

            # Penentuan posisi saat ini (di Rp 2.430 -> BOW Plan aktif)
            pos_ratio = (c0 - swing_low_60) / (swing_high_60 - swing_low_60 + 1e-5)
            plan_type = "BOW" if c0 < 2490 else "BOB"

            if plan_type == "BOW":
                b_low, b_high, sl_val = bow_buy_low, bow_buy_high, bow_sl
                tp1, tp2, tp3 = bow_tp1, bow_tp2, bow_tp3
            else:
                b_low, b_high, sl_val = bob_buy_low, bob_buy_high, bob_sl
                tp1, tp2, tp3 = bob_tp1, bob_tp2, bob_tp3
        else:
            # Algoritma Umum Saham Lain
            range_span = max(1.0, swing_high_60 - swing_low_60)
            pos_ratio = (c0 - swing_low_60) / range_span

            lh1 = round_to_valid_tick(float(df['High'].tail(25).iloc[:-2].max()))
            lh2 = round_to_valid_tick((lh1 + swing_high_60) / 2)

            if pos_ratio < 0.50:
                plan_type = "BOW"
                b_low = swing_low_60
                b_high = min(c0, round_to_valid_tick(float(df['Low'].tail(5).mean())))
                sl_val = subtract_ticks(swing_low_60, 3)
                tp1, tp2, tp3 = lh1, lh2, swing_high_60
            else:
                plan_type = "BOB"
                b_low = c0
                b_high = add_ticks(c0, 3)
                sl_val = subtract_ticks(c0, 3)
                tp1, tp2, tp3 = lh1, swing_high_60, add_ticks(swing_high_60, 10)

        entry_worst = b_high
        risk_pct = round(((entry_worst - sl_val) / entry_worst) * 100, 2)
        
        rew1_pct = round(((tp1 - entry_worst) / entry_worst) * 100, 2)
        rew2_pct = round(((tp2 - entry_worst) / entry_worst) * 100, 2)
        rew3_pct = round(((tp3 - entry_worst) / entry_worst) * 100, 2)

        rr1 = round(rew1_pct / risk_pct, 2) if risk_pct > 0 else 0
        rr2 = round(rew2_pct / risk_pct, 2) if risk_pct > 0 else 0
        rr3 = round(rew3_pct / risk_pct, 2) if risk_pct > 0 else 0

        return {
            "is_ihsg": False,
            "ticker": clean_sym,
            "company_name": get_company_name(clean_sym),
            "price": f"Rp {c0:,}",
            "plan_type": plan_type,
            "buy_range": f"Rp {b_low:,} – Rp {b_high:,}",
            "worst_entry": entry_worst,
            "sl_price": f"Rp {sl_val:,}",
            "risk_pct": f"{risk_pct}%",
            "tp1": f"Rp {tp1:,}", "rr1": rr1, "badge1": get_rr_badge(rr1),
            "tp2": f"Rp {tp2:,}", "rr2": rr2, "badge2": get_rr_badge(rr2),
            "tp3": f"Rp {tp3:,}", "rr3": rr3, "badge3": get_rr_badge(rr3)
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

# 9. Header Navigation
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

# 10. Layout Utama (2 Kolom)
col_left, col_right = st.columns([1, 2.2], gap="medium")

# --- KIRI: WATCHLIST / SCREENER ---
with col_left:
    st.markdown("<p style='font-size: 11px; color: #64748B; margin-bottom: 4px; font-weight: 600; letter-spacing: 0.5px;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊  **IHSG**  |  {ihsg_price:,.2f}  ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
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

        with st.container(height=448):
            if st.session_state.watchlist_tab == "bull":
                if not df_bull.empty:
                    for index, row in df_bull.iterrows():
                        t_code = row["Ticker"]
                        t_price = row["Harga"]
                        t_chg = row["Chg"]
                        t_score = row["Score"]
                        t_type = row["Type"]
                        # Format Tampilan Sesuai Request User
                        btn_label = f"{t_code} | {t_price:,} | {t_chg} | Score: {t_score} ({t_type})"
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
                        btn_label = f"{t_code} | {t_price:,} | {t_chg} | Score: {t_score} ({t_type})"
                        if st.button(btn_label, key=f"bear_{t_code}", use_container_width=True):
                            st.session_state.active_ticker = f"IDX:{t_code}"
                            st.rerun()
                else:
                    st.info("Tidak ada saham Bearish.")
    else:
        st.info("Silakan pilih strategi screener pada dropdown kanan atas untuk menampilkan rekomendasi saham.")

# --- KANAN: CHART / TRADE PLAN ---
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "IHSG" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol.replace("IDX:", "")
    company_full_name = get_company_name(clean_ticker)
    tv_symbol = "IDX:COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol

    # Header Ticker Card Dengan Nama Panjang Perusahaan
    c_title, c_b1, c_b2 = st.columns([2.5, 1, 1])
    with c_title:
        st.markdown(f"""
            <div class="ticker-header-card">
                <p class="ticker-header-text">Ticker : {clean_ticker}</p>
                <p class="ticker-company-name">{company_full_name}</p>
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
        
        st.markdown(f"#### 📋 Modul Trade Plan — `{clean_ticker}`")
        
        if tp.get("is_ihsg", False):
            st.info("ℹ️ **Indeks IHSG (Composite)** tidak memiliki Trade Plan individual. Silakan pilih salah satu saham dari watchlist sebelah kiri.")
        else:
            col_tp1, col_tp2, col_tp3 = st.columns(3)
            with col_tp1:
                st.metric("Strategi Plan", tp["plan_type"])
                st.metric("Area Beli (Buy Range)", tp["buy_range"])
                st.metric("Risk (%)", tp["risk_pct"])

            with col_tp2:
                st.metric("Stop Loss (SL)", tp["sl_price"])
                st.metric("Target Profit 1 (TP1)", f"{tp['tp1']}  {tp['badge1']}")
                st.metric("R:R Ratio (TP1)", f"1 : {tp['rr1']}  {tp['badge1']}")

            with col_tp3:
                st.metric("Target Profit 2 (TP2)", f"{tp['tp2']}  {tp['badge2']}")
                st.metric("R:R Ratio (TP2)", f"1 : {tp['rr2']}  {tp['badge2']}")
                st.metric("Target Profit 3 (TP3)", f"{tp['tp3']}  {tp['badge3']}")

            # Deskripsi / Legenda Warna Bulat R:R (Sesuai Permintaan)
            st.markdown("""
                > **💡 Legenda Indikator Kelayakan Risk to Reward (R:R):**  
                > 🔴 **Kurang Oke** (R:R < 1 : 2) &nbsp;|&nbsp; 🟡 **OK / Layak** (R:R 1 : 2 – 1 : 3) &nbsp;|&nbsp; 🟢 **Sangat Oke** (R:R > 1 : 3)
            """)

            st.markdown("---")
            
            if tp["plan_type"] == "BOW":
                st.info("💡 **Manajemen Porsi BOW:** Entry 50% porsi di area support. Tambah 50% porsi saat konfirmasi CHoCH Bullish (Daily Close di atas LH terdekat).")
            else:
                st.info("💡 **Manajemen Porsi BOB:** Trigger Candle Close di atas LH terdekat + Vol Spike. Max chasing +3 ticks dari breakout point.")

            st.markdown("##### 💵 Simulasi Alokasi Modal Trading")
            modal = st.number_input("Masukkan Total Capital / Modal (Rp):", min_value=1_000_000, value=10_000_000, step=1_000_000)
            
            entry_price = tp["worst_entry"]
            if entry_price > 0:
                total_lot = int(modal // (entry_price * 100))
                total_buy = total_lot * entry_price * 100
                sl_val = int(tp["sl_price"].replace("Rp ", "").replace(",", ""))
                tp1_val = int(tp["tp1"].replace("Rp ", "").replace(",", ""))
                max_loss_rp = total_lot * 100 * (entry_price - sl_val)
                max_gain_rp = total_lot * 100 * (tp1_val - entry_price)

                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.info(f"**Maksimal Pembelian:**\n\n**{total_lot} Lot** (Rp {int(total_buy):,})")
                c_m2.error(f"**Maksimal Risiko (Loss SL):**\n\n- Rp {int(max_loss_rp):,}")
                c_m3.success(f"**Potensi Profit (TP1):**\n\n+ Rp {int(max_gain_rp):,}")
