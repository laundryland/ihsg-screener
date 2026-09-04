import json
from datetime import datetime
import math
import pandas as pd
import yfinance as yf

TICKERS = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", 
    "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", 
    "BMRI.JK", "BRIS.JK", "BRPT.JK", "BUKA.JK", "CPIN.JK", 
    "EMTK.JK", "EXCL.JK", "GOTO.JK", "ICBP.JK", "INDF.JK", 
    "INTP.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MDKA.JK", 
    "MEDC.JK", "PGAS.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", 
    "TLKM.JK", "TPIA.JK", "UNTR.JK", "UNVR.JK", "BUVA.JK",
    "KOTA.JK", "LUCY.JK", "MDIA.JK", "ENRG.JK", "BIPI.JK",
    "CDIA.JK", "INDY.JK", "CBRE.JK", "KOKA.JK", "DEWA.JK",
    
]

# ... (kode lainnya tetap sama) ...

            # Ubah pembersihan nama ticker agar ^JKSE dibaca sebagai IHSG
            clean_name = ticker.replace(".JK", "").replace("^JKSE", "IHSG")

# ... (sisa kode bawahnya tetap sama) ...

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def clean_val(val):
    if val is None or math.isnan(val) or math.isinf(val):
        return 0.0
    return round(float(val), 2)

def run_screener():
    results = []
    print("Memulai analisis saham IHSG dengan Support, Demand, & Bandarmology Volume...")

    for ticker in TICKERS:
        try:
            df = yf.download(ticker, period="6mo", progress=False)

            if df.empty or len(df) < 20:
                print(f"Data {ticker} tidak cukup, dilewati.")
                continue

            close_prices = df['Close'].squeeze()
            high_prices = df['High'].squeeze()
            low_prices = df['Low'].squeeze()
            volume_data = df['Volume'].squeeze()

            # Indikator MA, RSI, & Volume MA20
            ma20_series = close_prices.rolling(window=20).mean()
            vol_ma20_series = volume_data.rolling(window=20).mean()
            rsi_series = calculate_rsi(close_prices)

            # Support & Resistance (20 hari terakhir)
            resistance_20 = high_prices.iloc[-21:-1].max()
            support_20 = low_prices.iloc[-21:-1].min()

            last_close = clean_val(close_prices.iloc[-1])
            last_rsi = clean_val(rsi_series.iloc[-1])
            last_ma20 = clean_val(ma20_series.iloc[-1])
            res_val = clean_val(resistance_20)
            sup_val = clean_val(support_20)
            
            # Analisis Volume (Bandarmology)
            last_vol = float(volume_data.iloc[-1])
            last_vol_ma = float(vol_ma20_series.iloc[-1])
            vol_ratio = clean_val(last_vol / last_vol_ma) if last_vol_ma > 0 else 1.0

            # Logika Signal & Konfirmasi Volume
            signal = "NEUTRAL"
            if last_close > res_val and res_val > 0:
                signal = "Strong Breakout R" if vol_ratio >= 1.5 else "Breakout R"
            elif last_close < sup_val and sup_val > 0:
                signal = "Strong Breakout S" if vol_ratio >= 1.5 else "Breakout S"
            elif last_rsi < 35 or last_close > last_ma20:
                signal = "BUY"
            elif last_rsi > 70 or last_close < last_ma20:
                signal = "SELL"

            clean_name = ticker.replace(".JK", "")

            results.append({
                "ticker": clean_name,
                "price": last_close,
                "rsi": last_rsi,
                "ma20": last_ma20,
                "support": sup_val,
                "resistance": res_val,
                "vol_ratio": vol_ratio,
                "signal": signal
            })
            print(f"Sukses memproses {clean_name}: {signal} (Vol Ratio: {vol_ratio}x)")

        except Exception as e:
            print(f"Gagal memproses {ticker}: {e}")

    output_data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": results
    }

    with open("data.json", "w") as f:
        json.dump(output_data, f, indent=4)

    print("Data berhasil diperbarui di data.json")

if __name__ == "__main__":
    run_screener()
