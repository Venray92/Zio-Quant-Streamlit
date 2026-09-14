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

    div.stButton > button.brand-btn {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        text-align: left !important;
        box-shadow: none !important;
    }
    div.stButton > button.brand-btn:hover {
        background: transparent !important;
        border: none !important;
        opacity: 0.8;
    }

    /* CUSTOM CARDS UI */
    .tp-card {
        background-color: #111A24;
        border: 1px solid #1E2D3D;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .tp-card-green {
        background-color: #0D201A;
        border: 1px solid #00E676;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .tp-card-red {
        background-color: #261418;
        border: 1px solid #FF5252;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .tp-card-blue {
        background-color: #101E2E;
        border: 1px solid #00B0FF;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .tp-badge-green {
        background-color: #00E67622;
        color: #00E676;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .tp-badge-red {
        background-color: #FF525222;
        color: #FF5252;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .tp-badge-blue {
        background-color: #00B0FF22;
        color: #00B0FF;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .tp-badge-gold {
        background-color: #FFD70022;
        color: #FFD700;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid #FFD700;
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

# Helper Data IHSG (Penambahan Fungsi yang Hilang)
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

# 3. Database Nama Lengkap Perusahaan IDX
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

SAHAM_LIST = sorted(list(set(NAMA_PERUSAHAAN.keys())))

# 4. Helper Fraksi Harga BEI
def get_tick_size(price):
    if price < 200: return 1
    elif price < 500: return 2
    elif price < 2000: return 5
    elif price < 5000: return 10
    else: return 25

def round_to_bei_tick(price):
    tick = get_tick_size(price)
    return float(round(price / tick) * tick)

def add_ticks(price, num_ticks):
    curr = float(price)
    for _ in range(num_ticks):
        curr += get_tick_size(curr)
    return round_to_bei_tick(curr)

def subtract_ticks(price, num_ticks):
    curr = float(price)
    for _ in range(num_ticks):
        curr -= get_tick_size(curr)
    return max(1.0, round_to_bei_tick(curr))

# 5. Helper Deteksi Reversal / Swing Structural
def find_swing_points(df, window=4):
    swing_highs = []
    swing_lows = []
    
    highs = df['High'].values
    lows = df['Low'].values
    n = len(df)
    
    for i in range(window, n - window):
        if all(highs[i] > highs[i - j] for j in range(1, window + 1)) and \
           all(highs[i] >= highs[i + j] for j in range(1, window + 1)):
            swing_highs.append(round_to_bei_tick(highs[i]))
            
        if all(lows[i] < lows[i - j] for j in range(1, window + 1)) and \
           all(lows[i] <= lows[i + j] for j in range(1, window + 1)):
            swing_lows.append(round_to_bei_tick(lows[i]))
            
    return swing_highs, swing_lows

# 6. Engine Screener
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

# 7.trade plan

# ==========================================
# MASTER TRADE PLAN ENGINE (BEI SPEC)
# ==========================================
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
    curr = price
    for _ in range(abs(num_ticks)):
        tick = get_tick_size(curr)
        curr += tick if num_ticks > 0 else -tick
    return float(curr)

def subtract_ticks(price, num_ticks):
    return add_ticks(price, -num_ticks)

@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    clean_code = symbol.replace('IDX:', '').replace('.JK', '').upper()
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {"is_ihsg": True}

    try:
        yf_symbol = f"{clean_code}.JK"
        df = yf.download(yf_symbol, period="90d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty or len(df) < 25:
            return {"is_ihsg": False, "error": "Data historis tidak cukup."}

        df_base = df.iloc[-21:-1] 
        c0 = round_to_bei_tick(float(df['Close'].iloc[-1]))
        o0 = round_to_bei_tick(float(df['Open'].iloc[-1]))
        h0 = round_to_bei_tick(float(df['High'].iloc[-1]))
        l0 = round_to_bei_tick(float(df['Low'].iloc[-1]))
        v0 = float(df['Volume'].iloc[-1])
        v_ma20 = float(df['Volume'].tail(20).mean())

        base_wick_high = round_to_bei_tick(float(df_base['High'].max()))
        base_wick_low = round_to_bei_tick(float(df_base['Low'].min()))
        base_low_body = round_to_bei_tick(float(df_base[['Open', 'Close']].min().min()))

        # EVALUASI RULE D
        rejected = False
        rejection_reasons = []

        if c0 < base_wick_low:
            rejected = True
            rejection_reasons.append("Breakdown Support Utama (Close < Wick Low Base)")

        candle_range = h0 - l0
        body_size = abs(c0 - o0)
        body_ratio = (body_size / candle_range) if candle_range > 0 else 0
        close_near_low = (c0 <= (l0 + (candle_range * 0.20)))

        if (c0 < o0) and (body_ratio > 0.80) and close_near_low:
            rejected = True
            rejection_reasons.append("Solid Bearish Marubozu (Falling Knife)")

        is_bob = (c0 > base_wick_high)
        if not is_bob:
            lower_wick = min(c0, o0) - l0
            has_lower_rejection = lower_wick > (candle_range * 0.35)
            is_green_candle = (c0 > o0)
            if not (has_lower_rejection or is_green_candle):
                rejected = True
                rejection_reasons.append("Tidak Ada Rejection di Support (BOW)")

        # JIKA DITOLAK RULE D
        if rejected:
            return {
                "is_ihsg": False,
                "ticker": clean_code,
                "close_price": f"Rp {int(c0):,}",
                "rule_d_status": "REJECTED",
                "rule_d_reason": " | ".join(rejection_reasons),
                "selected_strategy": "WAIT AND SEE",
                "volume_note": "N/A",
                "entry_range": "-",
                "worst_case_entry": "-",
                "sl_price": "-",
                "max_risk_pct": "-",
                "max_risk_status": "INVALID",
                "targets": []
            }

        # LOGIKA STRATEGI (BOB / BOW)
        if is_bob:
            selected_strategy = "BUY ON BREAKOUT (BOB)"
            vol_passed = v0 > v_ma20
            vol_note = "✅ Volume > MA20 (Valid)" if vol_passed else "⚠️ Volume < MA20 (Weak)"
            entry_low = add_ticks(base_wick_high, 1)
            entry_high = add_ticks(base_wick_high, 3)
            worst_case_entry = entry_high
            sl_price = subtract_ticks(base_wick_high, 3)
            max_risk_limit = 5.0
        else:
            selected_strategy = "BUY ON WEAKNESS (BOW)"
            vol_note = "ℹ️ Pelemahan Volume (Dry Up)"
            tick_sz = get_tick_size(base_low_body)
            gap_ticks = int((base_low_body - base_wick_low) / tick_sz)
            
            if gap_ticks > 5:
                entry_low = base_wick_low
                entry_high = add_ticks(base_wick_low, 5)
            else:
                entry_low = base_wick_low
                entry_high = base_low_body
                
            worst_case_entry = entry_high
            sl_price = subtract_ticks(base_wick_low, 3)
            max_risk_limit = 8.0

        risk_pts = worst_case_entry - sl_price
        max_risk_pct = round((risk_pts / worst_case_entry) * 100, 2)
        risk_status = "✅ RISIKO AMAN" if max_risk_pct <= max_risk_limit else f"⚠️ RISIKO TINGGI (> {max_risk_limit}%)"

        # TARGET PRICING
        base_height = base_wick_high - base_wick_low
        tp1 = round_to_bei_tick(worst_case_entry + base_height)
        
        df_40 = df.tail(40)
        r2_major = round_to_bei_tick(float(df_40['High'].max()))
        tp2 = max(r2_major, add_ticks(tp1, 10))
        
        tp3 = round_to_bei_tick(worst_case_entry + (base_height * 1.618))
        tp3 = max(tp3, add_ticks(tp2, 10))

        raw_targets = [
            ("Target 1 (Fast Swing)", tp1, "Measured Move Base", "Fast Swing"),
            ("Target 2 (Medium Swing)", tp2, "Major Resistance (40H)", "Medium Swing"),
            ("Target 3 (Long Swing)", tp3, "Fibo Extension 1.618", "Trend Following")
        ]

        targets_table = []
        for label, tp_price, basis, style in raw_targets:
            reward_pts = tp_price - worst_case_entry
            gain_pct = round((reward_pts / worst_case_entry) * 100, 2)
            rr_ratio = round(reward_pts / risk_pts, 2) if risk_pts > 0 else 0
            
            if rr_ratio < 2.00: rr_label = "⚠️ TIDAK SESUAI R:R"
            elif 2.00 <= rr_ratio <= 2.99: rr_label = "✅ LAYAK"
            else: rr_label = "✅ SANGAT LAYAK"

            targets_table.append({
                "target_label": label,
                "target_price": f"Rp {int(tp_price):,}",
                "target_basis": basis,
                "potential_gain_pct": f"+{gain_pct}%",
                "risk_points": f"Rp {int(risk_pts)}",
                "reward_points": f"Rp {int(reward_pts)}",
                "rr_ratio": f"1 : {rr_ratio}",
                "rr_status_label": rr_label,
                "suitable_trading_style": style
            })

        return {
            "is_ihsg": False,
            "ticker": clean_code,
            "close_price": f"Rp {int(c0):,}",
            "rule_d_status": "PASSED",
            "rule_d_reason": "Lolos Semua Filter Rule D",
            "selected_strategy": selected_strategy,
            "volume_note": vol_note,
            "entry_range": f"Rp {int(entry_low):,} – Rp {int(entry_high):,}",
            "worst_case_entry": f"Rp {int(worst_case_entry):,}",
            "sl_price": f"Rp {int(sl_price):,}",
            "max_risk_pct": f"-{max_risk_pct}%",
            "max_risk_status": risk_status,
            "targets": targets_table
        }
    except Exception as e:
        return {"is_ihsg": False, "error": str(e)}

# 8. Header Navigation
col_brand, col_space, col_menu = st.columns([3, 3.7, 2.3])

with col_brand:
    if st.button("📈 Zio - Quant", key="home_btn", help="Reset ke Home / Default View"):
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

# 9. Layout Utama (2 Kolom)
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

 
    # --------------------------------------------------
    # BLOCK 1: OVERVIEW & STATUS RULE D
    # --------------------------------------------------
    st.markdown("<p style='font-size: 13px; color: #00E676; font-weight: bold; margin-bottom: 8px;'>🎯 1. STATUS CHART & EKSEKUSI</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class="tp-card">
                <p style="color: #64748B; font-size: 11px; margin: 0;">Ticker IDX</p>
                <h2 style="color: #FFFFFF; margin: 4px 0; font-weight: 800;">{tp['ticker']}</h2>
                <p style="color: #64748B; font-size: 11px; margin: 0;">Harga Close: <b>{tp['close_price']}</b></p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        status_color = "#00E676" if tp['rule_d_status'] == "PASSED" else "#FF5252"
        st.markdown(f"""
            <div class="tp-card">
                <p style="color: #64748B; font-size: 11px; margin: 0;">Status Rule D / Validasi</p>
                <h3 style="color: {status_color}; margin: 4px 0; font-weight: 700;">{tp['rule_d_status']}</h3>
                <p style="color: #94A3B8; font-size: 11px; margin: 0;">{tp['rule_d_reason']}</p>
            </div>
        """, unsafe_allow_html=True)

    # CHECKPOINT: HANYA TAMPILKAN BLOCK 2 & 3 JIKA STATUS PASSED
    if tp['rule_d_status'] == "REJECTED":
        st.warning("⚠️ **TRADE PLAN DITOLAK**: Saham ini tidak memenuhi syarat masuk (Breakdown Support / Falling Knife). Disarankan **WAIT AND SEE**.")
    else:
        # --------------------------------------------------
        # BLOCK 2: HARGA & PARAMETER TRADE PLAN
        # --------------------------------------------------
        st.markdown("<p style='font-size: 13px; color: #00E676; font-weight: bold; margin-top: 15px; margin-bottom: 8px;'>📊 2. HARGA & PARAMETER TRADE PLAN</p>", unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.markdown(f"""
                <div class="tp-card-blue">
                    <p style="color: #00B0FF; font-size: 11px; margin: 0; font-weight: bold;">STRATEGI: {tp['selected_strategy']}</p>
                    <h3 style="color: #FFFFFF; margin: 4px 0;">{tp['entry_range']}</h3>
                    <p style="color: #94A3B8; font-size: 11px; margin: 0;">Worst Entry: {tp['worst_case_entry']}</p>
                </div>
            """, unsafe_allow_html=True)
        with pc2:
            st.markdown(f"""
                <div class="tp-card-red">
                    <p style="color: #FF5252; font-size: 11px; margin: 0; font-weight: bold;">STOP LOSS (SL)</p>
                    <h3 style="color: #FFFFFF; margin: 4px 0;">{tp['sl_price']}</h3>
                    <p style="color: #FF5252; font-size: 11px; margin: 0;">Max Risk: {tp['max_risk_pct']}</p>
                </div>
            """, unsafe_allow_html=True)
        with pc3:
            st.markdown(f"""
                <div class="tp-card-green">
                    <p style="color: #00E676; font-size: 11px; margin: 0; font-weight: bold;">EVALUASI RISIKO</p>
                    <h4 style="color: #FFFFFF; margin: 6px 0;">{tp['max_risk_status']}</h4>
                    <p style="color: #94A3B8; font-size: 11px; margin: 0;">{tp['volume_note']}</p>
                </div>
            """, unsafe_allow_html=True)

        # --------------------------------------------------
        # BLOCK 3: SCALING OUT TARGET & RATIO R:R
        # --------------------------------------------------
        st.markdown("<p style='font-size: 13px; color: #00E676; font-weight: bold; margin-top: 15px; margin-bottom: 8px;'>🎯 3. SCALING OUT TARGET & RATIO R:R</p>", unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        cols = [tc1, tc2, tc3]
        for idx, target in enumerate(tp['targets']):
            with cols[idx]:
                st.markdown(f"""
                    <div class="tp-card">
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">{target['target_label']}</p>
                        <h3 style="color: #FFFFFF; margin: 2px 0;">{target['target_price']}</h3>
                        <p style="color: #00E676; font-size: 11px; font-weight: bold; margin: 2px 0;">Potensi: {target['potential_gain_pct']} | R:R {target['rr_ratio']}</p>
                        <span class="tp-badge-green" style="font-size: 10px;">{target['target_basis']}</span>
                    </div>
                """, unsafe_allow_html=True)
