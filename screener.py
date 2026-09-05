import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

# ==========================================
# 1. DAFTAR EMITEN & PEMETAAN SEKTOR (DIBERSIHKAN DARI DUPLIKAT)
# ==========================================
# Menggunakan set & dict secara acak untuk memastikan tidak ada emiten ganda
RAW_STOCKS = [
    # Indeks Utama
    "^JKSE",
    
    # Perbankan & Keuangan
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "ARTO.JK", "BBTN.JK",
    
    # Energi, Tambang & Komoditas
    "ADRO.JK", "PTBA.JK", "ITMG.JK", "HRUM.JK", "AKRA.JK", "MEDC.JK", "PGAS.JK",
    "ANTM.JK", "INCO.JK", "MDKA.JK", "MBMA.JK", "NCKL.JK", "TINS.JK", "ENRG.JK",
    "BRMS.JK", "DEWA.JK", "AADI.JK", "BYAN.JK", "BULL.JK", "HUMI.JK", "DSSA.JK", "CBRE.JK",
    
    # Teknologi, Infrastruktur & Media
    "GOTO.JK", "EMTK.JK", "SCMA.JK", "BUKA.JK", "TLKM.JK", "ISAT.JK", "EXCL.JK",
    "JSMR.JK", "INET.JK", "WIFI.JK", "DOOH.JK", "BACH.JK", "KBLV.JK", "MDIA.JK", "DATA.JK", "MTDL.JK",
    
    # Konsumer, Ritel & Kesehatan
    "ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "AMRT.JK", "ACES.JK", "AGAR.JK", "MUTU.JK", "NIKL.JK",
    
    # Properti, Konstruksi & Pariwisata
    "BSDE.JK", "CTRA.JK", "PWON.JK", "KOTA.JK", "JGLE.JK", "BAPA.JK", "KOKA.JK",
    "CDIA.JK", "ROCK.JK", "BUVA.JK", "MWOP.JK", "DL.JK", "WBSA.JK",
    
    # Industri, Otomotif & Konglomerasi
    "ASII.JK", "UNTR.JK", "BNBR.JK"
]

# Menghilangkan duplikat jika ada dengan mempertahankan urutan
STOCKS = list(dict.fromkeys(RAW_STOCKS))

SECTOR_MAP = {
    # Perbankan
    "BBCA": "Perbankan", "BBRI": "Perbankan", "BMRI": "Perbankan", "BBNI": "Perbankan", 
    "BRIS": "Perbankan", "ARTO": "Perbankan", "BBTN": "Perbankan",
    
    # Energi & Tambang
    "ADRO": "Energi", "PTBA": "Energi", "ITMG": "Energi", "HRUM": "Energi", 
    "AKRA": "Energi", "MEDC": "Energi", "PGAS": "Energi", "ENRG": "Energi", "BYAN": "Energi",
    "ANTM": "Tambang", "INCO": "Tambang", "MDKA": "Tambang", "MBMA": "Tambang", 
    "NCKL": "Tambang", "TINS": "Tambang", "BRMS": "Tambang", "DEWA": "Tambang", "AADI": "Tambang",
    "DSSA": "Energi", "BULL": "Energi", "HUMI": "Energi", "CBRE": "Energi",
    
    # Teknologi & Media
    "GOTO": "Teknologi", "EMTK": "Teknologi", "BUKA": "Teknologi", "INET": "Teknologi",
    "WIFI": "Teknologi", "DATA": "Teknologi", "MTDL": "Teknologi", "KBLV": "Teknologi",
    "SCMA": "Media", "MDIA": "Media", "DOOH": "Media", "BACH": "Media",
    
    # Telekomunikasi & Industri
    "TLKM": "Industri", "ISAT": "Industri", "EXCL": "Industri", "JSMR": "Industri",
    "ASII": "Industri", "UNTR": "Industri", "BNBR": "Industri", "NIKL": "Industri",
    
    # Konsumer & Jasa
    "ICBP": "Konsumer", "INDF": "Konsumer", "UNVR": "Konsumer", "MYOR": "Konsumer", 
    "AMRT": "Konsumer", "ACES": "Konsumer", "AGAR": "Konsumer", "MUTU": "Konsumer",
    
    # Properti & Pariwisata
    "BSDE": "Properti", "CTRA": "Properti", "PWON": "Properti", "KOTA": "Properti",
    "JGLE": "Properti", "BAPA": "Properti", "KOKA": "Properti", "CDIA": "Properti",
    "ROCK": "Properti", "BUVA": "Properti", "MWOP": "Properti", "DL": "Properti", "WBSA": "Properti"
}

# ==========================================
# 2. HELPER FUNCTIONS (INDIKATOR TEKNIKAL)
# ==========================================
def clean_val(val, default=0):
    """Memastikan nilai terbebas dari NaN, Inf, atau format Series/Array."""
    if isinstance(val, (pd.Series, np.ndarray)):
        val = val.item() if val.size == 1 else val[-1]
    if pd.isna(val) or np.isinf(val):
        return default
    return float(val)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# ==========================================
