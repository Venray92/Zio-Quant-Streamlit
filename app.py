import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import warnings

# Abaikan warning
warnings.filterwarnings('ignore')

# 1. Konfigurasi Halaman Full-Width & Dark Mode
st.set_page_config(
    page_title="ZioQuant - IDX Stock Screener & Chart",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk merapikan layout & tampilan ala Terminal/Stockbit
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    h1, h2, h3 {
        color: #e6edf3;
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

# 3. Fungsi Engine Screener dengan Cache agar Cepat
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

            # STOCHASTIC (10,5,5) - SMA SMOOTHING
            low_min10 = df['Low'].rolling(window=10).min()
            high_max10 = df['High'].rolling(window=10).max()
            fast_k = 100 * ((df['Close'] - low_min10) / (high_max10 - low_min10))
            
            df['stoch_k'] = fast_k.rolling(window=5).mean()
            df['stoch_d'] = df['stoch_k'].rolling(window=5).mean()

            # PARABOLIC SAR
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

            # 1. GOLDEN CROSS (GC) -> OVERSOLD (k0 < 35)
            if k0 < 35:
                gc_today = (k1 < d1) and (k0 >= d0)
                gc_yesterday = (k2 < d2) and (k1 >= d1) and (k0 >= d0)
                gc_2days_ago = (k3 < d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                gc_3days_ago = (k4 < d4) and (k3 >= d3) and (k2 >= d2) and (k1 >= d1) and (k0 >= d0)
                is_almost_gc = (k0 <= d0) and ((d0 - k0) <= 3.0)

                stoch_signal = None
                if gc_today:
                    stoch_signal = {"type": "GC Hari Ini (H-0)", "score": 80, "code": "H0"}
                elif gc_yesterday:
                    stoch_signal = {"type": "GC Kemarin (H-1)", "score": 70, "code": "H1_H3"}
                elif gc_2days_ago:
                    stoch_signal = {"type": "GC 2 Hari Lalu (H-2)", "score": 70, "code": "H1_H3"}
                elif gc_3days_ago:
                    stoch_signal = {"type": "GC 3 Hari Lalu (H-3)", "score": 70, "code": "H1_H3"}
                elif is_almost_gc:
                    stoch_signal = {"type": "Early Signal (Merapat)", "score": 55, "code": "EARLY"}

                if stoch_signal:
                    score = stoch_signal["score"]
                    notes = [stoch_signal['type']]

                    if psar0 < l0:
                        score += 20
                        notes.append("PSAR Bullish (+20)")
                    else:
                        notes.append("PSAR Bearish (+0)")

                    if v0 > vol_ma20_0:
                        score += 10 if stoch_signal["code"] == "H0" else 5
                        notes.append("Vol > MA20")

                    results_gc.append({
                        "Ticker": ticker.replace(".JK", ""),
                        "Harga": int(c0),
                        "Value (M)": round(val0 / 1_000_000_000, 2),
                        "Stoch %K": round(k0, 1),
                        "Stoch %D": round(d0, 1),
                        "Score": score,
                        "Action": "BELI / WATCHLIST",
                        "Detail Signal": " | ".join(notes)
                    })

            # 2. DEAD CROSS (DC) -> OVERBOUGHT (k0 >= 75)
            if k0 >= 75:
                dc_today = (k1 > d1) and (k0 <= d0)
                dc_yesterday = (k2 > d2) and (k1 <= d1) and (k0 <= d0)
                dc_2days_ago = (k3 > d3) and (k2 <= d2) and (k1 <= d1) and (k0 <= d0)
                dc_3days_ago = (k4 > d4) and (k3 >= d3) and (k2 <= d2) and (k1 <= d1) and (k0 <= d0)
                is_almost_dc = (k0 >= d0) and ((k0 - d0) <= 3.0)

                dc_signal = None
                if dc_today:
                    dc_signal = {"type": "DC Hari Ini (H-0)", "score": -80, "code": "H0"}
                elif dc_yesterday:
                    dc_signal = {"type": "DC Kemarin (H-1)", "score": -70, "code": "H1_H3"}
                elif dc_2days_ago:
                    dc_signal = {"type": "DC 2 Hari Lalu (H-2)", "score": -70, "code": "H1_H3"}
                elif dc_3days_ago:
                    dc_signal = {"type": "DC 3 Hari Lalu (H-3)", "score": -70, "code": "H1_H3"}
                elif is_almost_dc:
                    dc_signal = {"type": "Early DC Signal (Merapat)", "score": -55, "code": "EARLY"}

                if dc_signal:
                    score = dc_signal["score"]
                    notes = [dc_signal['type']]

                    if psar0 > h0:
                        score -= 20
                        notes.append("PSAR Bearish (-20)")
                    else:
                        notes.append("PSAR Bullish (0)")

                    if v0 > vol_ma20_0:
                        penalty = 10 if dc_signal["code"] == "H0" else 5
                        score -= penalty
                        notes.append(f"High Vol Sell (-{penalty})")

                    results_dc.append({
                        "Ticker": ticker.replace(".JK", ""),
                        "Harga": int(c0),
                        "Value (M)": round(val0 / 1_000_000_000, 2),
                        "Stoch %K": round(k0, 1),
                        "Stoch %D": round(d0, 1),
                        "Score": score,
                        "Action": "JUAL / EXIT",
                        "Detail Signal": " | ".join(notes)
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

# 4. Header Aplikasi
st.title("⚡ ZioQuant - Professional IDX Screener & Chart")
st.markdown("---")

# Ambil data hasil screener
with st.spinner("Menjalankan pemindaian pasar saham IDX..."):
    df_gc, df_dc = run_screener(SAHAM_LIST)

# 5. Layout Utama: Dibagi 2 Kolom (Kiri: Screener, Kanan: TradingView Chart)
col_left, col_right = st.columns([1.2, 1.8], gap="medium")

with col_left:
    st.subheader("🔍 Screener")
    
    tab_gc, tab_dc = st.tabs(["🟢 Golden Cross (BUY)", "🔴 Dead Cross (SELL)"])
    
    selected_ticker = "BBCA"  # Default ticker
    
    with tab_gc:
        if not df_gc.empty:
            # Gunakan st.dataframe dengan pemilihan baris interaktif
            selected_gc = st.dataframe(
                df_gc,
                use_container_width=True,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun"
            )
            
            # Cek jika baris dipilih
            if selected_gc and len(selected_gc.selection.rows) > 0:
                idx = selected_gc.selection.rows[0]
                selected_ticker = df_gc.iloc[idx]["Ticker"]
        else:
            st.info("Tidak ada saham memenuhi kriteria Golden Cross saat ini.")

    with tab_dc:
        if not df_dc.empty:
            selected_dc = st.dataframe(
                df_dc,
                use_container_width=True,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun"
            )
            
            if selected_dc and len(selected_dc.selection.rows) > 0:
                idx = selected_dc.selection.rows[0]
                selected_ticker = df_dc.iloc[idx]["Ticker"]
        else:
            st.info("Tidak ada saham memenuhi kriteria Dead Cross saat ini.")

with col_right:
    st.subheader(f"📊 Live Advanced Chart: IDX:{selected_ticker}")
    
    # Widget TradingView Advanced Real-Time Chart dengan Tools Lengkap
    tv_symbol = f"IDX:{selected_ticker}"
    
    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:650px;width:100%">
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
        "details": true,
        "hotlist": true,
        "calendar": true,
        "studies": [
          "Stochastic@tv-basicstudies",
          "ParabolicSAR@tv-basicstudies"
        ],
        "container_id": "tradingview_widget"
      }});
      </script>
    </div>
    """
    st.components.v1.html(tradingview_html, height=660)
