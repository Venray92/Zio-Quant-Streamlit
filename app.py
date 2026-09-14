import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components
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
    .company-name-text {
        color: #94A3B8;
        font-size: 11px;
        margin-top: 2px;
        margin-bottom: 0px;
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
    </style>
""", unsafe_allow_html=True)

# 2. Inisialisasi Session State & Reset Function
def reset_to_default():
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

@st.cache_data(ttl=600)
def get_ihsg_data():
    try:
        df_ihsg = yf.download("^JKSE", period="5d", interval="1d", progress=False)
        if isinstance(df_ihsg.columns, pd.MultiIndex):
            df_ihsg.columns = df_ihsg.columns.get_level_values(0)
        c0 = float(df_ihsg['Close'].iloc[-1])
        c1 = float(df_ihsg['Close'].iloc[-2])
        chg_pct = ((c0 - c1) / c1) * 100
        return c0, chg_pct
    except Exception:
        return 7000.0, 0.0

# 3. Database Nama Perusahaan IDX
NAMA_PERUSAHAAN = {
    "AALI": "PT Astra Agro Lestari Tbk",
    "ACES": "PT Aspirasi Hidup Indonesia Tbk",
    "ADHI": "PT Adhi Karya (Persero) Tbk",
    "ADRO": "PT Adaro Energy Indonesia Tbk",
    "AGRO": "PT Bank Raya Indonesia Tbk",
    "AKRA": "PT AKR Corporindo Tbk",
    "AMMN": "PT Amman Mineral Internasional Tbk",
    "AMRT": "PT Sumber Alfaria Trijaya Tbk",
    "ANTM": "PT Aneka Tambang Tbk",
    "APLN": "PT Agung Podomoro Land Tbk",
    "ARTO": "PT Bank Jago Tbk",
    "ASII": "PT Astra International Tbk",
    "ASRI": "PT Alam Sutera Realty Tbk",
    "AUTO": "PT Astra Otoparts Tbk",
    "AVIA": "PT Avia Avian Tbk",
    "BBCA": "PT Bank Central Asia Tbk",
    "BBHI": "PT Allo Bank Indonesia Tbk",
    "BBNI": "PT Bank Negara Indonesia (Persero) Tbk",
    "BBRI": "PT Bank Rakyat Indonesia (Persero) Tbk",
    "BBTN": "PT Bank Tabungan Negara (Persero) Tbk",
    "BCIC": "PT Bank JTrust Indonesia Tbk",
    "BDMN": "PT Bank Danamon Indonesia Tbk",
    "BELI": "PT Global Digital Niaga Tbk (Blibli)",
    "BIRD": "PT Blue Bird Tbk",
    "BJBR": "PT Bank Pembangunan Daerah Jawa Barat dan Banten Tbk",
    "BJTM": "PT Bank Pembangunan Daerah Jawa Timur Tbk",
    "BMRI": "PT Bank Mandiri (Persero) Tbk",
    "BMTR": "PT Global Mediacom Tbk",
    "BNGA": "PT Bank CIMB Niaga Tbk",
    "BREN": "PT Barito Renewables Energy Tbk",
    "BRIS": "PT Bank Syariah Indonesia Tbk",
    "BRPT": "PT Barito Pacific Tbk",
    "BSDE": "PT Bumi Serpong Damai Tbk",
    "BUKA": "PT Bukalapak.com Tbk",
    "BUMI": "PT Bumi Resources Tbk",
    "BYAN": "PT Bayan Resources Tbk",
    "CITA": "PT Cita Mineral Investindo Tbk",
    "CLEO": "PT Sariguna Primatirta Tbk",
    "CMRY": "PT Cisarua Mountain Dairy Tbk",
    "CPIN": "PT Charoen Pokphand Indonesia Tbk",
    "CTRA": "PT Ciputra Development Tbk",
    "CUAN": "PT Petrindo Jaya Kreasi Tbk",
    "DCII": "PT DCI Indonesia Tbk",
    "DEWA": "PT Darma Henwa Tbk",
    "DILD": "PT Intiland Development Tbk",
    "DKFT": "PT Central Omega Resources Tbk",
    "DOID": "PT Delta Dunia Makmur Tbk",
    "DRMA": "PT Dharma Polimetal Tbk",
    "DSNG": "PT Dharma Satya Nusantara Tbk",
    "EAST": "PT Eastparc Hotel Tbk",
    "EDGE": "PT Indointernet Tbk",
    "ELSA": "PT Elnusa Tbk",
    "EMTK": "PT Elang Mahkota Teknologi Tbk",
    "ENRG": "PT Energi Mega Persada Tbk",
    "ESSA": "PT ESSA Industries Indonesia Tbk",
    "EXCL": "PT XL Axiata Tbk",
    "FILM": "PT MD Pictures Tbk",
    "GEMS": "PT Golden Energy Mines Tbk",
    "GJTL": "PT Gajah Tunggal Tbk",
    "GOTO": "PT GoTo Gojek Tokopedia Tbk",
    "HAIS": "PT Hasnur Internasional Shipping Tbk",
    "HEAL": "PT Medikaloka Hermina Tbk",
    "HRUM": "PT Harum Energy Tbk",
    "ICBP": "PT Indofood CBP Sukses Makmur Tbk",
    "INAF": "PT Indofarma Tbk",
    "INCO": "PT Vale Indonesia Tbk",
    "INDF": "PT Indofood Sukses Makmur Tbk",
    "INDY": "PT Indika Energy Tbk",
    "INKP": "PT Indah Kiat Pulp & Paper Tbk",
    "INTP": "PT Indocement Tunggal Prakarsa Tbk",
    "IPCC": "PT Indonesia Kendaraan Terminal Tbk",
    "IPCM": "PT Jasa Armada Indonesia Tbk",
    "IRRA": "PT Itama Ranoraya Tbk",
    "ISAT": "PT Indosat Tbk (Indosat Ooredoo Hutchison)",
    "ITMG": "PT Indo Tambangraya Megah Tbk",
    "JKON": "PT Jaya Konstruksi Manggala Pratama Tbk",
    "JPFA": "PT Japfa Comfeed Indonesia Tbk",
    "JSPT": "PT Jakarta Setiabudi Internasional Tbk",
    "KAEF": "PT Kimia Farma Tbk",
    "KEEN": "PT Kencana Energi Lestari Tbk",
    "KIJA": "PT Kawasan Industri Jababeka Tbk",
    "KLBF": "PT Kalbe Farma Tbk",
    "LEAD": "PT Logindo Samudramakmur Tbk",
    "LSIP": "PT PP London Sumatra Indonesia Tbk",
    "MAIN": "PT Malindo Feedmill Tbk",
    "MAPA": "PT Map Aktif Adiperkasa Tbk",
    "MAPI": "PT Mitra Adiperkasa Tbk",
    "MBAP": "PT Mitrabara Adiperdana Tbk",
    "MBMA": "PT Merdeka Battery Materials Tbk",
    "MCAS": "PT M Cash Integrasi Tbk",
    "MDKA": "PT Merdeka Copper Gold Tbk",
    "MEDC": "PT Medco Energi Internasional Tbk",
    "MEDS": "PT Hetzer Medical Indonesia Tbk",
    "MIKA": "PT Mitra Keluarga Karyasehat Tbk",
    "MNCN": "PT Media Nusantara Citra Tbk",
    "MPMX": "PT Mitra Pinasthika Mustika Tbk",
    "MTDL": "PT Metrodata Electronics Tbk",
    "MYOR": "PT Mayora Indah Tbk",
    "NCKL": "PT Trimegah Bangun Persada Tbk",
    "NELY": "PT Pelayaran Nelly Dwi Putri Tbk",
    "NRCA": "PT Nusa Raya Cipta Tbk",
    "PANI": "PT Pantai Indah Kapuk Dua Tbk",
    "PANR": "PT Panorama Sentrawisata Tbk",
    "PGAS": "PT Perusahaan Gas Negara Tbk",
    "PGEO": "PT Pertamina Geothermal Energy Tbk",
    "PNBN": "PT Bank Pan Indonesia Tbk",
    "POWR": "PT Cikarang Listrindo Tbk",
    "PRDA": "PT Prodia Widyahusada Tbk",
    "PSAB": "PT J Resources Asia Pasifik Tbk",
    "PSSI": "PT Pelita Samudera Shipping Tbk",
    "PTBA": "PT Bukit Asam Tbk",
    "PTPP": "PT PP (Persero) Tbk",
    "PWON": "PT Pakuwon Jati Tbk",
    "RAAM": "PT Tripar Multivision Plus Tbk",
    "RALS": "PT Ramayana Lestari Sentosa Tbk",
    "SAME": "PT Sarana Meditama Metropolitan Tbk",
    "SCMA": "PT Surya Citra Media Tbk",
    "SIDO": "PT Industri Jamu dan Farmasi Sido Muncul Tbk",
    "SILO": "PT Siloam International Hospitals Tbk",
    "SMBR": "PT Semen Baturaja Tbk",
    "SMDR": "PT Samudera Indonesia Tbk",
    "SMGR": "PT Semen Indonesia (Persero) Tbk",
    "SMRA": "PT Summarecon Agung Tbk",
    "SMSM": "PT Selamat Sempurna Tbk",
    "SSIA": "PT Surya Semesta Internusa Tbk",
    "SSMS": "PT Sawit Sumbermas Sarana Tbk",
    "STAA": "PT Sumber Tani Agung Resources Tbk",
    "TAPG": "PT Triputra Agro Persada Tbk",
    "TBIG": "PT Tower Bersama Infrastructure Tbk",
    "TCPI": "PT Transcoal Pacific Tbk",
    "TINS": "PT Timah Tbk",
    "TKIM": "PT Pabrik Kertas Tjiwi Kimia Tbk",
    "TLKM": "PT Telkom Indonesia (Persero) Tbk",
    "TMAS": "PT Temas Tbk",
    "TOBA": "PT Toba Bara Sejahtra Tbk",
    "TOTL": "PT Total Bangun Persada Tbk",
    "TOWR": "PT Sarana Menara Nusantara Tbk",
    "TPIA": "PT Chandra Asri Pacific Tbk",
    "TSPC": "PT Tempo Scan Pacific Tbk",
    "UNTR": "PT United Tractors Tbk",
    "UNVR": "PT Unilever Indonesia Tbk",
    "WEGE": "PT Wijaya Karya Bangunan Gedung Tbk",
    "WIFI": "PT Solusi Sinergi Digital Tbk",
    "WIKA": "PT Wijaya Karya (Persero) Tbk",
    "WINS": "PT Wintermar Off Shore Marine Tbk",
    "WOOD": "PT Integra Indocabinet Tbk"
}

SAHAM_LIST = sorted(list(NAMA_PERUSAHAAN.keys()))

# 4. Helper Fraksi Harga BEI
def get_tick_size(price):
    if price < 200: return 1
    elif price < 500: return 2
    elif price < 2000: return 5
    elif price < 5000: return 10
    else: return 25

def round_to_bei_tick(price):
    if price <= 0 or pd.isna(price): return 0
    tick = get_tick_size(price)
    return float(round(price / tick) * tick)

def add_ticks(price, num_ticks):
    curr = float(price)
    for _ in range(abs(num_ticks)):
        tick = get_tick_size(curr)
        curr += tick if num_ticks > 0 else -tick
    return round_to_bei_tick(curr)

def subtract_ticks(price, num_ticks):
    return add_ticks(price, -num_ticks)

# 5. Engine Screener
@st.cache_data(ttl=3600)
def run_screener(tickers):
    results_gc = []
    results_dc = []
    for ticker in tickers:
        try:
            yf_ticker = f"{ticker}.JK"
            df = yf.download(yf_ticker, period="90d", interval="1d", progress=False)
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
                        "Ticker": ticker, 
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
                        "Ticker": ticker, 
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

# 6. Trade Plan Engine Komplet Sesuai Versi Lama dengan Sorting & Periode yang Akurat
@st.cache_data(ttl=600)
def get_comprehensive_trade_plan(symbol):
    clean_code = symbol.replace('IDX:', '').replace('.JK', '').upper()
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {"is_ihsg": True}

    try:
        yf_symbol = f"{clean_code}.JK"
        df = yf.download(yf_symbol, period="180d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty or len(df) < 30:
            return {"is_ihsg": False, "error": "Data historis tidak cukup."}

        # Kalkulasi Swing Points
        window = 4
        swing_highs_rows = []
        swing_lows_rows = []
        highs = df['High'].values
        lows = df['Low'].values
        opens = df['Open'].values
        closes = df['Close'].values
        dates = df.index

        for i in range(window, len(df) - window):
            if all(highs[i] > highs[i - j] for j in range(1, window + 1)) and \
               all(highs[i] >= highs[i + j] for j in range(1, window + 1)):
                op, hi, lo, cl = opens[i], highs[i], lows[i], closes[i]
                body_top = max(op, cl)
                met = f"{body_top}" if body_top == hi else "-"
                swing_highs_rows.append({
                    "Date": dates[i],
                    "Open": round_to_bei_tick(op),
                    "High": round_to_bei_tick(hi),
                    "Low": round_to_bei_tick(lo),
                    "Close": round_to_bei_tick(cl),
                    "Swing_Type": "Swing High",
                    "metpoint": met
                })

            if all(lows[i] < lows[i - j] for j in range(1, window + 1)) and \
               all(lows[i] <= lows[i + j] for j in range(1, window + 1)):
                op, hi, lo, cl = opens[i], highs[i], lows[i], closes[i]
                body_bot = min(op, cl)
                met = f"{body_bot}" if body_bot == lo else "-"
                swing_lows_rows.append({
                    "Date": dates[i],
                    "Open": round_to_bei_tick(op),
                    "High": round_to_bei_tick(hi),
                    "Low": round_to_bei_tick(lo),
                    "Close": round_to_bei_tick(cl),
                    "Swing_Type": "Swing Low",
                    "metpoint": met
                })

        df_sh = pd.DataFrame(swing_highs_rows)
        df_sl = pd.DataFrame(swing_lows_rows)

        # Pastikan ter-sort descending (terbaru di atas)
        if not df_sh.empty:
            df_sh = df_sh.sort_values(by="Date", ascending=False).reset_index(drop=True)
        if not df_sl.empty:
            df_sl = df_sl.sort_values(by="Date", ascending=False).reset_index(drop=True)
        
        # Gabungkan tabel swing points
        df_swings = pd.concat([df_sh.head(15), df_sl.head(15)], ignore_index=True)
        df_swings.insert(0, "No", range(1, len(df_swings) + 1))

        # Strong Resistance (ambil 2 Swing High terbaru)
        strong_res = []
        if not df_sh.empty:
            top_sh = df_sh.head(2)
            ranks = ["1st Highest (Utama)", "2nd Highest (Kedua)"]
            for idx, row in enumerate(top_sh.itertuples()):
                strong_res.append({
                    "Date": row.Date.strftime('%Y-%m-%d') if hasattr(row.Date, 'strftime') else str(row.Date)[:10],
                    "Rank": ranks[idx],
                    "Body_Top": max(row.Open, row.Close),
                    "High": row.High
                })
        df_strong_res = pd.DataFrame(strong_res)

        # Strong Support (ambil 2 Swing Low terbaru)
        strong_sup = []
        if not df_sl.empty:
            bot_sl = df_sl.head(2)
            ranks_sup = ["1st Support (Terdekat)", "2nd Support"]
            for idx, row in enumerate(bot_sl.itertuples()):
                strong_sup.append({
                    "Date": row.Date.strftime('%Y-%m-%d') if hasattr(row.Date, 'strftime') else str(row.Date)[:10],
                    "Rank": ranks_sup[idx],
                    "Low": row.Low,
                    "Body_Bottom": min(row.Open, row.Close)
                })
        df_strong_sup = pd.DataFrame(strong_sup)

        # Direction Table
        sh_update = float(df_sh['High'].iloc[0]) if not df_sh.empty else float(df['High'].max())
        sl_update = float(df_sl['Low'].iloc[0]) if not df_sl.empty else float(df['Low'].min())
        level_50 = round_to_bei_tick((sh_update + sl_update) / 2)
        last_close = round_to_bei_tick(float(df['Close'].iloc[-1]))
        mkt_dir = "BOW" if last_close < level_50 else "BOB"

        df_direction = pd.DataFrame([{
            "Swing High Terupdate": sh_update,
            "Swing Low Terupdate": sl_update,
            "Level 50%": level_50,
            "Last Close": last_close,
            "Market Direction": mkt_dir
        }])

        # Trade Plan Table
        c0 = last_close
        o0 = round_to_bei_tick(float(df['Open'].iloc[-1]))
        
        # Status Candle & Warning
        if c0 > o0:
            status_candle = "Bullish Engulfing"
            warning_msg = "💡 Sinyal: Pembeli mengambil alih. Sinyal pembalikan arah naik cukup valid."
        else:
            status_candle = "Bearish Candle"
            warning_msg = "⚠️ Sinyal: Tekanan jual masih mendominasi, perhatikan area support terdekat."

        tp1_val = float(df_strong_res['High'].iloc[0]) if not df_strong_res.empty else round_to_bei_tick(c0 * 1.1)
        tp2_val = float(df_strong_res['High'].iloc[1]) if len(df_strong_res) > 1 else round_to_bei_tick(tp1_val * 1.05)

        bow_buy_low = sl_update
        bow_buy_high = round_to_bei_tick(sl_update + ((sh_update - sl_update) * 0.15))
        bow_sl = subtract_ticks(bow_buy_low, 3)
        bow_rr = round((tp1_val - bow_buy_high) / (bow_buy_high - bow_sl), 1) if (bow_buy_high - bow_sl) > 0 else 5.0

        bob_buy_low = sh_update
        bob_buy_high = add_ticks(sh_update, 3)
        bob_sl = subtract_ticks(sh_update, 3)
        bob_rr = round((tp2_val - bob_buy_high) / (bob_buy_high - bob_sl), 1) if (bob_buy_high - bob_sl) > 0 else 5.0

        trade_plans = [
            {
                "No": 1,
                "Type": "BOW",
                "Range Buy": f"{int(bow_buy_low)} - {int(bow_buy_high)}",
                "Stop Loss": int(bow_sl),
                "Target 1": int(tp1_val),
                "Target 2": int(tp2_val),
                "Rasio (R:R)": f"1 : {bow_rr}",
                "Status Candle": status_candle,
                "Warning": warning_msg
            },
            {
                "No": 2,
                "Type": "BOB",
                "Range Buy": f"{int(bob_buy_low)} - {int(bob_buy_high)}",
                "Stop Loss": int(bob_sl),
                "Target 1": int(tp1_val),
                "Target 2": int(tp2_val),
                "Rasio (R:R)": f"1 : {bob_rr}",
                "Status Candle": status_candle,
                "Warning": warning_msg
            }
        ]
        df_trade_plans = pd.DataFrame(trade_plans)

        return {
            "is_ihsg": False,
            "ticker": clean_code,
            "df_swings": df_swings,
            "df_strong_res": df_strong_res,
            "df_strong_sup": df_strong_sup,
            "df_direction": df_direction,
            "df_trade_plans": df_trade_plans
        }
    except Exception as e:
        return {"is_ihsg": False, "error": str(e)}

# 7. Header Navigation
col_brand, col_space, col_menu = st.columns([3, 3.7, 2.3])

with col_brand:
    if st.button("📈 Zio - Quant", key="home_btn"):
        reset_to_default()
        st.rerun()

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

# 9. Kolom Kanan: Chart / Trade Plan Komplet
with col_right:
    active_symbol = st.session_state.active_ticker
    clean_ticker = "IHSG" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol.replace("IDX:", "")
    tv_symbol = "IDX:COMPOSITE" if active_symbol in ["^JKSE", "IDX:COMPOSITE"] else active_symbol

    company_name = NAMA_PERUSAHAAN.get(clean_ticker, "Indeks Harga Saham Gabungan (Composite Index)" if clean_ticker == "IHSG" else clean_ticker)

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

    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)

    if st.session_state.view_mode == "chart":
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:550px;width:100%">
          <div id="tradingview_widget" style="height:100%;width:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
            "width": "100%",
            "height": "550",
            "symbol": "{tv_symbol}",
            "interval": "D",
            "timezone": "Asia/Jakarta",
            "theme": "dark",
            "style": "1",
            "locale": "id",
            "toolbar_bg": "#121E2B",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": false,
            "watchlist": [
              "IDX:BBCA",
              "IDX:BBRI",
              "IDX:BMRI",
              "IDX:BBNI",
              "IDX:ASII",
              "IDX:TLKM",
              "IDX:GOTO"
            ],
            "details": true,
            "hotlist": true,
            "calendar": false,
            "studies": [
              "MASimple@tv-basicstudies",
              "Volume@tv-basicstudies"
            ],
            "container_id": "tradingview_widget"
          }}
          );
          </script>
        </div>
        """
        components.html(tv_html, height=560)
        
    elif st.session_state.view_mode == "trade_plan":
        plan = get_comprehensive_trade_plan(active_symbol)
        if plan.get("is_ihsg"):
            st.info("Trade Plan otomatis khusus untuk saham individual IDX. IHSG adalah indeks komposit.")
        elif "error" in plan:
            st.error(f"Gagal memuat trade plan: {plan['error']}")
        else:
            st.markdown(f"### === TABEL SWING POINTS ===")
            st.dataframe(plan["df_swings"], use_container_width=True, hide_index=True)

            col_res, col_sup = st.columns(2)
            with col_res:
                st.markdown(f"### === STRONG RESISTANCE ===")
                st.dataframe(plan["df_strong_res"], use_container_width=True, hide_index=True)
            with col_sup:
                st.markdown(f"### === STRONG SUPPORT ===")
                st.dataframe(plan["df_strong_sup"], use_container_width=True, hide_index=True)

            st.markdown(f"### === TABEL DIRECTION ===")
            st.dataframe(plan["df_direction"], use_container_width=True, hide_index=True)

            st.markdown(f"### === TABEL TRADE PLAN ===")
            st.dataframe(plan["df_trade_plans"], use_container_width=True, hide_index=True)
