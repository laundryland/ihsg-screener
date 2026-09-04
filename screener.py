import json
from datetime import datetime
import math
import pandas as pd
import yfinance as yf

# Daftar ticker saham IHSG terkemuka
TICKERS = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", 
    "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", 
    "BUKA.JK", "CPIN.JK", "EMTK.JK", "EXCL.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", 
    "INKP.JK", "INDF.JK", "INTP.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", 
    "MDKA.JK", "MEDC.JK", "PGAS.JK", "PTBA.JK", "SAMP.JK", "SCMA.JK", "SGRS.JK", 
    "SIDO.JK", "SMGR.JK", "SRTG.JK", "TBIG.JK", "TKIM.JK", "TLKM.JK", "TPIA.JK", 
    "UNTR.JK", "UNVR.JK", "BNBR.JK", "JGLE.JK", "CUAN.JK", "KOTA.JK", "BYAN.JK",
]

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def clean_val(val):
    """Memastikan angka aman dari NaN / Infinity untuk format JSON"""
    if val is None or math.isnan(val) or math.isinf(val):
        return 0.0
    return round(float(val), 2)

def run_screener():
    results = []
    print("Memulai analisis saham IHSG...")

    for ticker in TICKERS:
        try:
            # Download data saham
            df = yf.download(ticker, period="6mo", progress=False)

            if df.empty or len(df) < 20:
                print(f"Data {ticker} tidak cukup, dilewati.")
                continue

            # Ambil kolom Close
            close_prices = df['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.squeeze()

            ma20_series = close_prices.rolling(window=20).mean()
            ma50_series = close_prices.rolling(window=50).mean()
            rsi_series = calculate_rsi(close_prices)

            last_close = clean_val(close_prices.iloc[-1])
            last_rsi = clean_val(rsi_series.iloc[-1])
            last_ma20 = clean_val(ma20_series.iloc[-1])
            last_ma50 = clean_val(ma50_series.iloc[-1])

            # Evaluasi Sinyal
            signal = "NEUTRAL"
            if last_rsi > 0 and last_rsi < 35:
                signal = "BUY"
            elif last_close > last_ma20 and last_ma20 > last_ma50 and last_ma50 > 0:
                signal = "BUY"
            elif last_rsi > 70 or (last_close < last_ma20 and last_ma20 < last_ma50 and last_ma50 > 0):
                signal = "SELL"

            clean_name = ticker.replace(".JK", "")

            results.append({
                "ticker": clean_name,
                "price": last_close,
                "rsi": last_rsi,
                "ma20": last_ma20,
                "ma50": last_ma50,
                "signal": signal
            })
            print(f"Sukses memproses {clean_name}: {signal}")

        except Exception as e:
            print(f"Gagal memproses {ticker}: {e}")

    output_data = {
        "updated_at": datetime.now().strftime("%d %B %Y - %H:%M WIB"),
        "stocks": results
    }

    with open("data.json", "w") as f:
        json.dump(output_data, f, indent=4)

    print("Data berhasil diperbarui di data.json")

if __name__ == "__main__":
    run_screener()
