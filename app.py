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

# Custom CSS untuk merapikan padding atas agar header tidak terpotong
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

# 3. Engine Screener (Bullish & Bearish dengan Stoch 10,5,5 & PSAR)
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

            # 1. BULLISH (Golden Cross / Oversold)
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

            # 2. BEARISH (Dead Cross / Overbought)
            if k0 >= 75:
                dc_today = (k1 > d1) and (k0 <= d0)
                dc_yesterday = (k2 > d2) and (k1 <= d1) and (k0 <= d0)
                dc_2days_ago = (k3 > d3) and (k2 <= d2) and (k1 <= d1) and (k0 <= d0)
                dc_3days_ago = (k4 > d4) and (k3 >= d3) and (k2 <= d2) and (k1 <= d1) and (k0 <= d0)
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

# Fungsi ambil data IHSG terkini
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

# 4. Header Bar (Logo, Nama, Dropdown Menu)
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
        key="screener_dropdown",
        label_visibility="collapsed"
    )

st.markdown("<hr style='margin-top: 5px; margin-bottom: 12px; border-color: #30363d;'>", unsafe_allow_html=True)

# Session State untuk Menyimpan Ticker Aktif
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "^JKSE"

# 5. Layout Utama (Kiri: List IHSG & Screener, Kanan: TradingView Chart Bersih & Tombol Trade Plan)
col_left, col_right = st.columns([1, 2.2], gap="medium")

with col_left:
    st.markdown("<p style='font-size: 12px; color: #8b949e; margin-bottom: 6px; font-weight: 600;'>MARKET INDEX & WATCHLIST</p>", unsafe_allow_html=True)
    
    # IHSG Selalu di Posisi No. 1
    ihsg_price, ihsg_chg = get_ihsg_data()
    ihsg_sign = "+" if ihsg_chg >= 0 else ""
    
    if st.button(f"📊  **IHSG**  |  {ihsg_price:,.2f}  ({ihsg_sign}{ihsg_chg:.2f}%)", use_container_width=True):
        st.session_state.active_ticker = "^JKSE"
        st.rerun()

    st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)

    # Jika menu Stoch - Psar dipilih, tampilkan tab Bullish & Bearish di bawah IHSG
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

with col_right:
    # Tombol Trade Plan pengganti teks live chart
    col_empty, col_btn = st.columns([2.5, 1])
    with col_btn:
        if st.button("📋 Trade Plan", use_container_width=True):
            st.info("Modul Trade Plan aktif.")

    active_symbol = st.session_state.active_ticker
    
    # TradingView Chart dengan setting Stoch (10, 5, 5), PSAR, tanpa widget samping, dan volume disembunyikan agar bersih
    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:620px;width:100%">
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
        "details": false,
        "hotlist": false,
        "calendar": false,
        "studies": [
          "ParabolicSAR@tv-basicstudies",
          "Stochastic@tv-basicstudies"
        ],
        "studies_overrides": {{
          "ParabolicSAR.start": 0.02,
          "ParabolicSAR.increment": 0.02,
          "ParabolicSAR.max value": 0.2,
          "Stochastic.length": 10,
          "Stochastic.k smoothing": 5,
          "Stochastic.d smoothing": 5
        }},
        "disabled_features": [
          "volume_force_overlay"
        ],
        "container_id": "tradingview_widget"
      }});
      </script>
    </div>
    """
    st.components.v1.html(tradingview_html, height=630)
