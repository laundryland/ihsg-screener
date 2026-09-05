import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

# ==========================================
# 1. DAFTAR EMITEN & PEMETAAN SEKTOR
# ==========================================
STOCKS = [
    # Indeks
    "^JKSE",
    
    # Perbankan
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "ARTO.JK", "BBTN.JK",
    
    # Energi & Komoditas
    "ADRO.JK", "PTBA.JK", "ITMG.JK", "HRUM.JK", "AKRA.JK", "MEDC.JK", "PGAS.JK",
    
    # Tambang & Logam
    "ANTM.JK", "INCO.JK", "MDKA.JK", "MBMA.JK", "NCKL.JK", "TINS.JK",
    
    # Teknologi & Media
    "GOTO.JK", "EMTK.JK", "SCMA.JK", "BUKA.JK",
    
    # Konsumer & Ritel
    "ICBP.JK", "INDF.JK", "UNVR.JK", "MYOR.JK", "AMRT.JK", "ACES.JK",
    
    # Properti & Infrastruktur
    "BSDE.JK", "CTRA.JK", "PWON.JK", "TLKM.JK", "ISAT.JK", "EXCL.JK", "JSMR.JK",
    
    # Industri & Otomotif
    "ASII.JK", "UNTR.JK"
]

SECTOR_MAP = {
    "BBCA": "Perbankan", "BBRI": "Perbankan", "BMRI": "Perbankan", "BBNI": "Perbankan", 
    "BRIS": "Perbankan", "ARTO": "Perbankan", "BBTN": "Perbankan",
    
    "ADRO": "Energi", "PTBA": "Energi", "ITMG": "Energi", "HRUM": "Energi", 
    "AKRA": "Energi", "MEDC": "Energi", "PGAS": "Energi",
    
    "ANTM": "Tambang", "INCO": "Tambang", "MDKA": "Tambang", "MBMA": "Tambang", 
    "NCKL": "Tambang", "TINS": "Tambang",
    
    "GOTO": "Teknologi", "EMTK": "Teknologi", "SCMA": "Media", "BUKA": "Teknologi",
    
    "ICBP": "Konsumer", "INDF": "Konsumer", "UNVR": "Konsumer", "MYOR": "Konsumer", 
    "AMRT": "Konsumer", "ACES": "Konsumer",
    
    "BSDE": "Properti", "CTRA": "Properti", "PWON": "Properti", "TLKM": "Industri", 
    "ISAT": "Industri", "EXCL": "Industri", "JSMR": "Industri",
    
    "ASII": "Industri", "UNTR": "Industri"
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
    print("Memulai proses screening saham...")
    results = []
    
    for ticker_symbol in STOCKS:
        try:
            clean_name = "IHSG" if ticker_symbol == "^JKSE" else ticker_symbol.replace(".JK", "")
            print(f"Mengunduh data: {clean_name} ...")
            
            # Ambil data histori 100 hari terakhir
            df = yf.download(ticker_symbol, period="100d", interval="1d", progress=False)
            
            if df.empty or len(df) < 30:
                print(f"Data {clean_name} kurang / tidak tersedia. Dilewati.")
                continue

            # Menangani MultiIndex Column jika ada dari yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # --- EKSTRAKSI HARGA PRICE ACTION ---
            close_prices = df['Close']
            open_prices = df['Open']
            high_prices = df['High']
            low_prices = df['Low']
            volumes = df['Volume']

            last_close = round(clean_val(close_prices.iloc[-1]))
            last_open = round(clean_val(open_prices.iloc[-1]))
            last_high = round(clean_val(high_prices.iloc[-1]))
            last_low = round(clean_val(low_prices.iloc[-1]))

            # --- KALKULASI INDIKATOR TEKNIKAL ---
            # 1. Moving Average & Support/Resistance
            ma20 = clean_val(close_prices.rolling(window=20).mean().iloc[-1])
            support = round(clean_val(low_prices.rolling(window=20).min().iloc[-1]))
            resistance = round(clean_val(high_prices.rolling(window=20).max().iloc[-1]))

            # 2. RSI & Status
            rsi_series = calculate_rsi(close_prices, 14)
            rsi_val = clean_val(rsi_series.iloc[-1], default=50)
            
            rsi_status = "NEUTRAL"
            if rsi_val <= 38:
                rsi_status = "BUY"
            elif rsi_val >= 62:
                rsi_status = "SELL"

            # 3. MACD & Status
            macd, macd_sig = calculate_macd(close_prices)
            macd_val = clean_val(macd.iloc[-1])
            macd_sig_val = clean_val(macd_sig.iloc[-1])
            
            macd_status = "BUY" if macd_val > macd_sig_val else "SELL"

            # 4. Volume Ratio & Status
            vol_ma20 = clean_val(volumes.rolling(window=20).mean().iloc[-1], default=1)
            last_vol = clean_val(volumes.iloc[-1])
            vol_ratio = round(last_vol / vol_ma20, 2) if vol_ma20 > 0 else 1.0
            
            vol_status = "BUY" if vol_ratio >= 1.2 else ("SELL" if vol_ratio <= 0.8 else "NEUTRAL")

            # 5. FIBO RSI Status
            fibo_rsi_status = "NORMAL"
            if rsi_val <= 30:
                fibo_rsi_status = "OVER SOLD"
            elif rsi_val >= 70:
                fibo_rsi_status = "OVER BOUGHT"

            # ==========================================
            # PEMETAAN SINYAL LENGKAP:
            # STRONG BUY, BUY, NETRAL, SELL, STRONG SELL
            # ==========================================
            buy_score = (1 if rsi_status == "BUY" else 0) + \
                        (1 if macd_status == "BUY" else 0) + \
                        (1 if vol_status == "BUY" else 0)

            sell_score = (1 if rsi_status == "SELL" else 0) + \
                         (1 if macd_status == "SELL" else 0) + \
                         (1 if vol_status == "SELL" else 0)

            signal = "NETRAL"

            # Sinyal Beli
            if (last_close >= resistance and vol_ratio > 1.2) or buy_score == 3:
                signal = "STRONG BUY"
            elif buy_score >= 2 or (last_close > ma20 and macd_status == "BUY"):
                signal = "BUY"
            
            # Sinyal Jual
            elif (last_close <= support and vol_ratio > 1.2) or sell_score == 3:
                signal = "STRONG SELL"
            elif sell_score >= 2 or (last_close < support):
                signal = "SELL"

            # ==========================================
            # OBJECT OUTPUT JSON
            # ==========================================
            stock_data = {
                "ticker": clean_name,
                "category": "Indeks Utama" if clean_name == "IHSG" else SECTOR_MAP.get(clean_name, "Lainnya"),
                "price": last_close,
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
                "signal": signal  # Mendukung STRONG BUY / BUY / NETRAL / SELL / STRONG SELL
            }

            results.append(stock_data)

        except Exception as e:
            print(f"Gagal memproses {ticker_symbol}: {str(e)}")

    # Format akhir JSON
    output_json = {
        "updated_at": datetime.now().isoformat(),
        "stocks": results
    }

    # Simpan ke data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)

    print("\nProses screening selesai! Hasil telah disimpan ke 'data.json'.")

if __name__ == "__main__":
    run_screener()