# 3. PROSES UTAMA SCREENING
# ==========================================
def run_screener():
    print(f"Memulai proses screening untuk {len(STOCKS)} emiten...")
    results = []
    
    for ticker_symbol in STOCKS:
        try:
            clean_name = "IHSG" if ticker_symbol == "^JKSE" else ticker_symbol.replace(".JK", "")
            print(f"Mengunduh data: {clean_name} ...")
            
            # Ambil data histori 100 hari terakhir
            df = yf.download(ticker_symbol, period="100d", interval="1d", progress=False)
            
            if df.empty or len(df) < 5:
                print(f"Data {clean_name} kurang / tidak tersedia. Dilewati.")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close_prices = df['Close']
            open_prices = df['Open']
            high_prices = df['High']
            low_prices = df['Low']
            volumes = df['Volume']

            last_close = round(clean_val(close_prices.iloc[-1]))
            last_open = round(clean_val(open_prices.iloc[-1]))
            last_high = round(clean_val(high_prices.iloc[-1]))
            last_low = round(clean_val(low_prices.iloc[-1]))
            prev_close = round(clean_val(close_prices.iloc[-2])) if len(close_prices) > 1 else last_open

            # Indikator Teknikal
            ma20 = clean_val(close_prices.rolling(window=min(20, len(close_prices))).mean().iloc[-1])
            support = round(clean_val(low_prices.rolling(window=min(20, len(low_prices))).min().iloc[-1]))
            resistance = round(clean_val(high_prices.rolling(window=min(20, len(high_prices))).max().iloc[-1]))

            # RSI
            rsi_series = calculate_rsi(close_prices, 14)
            rsi_val = clean_val(rsi_series.iloc[-1], default=50)
            
            rsi_status = "NEUTRAL"
            if rsi_val <= 38:
                rsi_status = "BUY"
            elif rsi_val >= 62:
                rsi_status = "SELL"

            # MACD
            macd, macd_sig = calculate_macd(close_prices)
            macd_val = clean_val(macd.iloc[-1])
            macd_sig_val = clean_val(macd_sig.iloc[-1])
            macd_status = "BUY" if macd_val > macd_sig_val else "SELL"

            # Volume Ratio
            vol_ma20 = clean_val(volumes.rolling(window=min(20, len(volumes))).mean().iloc[-1], default=1)
            last_vol = clean_val(volumes.iloc[-1])
            vol_ratio = round(last_vol / vol_ma20, 2) if vol_ma20 > 0 else 1.0
            vol_status = "BUY" if vol_ratio >= 1.2 else ("SELL" if vol_ratio <= 0.8 else "NEUTRAL")

            # FIBO RSI
            fibo_rsi_status = "NORMAL"
            if rsi_val <= 30:
                fibo_rsi_status = "OVER SOLD"
            elif rsi_val >= 70:
                fibo_rsi_status = "OVER BOUGHT"

            # Sinyal Utama
            buy_score = (1 if rsi_status == "BUY" else 0) + \
                        (1 if macd_status == "BUY" else 0) + \
                        (1 if vol_status == "BUY" else 0)

            sell_score = (1 if rsi_status == "SELL" else 0) + \
                         (1 if macd_status == "SELL" else 0) + \
                         (1 if vol_status == "SELL" else 0)

            signal = "NETRAL"
            if (last_close >= resistance and vol_ratio > 1.2) or buy_score == 3:
                signal = "STRONG BUY"
            elif buy_score >= 2 or (last_close > ma20 and macd_status == "BUY"):
                signal = "BUY"
            elif (last_close <= support and vol_ratio > 1.2) or sell_score == 3:
                signal = "STRONG SELL"
            elif sell_score >= 2 or (last_close < support):
                signal = "SELL"

            # Logika "Wait" untuk Entry, Take Profit, dan Cut Loss
            if signal in ["STRONG BUY", "BUY"]:
                entry_price = last_close
                cut_loss = round(support * 0.98)
                risk = entry_price - cut_loss
                if risk <= 0:
                    risk = entry_price * 0.02
                take_profit = round(entry_price + (risk * 2))
            else:
                entry_price = "Wait"
                cut_loss = "Wait"
                take_profit = "Wait"

            stock_data = {
                "ticker": clean_name,
                "category": "Indeks Utama" if clean_name == "IHSG" else SECTOR_MAP.get(clean_name, "Lainnya"),
                "price": last_close,
                "prev_close": prev_close,
                "open": last_open,
                "high": last_high,
                "low": last_low,
                "rsi": round(rsi_val, 2),
                "rsi_status": rsi_status,
                "ma20": round(ma20),
                "support": support,
                "resistance": resistance,
                "vol_ratio": vol_ratio,
                "vol_status": vol_status,
                "macd_status": macd_status,
                "fibo_rsi_status": fibo_rsi_status,
                "signal": signal,
                "entry_price": entry_price,
                "cut_loss": cut_loss,
                "take_profit": take_profit,
                "visual_indicator_info": "Indikator Visual Sinyal Transaksi Saham.",
                "image_source": "tupungato / Getty Images"
            }

            results.append(stock_data)

        except Exception as e:
            print(f"Gagal memproses {ticker_symbol}: {str(e)}")

    output_json = {
        "updated_at": datetime.now().isoformat(),
        "stocks": results
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)

    print("\nProses screening selesai! Hasil telah disimpan ke 'data.json'.")

if __name__ == "__main__":
    run_screener()
