import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import warnings
import requests

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
    .stApp { background-color: #0B131D !important; color: #E2E8F0; }
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .ticker-header-card {
        background: linear-gradient(135deg, #121E2B 0%, #1A293B 100%);
        border: 1px solid #243447; border-left: 5px solid #00E676;
        padding: 4px 12px; border-radius: 6px; display: inline-block; margin-bottom: 4px;
    }
    .ticker-header-text { color: #00E676; font-size: 16px; font-weight: 700; letter-spacing: 0.5px; margin: 0; }
    .company-name-text { color: #94A3B8; font-size: 11px; margin-top: 2px; margin-bottom: 0px; font-weight: 500; }
    
    div.stButton > button[kind="primary"] { background-color: #00E676 !important; color: #0B131D !important; border: none !important; font-weight: 700 !important; }
    div.stButton > button[kind="secondary"] { background-color: #121E2B !important; color: #94A3B8 !important; border: 1px solid #243447 !important; }
    div.stButton > button[kind="secondary"]:hover { border-color: #00E676 !important; color: #00E676 !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Inisialisasi Session State
def reset_to_default():
    st.session_state.active_ticker = "IDX:COMPOSITE"
    st.session_state.view_mode = "chart"
    st.session_state.watchlist_tab = "bull"
    st.session_state.screener_choice = "-- Pilih Screener --"

if 'active_ticker' not in st.session_state: st.session_state.active_ticker = "IDX:COMPOSITE"
if 'view_mode' not in st.session_state: st.session_state.view_mode = "chart"
if 'watchlist_tab' not in st.session_state: st.session_state.watchlist_tab = "bull"
if 'screener_choice' not in st.session_state: st.session_state.screener_choice = "-- Pilih Screener --"

# 3. AUTOMATIC FETCH DAFTAR SAHAM & NAMA PERUSAHAAN BEI (TANPA KETIK MANUAL!)
@st.cache_data(ttl=86400) # Cache 24 Jam
def load_idx_companies():
    """Tarik daftar seluruh saham IDX & Nama Perusahaan dari Github Open Dataset / Fallback"""
    try:
        url = "https://raw.githubusercontent.com/datasets/investing-idx/master/data/stock-list.csv"
        df_idx = pd.read_csv(url)
        companies = dict(zip(df_idx['Code'], df_idx['Name']))
        return companies
    except Exception:
        # Fallback jika koneksi ke GitHub Dataset terkendala
        return {
            "BBCA": "Bank Central Asia Tbk", "BBRI": "Bank Rakyat Indonesia Tbk",
            "BMRI": "Bank Mandiri Tbk", "BBNI": "Bank Negara Indonesia Tbk",
            "TLKM": "Telkom Indonesia Tbk", "ASII": "Astra International Tbk",
            "ISAT": "Indosat Tbk", "AMMN": "Amman Mineral Internasional Tbk",
            "BREN": "Barito Renewables Energy Tbk", "TPIA": "Chandra Asri Pacific Tbk"
        }

NAMA_PERUSAHAAN = load_idx_companies()
SAHAM_LIST = sorted(list(NAMA_PERUSAHAAN.keys()))

# 4. Helper Fraksi Harga BEI Sesuai Aturan Regulasi Mutlak
def get_tick_size(price):
    if price < 200: return 1
    elif price < 500: return 2
    elif price < 2000: return 5
    elif price < 5000: return 10
    else: return 25

def subtract_ticks(price, num_ticks):
    curr = float(price)
    for _ in range(num_ticks):
        curr -= get_tick_size(curr)
    return max(1.0, curr)

def add_ticks(price, num_ticks):
    curr = float(price)
    for _ in range(num_ticks):
        curr += get_tick_size(curr)
    return curr

# 5. Algoritma Deteksi Fractal Swing Low & Swing High Nyata
def find_swing_points(df, window=3):
    """Mencari titik puncak reversal (Swing High) dan puncak lembah (Swing Low)"""
    swing_highs = []
    swing_lows = []
    
    highs = df['High'].values
    lows = df['Low'].values
    n = len(df)
    
    for i in range(window, n - window):
        # Deteksi Swing High (Peak Puncak)
        if all(highs[i] > highs[i - j] for j in range(1, window + 1)) and \
           all(highs[i] >= highs[i + j] for j in range(1, window + 1)):
            swing_highs.append(float(highs[i]))
            
        # Deteksi Swing Low (Peak Lembah)
        if all(lows[i] < lows[i - j] for j in range(1, window + 1)) and \
           all(lows[i] <= lows[i + j] for j in range(1, window + 1)):
            swing_lows.append(float(lows[i]))
            
    return swing_highs, swing_lows

# 6. Screener Engine
@st.cache_data(ttl=3600)
def run_screener(tickers):
    results_gc, results_dc = [], []
    for ticker in tickers[:150]: # Menguji 150 saham teratas agar cepat
        try:
            df = yf.download(f"{ticker}.JK", period="90d", interval="1d", progress=False)
            if df.empty or len(df) < 30: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

            c0 = float(df['Close'].iloc[-1])
            c1 = float(df['Close'].iloc[-2])
            chg_pct = ((c0 - c1) / c1) * 100
            v0 = float(df['Volume'].iloc[-1])
            val0 = c0 * v0

            if c0 <= 50 or val0 < 1_000_000_000: continue

            df['vol_ma20'] = df['Volume'].rolling(window=20).mean()
            vol_ma20_0 = float(df['vol_ma20'].iloc[-1])

            low_min10 = df['Low'].rolling(window=10).min()
            high_max10 = df['High'].rolling(window=10).max()
            fast_k = 100 * ((df['Close'] - low_min10) / (high_max10 - low_min10))
            df['stoch_k'] = fast_k.rolling(window=5).mean()
            df['stoch_d'] = df['stoch_k'].rolling(window=5).mean()

            psar_ind = ta.trend.PSARIndicator(high=df['High'], low=df['Low'], close=df['Close'], step=0.02, max_step=0.2)
            df['psar'] = psar_ind.psar()

            k0, d0 = float(df['stoch_k'].iloc[-1]), float(df['stoch_d'].iloc[-1])
            k1, d1 = float(df['stoch_k'].iloc[-2]), float(df['stoch_d'].iloc[-2])

            if k0 < 35 and (k1 < d1) and (k0 >= d0):
                score = 80
                if v0 > vol_ma20_0: score += 10
                results_gc.append({"Ticker": ticker, "Harga": int(c0), "Chg": chg_pct, "Score": score, "Type": "Stoch Golden Cross"})

            if k0 >= 75 and (k1 > d1) and (k0 <= d0):
                score = -80
                if v0 > vol_ma20_0: score -= 10
                results_dc.append({"Ticker": ticker, "Harga": int(c0), "Chg": chg_pct, "Score": score, "Type": "Stoch Dead Cross"})
        except Exception:
            continue

    df_gc = pd.DataFrame(results_gc).sort_values(by="Score", ascending=False) if results_gc else pd.DataFrame()
    df_dc = pd.DataFrame(results_dc).sort_values(by="Score", ascending=True) if results_dc else pd.DataFrame()
    return df_gc, df_dc

# 7. Trade Plan Engine TERPERBARUI DENGAN LOGIKA STRUCTURAL FRACTAL
@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {"is_ihsg": True}
    try:
        yf_symbol = f"{symbol.replace('IDX:', '')}.JK"
        df = yf.download(yf_symbol, period="180d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        c0 = float(df['Close'].iloc[-1])
        o0 = float(df['Open'].iloc[-1])
        h0 = float(df['High'].iloc[-1])
        l0 = float(df['Low'].iloc[-1])
        v0 = float(df['Volume'].iloc[-1])

        # A. Cari Swing Points Real
        sh_list, sl_list = find_swing_points(df, window=3)
        
        # Filtering Target Swing High di atas harga saat ini (TP1, TP2, TP3)
        valid_sh = sorted(list(set([x for x in sh_list if x > c0])))
        
        # Emergency Fallback jika data puncak terbatas
        if len(valid_sh) == 0:
            tp1 = add_ticks(c0, 6)
            tp2 = add_ticks(tp1, 8)
            tp3 = add_ticks(tp2, 12)
        elif len(valid_sh) == 1:
            tp1 = valid_sh[0]
            tp2 = add_ticks(tp1, 8)
            tp3 = add_ticks(tp2, 12)
        elif len(valid_sh) == 2:
            tp1, tp2 = valid_sh[0], valid_sh[1]
            tp3 = add_ticks(tp2, 10)
        else:
            tp1, tp2, tp3 = valid_sh[0], valid_sh[1], valid_sh[2]

        # Filtering Swing Low Support Terdekat di bawah Close
        valid_sl = sorted(list(set([x for x in sl_list if x <= c0])))
        swing_low_real = valid_sl[-1] if len(valid_sl) > 0 else subtract_ticks(c0, 6)

        # B. Formulasi Area BOW & BOB Secara Independen
        # 1. Parameter BOW (Buy On Weakness)
        bow_range_low = subtract_ticks(swing_low_real, 3)
        bow_range_high = add_ticks(swing_low_real, 3)
        bow_sl_price = subtract_ticks(bow_range_low, 3)

        # 2. Parameter BOB (Buy On Breakout) -> ENTRY SAAT NEMBUS TP1 (SWING HIGH 1)
        bob_range_low = tp1
        bob_range_high = add_ticks(tp1, 3)
        bob_sl_price = subtract_ticks(tp1, 3)

        # C. Evaluasi Kedekatan Posisi Untuk Menentukan Setup Utama (Rekomendasi)
        dist_to_low = abs(c0 - swing_low_real)
        dist_to_high = abs(tp1 - c0)

        if dist_to_low <= dist_to_high:
            rec_setup = "BUY ON WEAKNESS (BOW)"
            buy_range_low, buy_range_high = bow_range_low, bow_range_high
            sl_price = bow_sl_price
        else:
            rec_setup = "BUY ON BREAKOUT (BOB)"
            buy_range_low, buy_range_high = bob_range_low, bob_range_high
            sl_price = bob_sl_price

        # Deteksi Reversal Bad Signal / Breakdown
        is_marubozu_red = (c0 < o0) and ((o0 - c0) / (h0 - l0 + 1e-5) > 0.85)
        is_breakdown = is_marubozu_red or (c0 <= swing_low_real * 0.98)

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
            "rec_setup": rec_setup,
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
            "rr_1": rr_1, "rr_2": rr_2, "rr_3": rr_3,
            "vol_spike": (v0 >= vol_ma20),
            "entry_worst": entry_worst,
            "bow_range": f"Rp {int(bow_range_low):,} – Rp {int(bow_range_high):,}",
            "bow_sl": f"Rp {int(bow_sl_price):,}",
            "bob_range": f"Rp {int(bob_range_low):,} – Rp {int(bob_range_high):,}",
            "bob_sl": f"Rp {int(bob_sl_price):,}"
        }
    except Exception:
        return {"is_ihsg": False, "price": "-", "rec_setup": "-"}

@st.cache_data(ttl=600)
def get_ihsg_data():
    try:
        ihsg_df = yf.download("^JKSE", period="5d", interval="1d", progress=False)
        if isinstance(ihsg_df.columns, pd.MultiIndex): ihsg_df.columns = ihsg_df.columns.get_level_values(0)
        c_now = float(ihsg_df['Close'].iloc[-1])
        c_prev = float(ihsg_df['Close'].iloc[-2])
        return c_now, ((c_now - c_prev) / c_prev) * 100
    except:
        return 7000.0, 0.0

# 8. Render UI Header
col_brand, col_space, col_menu = st.columns([3, 3.7, 2.3])
with col_brand:
    if st.button("📈 Zio - Quant", key="home_btn"):
        reset_to_default()
        st.rerun()

with col_menu:
    selected_screener = st.selectbox("Pilih Screener", ["-- Pilih Screener --", "Stoch - Psar"], key="screener_choice", label_visibility="collapsed")

st.markdown("<hr style='margin-top: 2px; margin-bottom: 6px; border-color: #1E2D3D;'>", unsafe_allow_html=True)

# 9. Main Body
col_left, col_right = st.columns([1, 2.2], gap="medium")

# --- KIRI: WATCHLIST & SCREENER ---
with col_left:
    st.markdown("<p style='font-size: 11px; color: #64748B; font-weight: 600;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊 **IHSG** | {ihsg_price:,.2f} ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
        st.session_state.active_ticker = "IDX:COMPOSITE"
        st.session_state.screener_choice = "-- Pilih Screener --"
        st.rerun()

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

        with st.spinner("Memindai 150+ Saham..."):
            df_bull, df_bear = run_screener(SAHAM_LIST)

        with st.container(height=435):
            target_df = df_bull if st.session_state.watchlist_tab == "bull" else df_bear
            if not target_df.empty:
                for _, row in target_df.iterrows():
                    t_code, t_price, t_chg = row["Ticker"], row["Harga"], row["Chg"]
                    chg_sign = "+" if t_chg >= 0 else ""
                    if st.button(f"{t_code} | {t_price:,} | {chg_sign}{t_chg:.2f}%", key=f"btn_{t_code}", use_container_width=True):
                        st.session_state.active_ticker = f"IDX:{t_code}"
                        st.rerun()
            else:
                st.info("Tidak ada sinyal.")
    else:
        st.info("Silakan pilih screener di menu kanan atas.")

# --- KANAN: CHART / TRADE PLAN ---
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "IHSG" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol.replace("IDX:", "")
    tv_symbol = "IDX:COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol
    company_name = NAMA_PERUSAHAAN.get(clean_ticker, "Indeks Harga Saham Gabungan" if clean_ticker == "IHSG" else clean_ticker)

    c_title, c_b1, c_b2 = st.columns([2.5, 1, 1])
    with c_title:
        st.markdown(f"""
            <div class="ticker-header-card">
                <p class="ticker-header-text">Ticker : {clean_ticker}</p>
                <p class="company-name-text">{company_name}</p>
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

    # VIEW 1: TRADINGVIEW CHART
    if st.session_state.view_mode == "chart":
        tradingview_html = f"""
        <div class="tradingview-widget-container" style="height:535px;width:100%">
          <div id="tradingview_widget" style="height:100%;width:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true, "symbol": "{tv_symbol}", "interval": "D", "timezone": "Asia/Jakarta",
            "theme": "dark", "style": "1", "locale": "id", "container_id": "tradingview_widget"
          }});
          </script>
        </div>
        """
        st.components.v1.html(tradingview_html, height=540)

    # VIEW 2: TRADE PLAN MODUL (TERPERBARUI DENAGAN LOGIKA BENTENG FRACTAL)
    elif st.session_state.view_mode == "trade_plan":
        tp = get_stock_trade_plan(active_symbol)
        
        if tp.get("is_ihsg", False):
            st.info("ℹ️ **Indeks IHSG (Composite)** tidak memiliki Trade Plan individual.")
        else:
            st.markdown("##### 🟢 **1. STATUS CHART**")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 12px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 11px; margin: 0;">Ticker IDX</p>
                        <h3 style="color: #E2E8F0; margin: 2px 0; font-size: 20px;">{clean_ticker}</h3>
                    </div>
                """, unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 12px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 11px; margin: 0;">Last Price</p>
                        <h3 style="color: #E2E8F0; margin: 2px 0; font-size: 20px;">{tp['price']}</h3>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: #121E2B; border: 1px solid #243447; padding: 10px 14px; border-radius: 8px; margin-top: 8px;">
                    <p style="color: #64748B; font-size: 11px; margin: 0;">Rekomendasi Setup Utama (Berdasarkan Structural Reversal)</p>
                    <p style="color: #00E676; font-size: 14px; font-weight: bold; margin: 2px 0;">⚡ {tp['rec_setup']}</p>
                </div>
            """, unsafe_allow_html=True)

            if tp.get("is_breakdown", False):
                st.error("⛔ **RULE PENOLAKAN:** Saham Breakdown Support. Status: **SKIP / WAIT AND SEE**.")

            st.markdown("##### 🔵 **2. DETAIL TARGET RESISTANCE & SUPPORT STRUCTURAL**")
            
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #1E3A2F; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #00E676; font-size: 11px; font-weight: bold; margin: 0;">🟢 AREA ENTRY REKOMENDASI ({tp['rec_setup']})</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['buy_range']}</h4>
                    </div>
                """, unsafe_allow_html=True)
            with d2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #3A1E1E; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #FF5252; font-size: 11px; font-weight: bold; margin: 0;">🛑 STOP LOSS REKOMENDASI ({tp['risk_pct']})</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['sl_price']}</h4>
                    </div>
                """, unsafe_allow_html=True)

            # Rincian Angka BOW vs BOB Nyata
            st.markdown("<p style='font-size: 11px; color: #64748B; font-weight: bold;'>DETAIL STRATEGI OPERASIONAL (BOW VS BOB):</p>", unsafe_allow_html=True)
            ref_col1, ref_col2 = st.columns(2)
            with ref_col1:
                st.caption(f"📉 **Buy On Weakness (BOW)**:\nArea Beli: **{tp['bow_range']}** | SL: **{tp['bow_sl']}**")
            with ref_col2:
                st.caption(f"🚀 **Buy On Breakout (BOB)**:\nArea Beli: **{tp['bob_range']}** | SL: **{tp['bob_sl']}**")

            # Target Resistance (TP)
            t1, t2, t3 = st.columns(3)
            with t1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 1 (Swing High 1) | +{tp['reward_pct_1']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp1']}</h5>
                    </div>
                """, unsafe_allow_html=True)
            with t2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 2 (Swing High 2) | +{tp['reward_pct_2']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp2']}</h5>
                    </div>
                """, unsafe_allow_html=True)
            with t3:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 3 (Swing High 3) | +{tp['reward_pct_3']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp3']}</h5>
                    </div>
                """, unsafe_allow_html=True)
