import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import warnings

warnings.filterwarnings('ignore')

# 1. Konfigurasi Halaman Full-Width & Dark Mode
st.set_page_config(
    page_title="Zio - Quant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Styling Card Stat Trade Plan */
    .tp-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Daftar Saham IDX
SAHAM_LIST = [
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
]
SAHAM_LIST = sorted(list(set(SAHAM_LIST)))

# 3. Engine Screener
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

            # STOCHASTIC (10, 5, 5)
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

            # Bullish
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

            # Bearish
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

# Ambil data statistik saham untuk Trade Plan
@st.cache_data(ttl=600)
def get_stock_details(symbol):
    try:
        yf_symbol = "^JKSE" if symbol == "^JKSE" else f"{symbol.replace('IDX:', '')}.JK"
        df = yf.download(yf_symbol, period="30d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        c0 = float(df['Close'].iloc[-1])
        low20 = float(df['Low'].min())
        high20 = float(df['High'].max())
        return c0, low20, high20
    except:
        return 1000.0, 950.0, 1100.0

# Ambil data IHSG
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

# 4. Header Bar
col_logo, col_title, col_space, col_menu = st.columns([0.3, 2.2, 4.2, 2.3])

with col_logo:
    st.markdown("<h2 style='margin: 0; padding-top: 2px;'>📈</h2>", unsafe_allow_html=True)

with col_title:
    st.markdown("<h3 style='margin: 0; padding-top: 6px; font-size: 17px; color: #e6edf3; font-weight: 700;'>Zio - Quant</h3>", unsafe_allow_html=True)

with col_menu:
    selected_screener = st.selectbox(
        "Pilih Screener",
        ["-- Pilih Screener --", "Stoch - Psar"],
        index=0,
        label_visibility="collapsed"
    )

st.markdown("<hr style='margin-top: 5px; margin-bottom: 12px; border-color: #30363d;'>", unsafe_allow_html=True)

# Session States
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "^JKSE"

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "chart"

# 5. Layout Utama
col_left, col_right = st.columns([1, 2.2], gap="medium")

# --- KIRI: WATCHLIST & SCREENER ---
with col_left:
    st.markdown("<p style='font-size: 12px; color: #8b949e; margin-bottom: 6px; font-weight: 600;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊  **IHSG**  |  {ihsg_price:,.2f}  ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
        st.session_state.active_ticker = "^JKSE"
        st.rerun()

    st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)

    if selected_screener == "Stoch - Psar":
        st.markdown("<p style='font-size: 12px; color: #58a6ff; font-weight: bold; margin-bottom: 4px;'>⚡ SCREENER: STOCH (10,5,5) - PSAR</p>", unsafe_allow_html=True)
        
        with st.spinner("Memindai pasar..."):
            df_bull, df_bear = run_screener(SAHAM_LIST)
            
        tab_bull, tab_bear = st.tabs(["🟢 Bullish", "🔴 Bearish"])
        
        with tab_bull:
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
                
        with tab_bear:
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
    else:
        st.markdown("<p style='font-size: 12px; color: #8b949e; font-style: italic;'>Pilih menu **Stoch - Psar** di kanan atas untuk menampilkan hasil screening.</p>", unsafe_allow_html=True)

# --- KANAN: DISPLAY CHART / TRADE PLAN ---
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "IHSG" if active_symbol == "^JKSE" else active_symbol.replace("IDX:", "")
    
    # Tombol Switcher: Chart vs Trade Plan
    c_title, c_b1, c_b2 = st.columns([2.5, 1, 1])
    with c_title:
        st.markdown(f"<p style='font-size: 16px; font-weight: bold; color: #58a6ff; margin: 0;'>{clean_ticker}</p>", unsafe_allow_html=True)
    with c_b1:
        if st.button("📈 Chart", use_container_width=True):
            st.session_state.view_mode = "chart"
            st.rerun()
    with c_b2:
        if st.button("📋 Trade Plan", use_container_width=True):
            st.session_state.view_mode = "trade_plan"
            st.rerun()

    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # TAMPILAN 1: CHART TRADINGVIEW BERSIH (TANPA INDIKATOR DEFAULT, ADA DRAWING TOOLS)
    if st.session_state.view_mode == "chart":
        tradingview_html = f"""
        <div class="tradingview-widget-container" style="height:600px;width:100%">
          <div id="tradingview_widget" style="height:100%;width:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
            "autosize": true,
            "symbol": "{active_symbol}",
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
        st.components.v1.html(tradingview_html, height=610)

    # TAMPILAN 2: HALAMAN TRADE PLAN DINAMIS
    elif st.session_state.view_mode == "trade_plan":
        c_price, supp_low, res_high = get_stock_details(active_symbol)
        
        # Kalkulasi Trade Plan
        entry_price = c_price
        stop_loss = int(supp_low * 0.98) # Support - 2%
        target_profit = int(entry_price + (entry_price - stop_loss) * 2) # Risk/Reward 1:2
        
        risk_pct = round(((entry_price - stop_loss) / entry_price) * 100, 2)
        reward_pct = round(((target_profit - entry_price) / entry_price) * 100, 2)
        rr_ratio = round(reward_pct / risk_pct, 2) if risk_pct > 0 else 0

        st.markdown(f"#### 📋 Trade Plan Kalkulator — `{clean_ticker}`")
        st.markdown("---")
        
        col_tp1, col_tp2, col_tp3 = st.columns(3)
        with col_tp1:
            st.metric("Harga Saat Ini (Entry)", f"Rp {int(entry_price):,}")
            st.metric("Risk / Loss (%)", f"-{risk_pct}%")
        with col_tp2:
            st.metric("Stop Loss (Cut Loss)", f"Rp {stop_loss:,}", delta=f"-{risk_pct}%", delta_color="inverse")
            st.metric("Reward / Gain (%)", f"+{reward_pct}%")
        with col_tp3:
            st.metric("Target Profit (TP)", f"Rp {target_profit:,}", delta=f"+{reward_pct}%")
            st.metric("Risk to Reward Ratio", f"1 : {rr_ratio}")

        st.markdown("---")
        st.markdown("##### 💡 Simulasi Alokasi Modal Trading")
        modal = st.number_input("Masukkan Modal Trading (Rp):", min_value=1_000_000, value=10_000_000, step=1_000_000)
        
        total_lot = int(modal // (entry_price * 100))
        total_buy = total_lot * entry_price * 100
        max_loss_rp = total_lot * 100 * (entry_price - stop_loss)
        max_gain_rp = total_lot * 100 * (target_profit - entry_price)

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.info(f"**Maksimal Pembelian:**\n\n**{total_lot} Lot** (Rp {int(total_buy):,})")
        c_m2.error(f"**Maksimal Risiko (Loss):**\n\n- Rp {int(max_loss_rp):,}")
        c_m3.success(f"**Potensi Profit (Gain):**\n\n+ Rp {int(max_gain_rp):,}")
