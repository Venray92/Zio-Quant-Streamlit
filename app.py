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

# 4. Helper Fraksi Harga BEI Sesuai Aturan Mutlak
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

# 5. Helper Deteksi Reversal / Swing Structural (Fractal Peak & Trough)
def find_swing_points(df, window=4):
    """Mencari Swing High dan Swing Low nyata berdasarkan titik puncak/lembah lokal."""
    swing_highs = []
    swing_lows = []
    
    highs = df['High'].values
    lows = df['Low'].values
    n = len(df)
    
    for i in range(window, n - window):
        # Peak / Swing High
        if all(highs[i] > highs[i - j] for j in range(1, window + 1)) and \
           all(highs[i] >= highs[i + j] for j in range(1, window + 1)):
            swing_highs.append(highs[i])
            
        # Trough / Swing Low
        if all(lows[i] < lows[i - j] for j in range(1, window + 1)) and \
           all(lows[i] <= lows[i + j] for j in range(1, window + 1)):
            swing_lows.append(lows[i])
            
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

# 7. Trade Plan Engine (Presisi Struktur Support & Resistance Real)
@st.cache_data(ttl=600)
def get_stock_trade_plan(symbol):
    if symbol in ["^JKSE", "IDX:COMPOSITE"]:
        return {
            "is_ihsg": True, "price": "-", "plan_type": "-", "is_breakdown": False,
            "buy_range": "-", "sl_price": "-", "tp1": "-", "tp2": "-", "tp3": "-",
            "risk_pct": "-", "reward_pct_1": "-", "reward_pct_2": "-", "reward_pct_3": "-",
            "rr_1": 0, "rr_2": 0, "rr_3": 0, "max_allowed_risk": 0,
            "vol_spike": False, "entry_worst": 0, "technical_score": 50,
            "bow_range": "-", "bow_sl": "-", "bob_range": "-", "bob_sl": "-"
        }
    try:
        yf_symbol = f"{symbol.replace('IDX:', '')}.JK"
        df = yf.download(yf_symbol, period="180d", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        c0 = float(df['Close'].iloc[-1])
        o0 = float(df['Open'].iloc[-1])
        h0 = float(df['High'].iloc[-1])
        l0 = float(df['Low'].iloc[-1])
        v0 = float(df['Volume'].iloc[-1])

        # 1. Deteksi Swing Points Nyata (Structural Fractalling)
        sh_list, sl_list = find_swing_points(df, window=4)
        
        # Cari Swing High yang valid di atas harga Close saat ini
        valid_sh = sorted([x for x in set(sh_list) if x > c0])
        if len(valid_sh) < 3:
            # Fallback jika tidak cukup fractal high
            max_h = float(df['High'].max())
            step = (max_h - c0) / 3 if max_h > c0 else c0 * 0.05
            tp1 = valid_sh[0] if len(valid_sh) >= 1 else add_ticks(c0, 5)
            tp2 = valid_sh[1] if len(valid_sh) >= 2 else add_ticks(tp1, 5)
            tp3 = max_h if max_h > tp2 else add_ticks(tp2, 5)
        else:
            tp1, tp2, tp3 = valid_sh[0], valid_sh[1], valid_sh[2]

        # Cari Swing Low utama (Support Terdekat di bawah Close)
        valid_sl = sorted([x for x in set(sl_list) if x <= c0])
        swing_low_real = valid_sl[-1] if len(valid_sl) > 0 else float(df['Low'].tail(30).min())

        # 2. Penentuan Tipe Trade Plan Berdasarkan Kedekatan Posisi
        dist_to_low = abs(c0 - swing_low_real)
        dist_to_high = abs(tp1 - c0)

        if dist_to_low <= dist_to_high:
            plan_type = "BUY ON WEAKNESS (BOW)"
        else:
            plan_type = "BUY ON BREAKOUT (BOB)"

        # 3. Formulasi Parameter BOW & BOB yang Presisi
        # Area BOW: Range sekitar Swing Low
        bow_range_low = subtract_ticks(swing_low_real, 3)
        bow_range_high = add_ticks(swing_low_real, 3)
        bow_sl_price = subtract_ticks(bow_range_low, 3)

        # Area BOB: Saat Breakout Swing High 1 (TP1)
        bob_range_low = tp1
        bob_range_high = add_ticks(tp1, 3)
        bob_sl_price = subtract_ticks(tp1, 3)

        # Gunakan parameter sesuai rekomendasi setup utama
        if "WEAKNESS" in plan_type:
            buy_range_low = bow_range_low
            buy_range_high = bow_range_high
            sl_price = bow_sl_price
        else:
            buy_range_low = bob_range_low
            buy_range_high = bob_range_high
            sl_price = bob_sl_price

        # Deteksi Reversal/Breakdown Parah
        is_marubozu_red = (c0 < o0) and ((o0 - c0) / (h0 - l0 + 1e-5) > 0.85) and ((c0 - l0) / (h0 - l0 + 1e-5) < 0.05)
        is_new_low = c0 <= (swing_low_real * 0.98)
        is_breakdown = is_marubozu_red or is_new_low

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
            "vol_spike": (v0 >= vol_ma20),
            "entry_worst": entry_worst,
            "bow_range": f"Rp {int(bow_range_low):,} – Rp {int(bow_range_high):,}",
            "bow_sl": f"Rp {int(bow_sl_price):,}",
            "bob_range": f"Rp {int(bob_range_low):,} – Rp {int(bob_range_high):,}",
            "bob_sl": f"Rp {int(bob_sl_price):,}"
        }
    except Exception as e:
        return {
            "is_ihsg": False, "price": "-", "plan_type": "-", "is_breakdown": False,
            "buy_range": "-", "sl_price": "-", "tp1": "-", "tp2": "-", "tp3": "-",
            "risk_pct": "-", "reward_pct_1": "-", "reward_pct_2": "-", "reward_pct_3": "-",
            "rr_1": 0, "rr_2": 0, "rr_3": 0, "vol_spike": False, "entry_worst": 0,
            "bow_range": "-", "bow_sl": "-", "bob_range": "-", "bob_sl": "-"
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

    # VIEW 2: TRADE PLAN MODUL (TERPERBARUI DENAGAN LOGIKA STRUCTURAL PRESI)
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
                    <p style="color: #64748B; font-size: 11px; margin: 0;">Rekomendasi Setup Utama (Posisi Terdekat)</p>
                    <p style="color: #00E676; font-size: 14px; font-weight: bold; margin: 2px 0;">⚡ {tp['plan_type']}</p>
                </div>
            """, unsafe_allow_html=True)

            if tp["is_breakdown"]:
                st.error("⛔ **RULE PENOLAKAN:** Saham Breakdown Support (Marubozu Merah / New Low). Status: **SKIP / WAIT AND SEE**.")

            # Bagian 2: Trading Plan Detail
            st.markdown("##### 🔵 **2. TRADING PLAN DETAIL (REKOMENDASI SETUP)**")
            
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #1E3A2F; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #00E676; font-size: 11px; font-weight: bold; margin: 0;">🟢 AREA ENTRY ({tp['plan_type']})</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['buy_range']}</h4>
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">Area eksekusi beli presisi sesuai struktur Swing.</p>
                    </div>
                """, unsafe_allow_html=True)
            with d2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #3A1E1E; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #FF5252; font-size: 11px; font-weight: bold; margin: 0;">🛑 STOP LOSS ({tp['risk_pct']})</p>
                        <h4 style="color: #E2E8F0; margin: 4px 0;">{tp['sl_price']}</h4>
                        <p style="color: #94A3B8; font-size: 11px; margin: 0;">Cut loss disiplin jika closing menembus level ini.</p>
                    </div>
                """, unsafe_allow_html=True)

            # Referensi Lengkap Pembagian Parameter Parameter BOW vs BOB
            st.markdown("<p style='font-size: 11px; color: #64748B; font-weight: bold; margin-top: 4px; margin-bottom: 4px;'>PARAMETER LENGKAP STRATEGI (BOW & BOB):</p>", unsafe_allow_html=True)
            ref_col1, ref_col2 = st.columns(2)
            with ref_col1:
                st.caption(f"📉 **Buy On Weakness (BOW)**:\nArea Beli: **{tp['bow_range']}** | SL: **{tp['bow_sl']}**")
            with ref_col2:
                st.caption(f"🚀 **Buy On Breakout (BOB)**:\nArea Beli: **{tp['bob_range']}** | SL: **{tp['bob_sl']}**")

            # Target Resistance Swing High (TP)
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            t1, t2, t3 = st.columns(3)
            with t1:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 1 (Swing High 1) | +{tp['reward_pct_1']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp1']}</h5>
                        <p style="color: #94A3B8; font-size: 9px; margin: 0;">Target profit pertama.</p>
                    </div>
                """, unsafe_allow_html=True)
            with t2:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 2 (Swing High 2) | +{tp['reward_pct_2']}</p>
                        <h5 style="color: #E2E8F0; margin: 2px 0;">{tp['tp2']}</h5>
                        <p style="color: #94A3B8; font-size: 9px; margin: 0;">Target profit kedua.</p>
                    </div>
                """, unsafe_allow_html=True)
            with t3:
                st.markdown(f"""
                    <div style="background: #121E2B; border: 1px solid #243447; padding: 10px; border-radius: 8px;">
                        <p style="color: #64748B; font-size: 10px; margin: 0;">TP 3 (Swing High 3) | +{tp['reward_pct_3']}</p>
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
