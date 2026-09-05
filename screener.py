import json
from datetime import datetime
import math
import pandas as pd
import yfinance as yf

TICKERS = [
    # 1. Saham Konglomerat
    "^JKSE", "AMRT.JK", "ASII.JK", "BRPT.JK", "CUAN.JK", "EMTK.JK", 
    "ICBP.JK", "INDF.JK", "ITMG.JK", "MDKA.JK", "PTBA.JK", "PTRO.JK", 
    "TLKM.JK", "TPIA.JK", "UNTR.JK", "UNVR.JK",
    
    # 2. Saham Perbankan
    "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK",
    
    # 3. Saham Volatil & Sisanya
    "ACES.JK", "ADRO.JK", "AKRA.JK", "ANTM.JK", "BUKA.JK", "CPIN.JK", 
    "EXCL.JK", "INTP.JK", "KLBF.JK", "MAPI.JK", "MDIA.JK", "MEDC.JK", 
    "PGAS.JK", "SIDO.JK", "SMGR.JK"
]

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def clean_val(val):
    if val is None or math.isnan(val) or math.isinf(val):
        return 0.0
    return round(float(val), 2)

def run_screener():
    results = []
    print("Memulai analisis saham IHSG...")

    for ticker in TICKERS:
        try:
            df = yf.download(ticker, period="6mo", progress=False)

            if df.empty or len(df) < 35:
                continue

            close_prices = df['Close'].squeeze()
            high_prices = df['High'].squeeze()
            low_prices = df['Low'].squeeze()
            volume_data = df['Volume'].squeeze()

            ma20_series = close_prices.rolling(window=20).mean()
            vol_ma20_series = volume_data.rolling(window=20).mean()
            rsi_series = calculate_rsi(close_prices)
            macd_series, macd_signal_series = calculate_macd(close_prices)

            resistance_20 = high_prices.iloc[-21:-1].max()
            support_20 = low_prices.iloc[-21:-1].min()

            last_close = clean_val(close_prices.iloc[-1])
            last_rsi = clean_val(rsi_series.iloc[-1])
            last_ma20 = clean_val(ma20_series.iloc[-1])
            res_val = clean_val(resistance_20)
            sup_val = clean_val(support_20)
            
            if last_rsi < 35:
                rsi_status = "BUY"
            elif last_rsi > 70:
                rsi_status = "SELL"
            else:
                rsi_status = "NEUTRAL"

            last_macd = clean_val(macd_series.iloc[-1])
            last_macd_sig = clean_val(macd_signal_series.iloc[-1])
            
            if last_macd > last_macd_sig and last_macd > 0:
                macd_status = "BUY"
            elif last_macd < last_macd_sig and last_macd < 0:
                macd_status = "SELL"
            else:
                macd_status = "NEUTRAL"

            last_vol = float(volume_data.iloc[-1])
            last_vol_ma = float(vol_ma20_series.iloc[-1])
            vol_ratio = clean_val(last_vol / last_vol_ma) if last_vol_ma > 0 else 1.0

            if vol_ratio >= 1.5:
                vol_status = "BUY"
            elif vol_ratio < 0.7:
                vol_status = "SELL"
            else:
                vol_status = "NEUTRAL"

            if sup_val > 0 and last_close <= (sup_val * 1.02):
                snd_status = "BUY"
            elif res_val > 0 and last_close >= (res_val * 0.98):
                snd_status = "SELL"
            else:
                snd_status = "NEUTRAL"

            # Penentuan Sinyal
            signal = "NEUTRAL"
            if last_close > res_val and res_val > 0:
                signal = "SBR" if vol_ratio >= 1.5 else "Break R"
            elif last_close < sup_val and sup_val > 0:
                signal = "SBS" if vol_ratio >= 1.5 else "Break S"
            elif rsi_status == "BUY" or last_close > last_ma20:
                signal = "BUY"
            elif rsi_status == "SELL" or last_close < last_ma20:
                signal = "SELL"

            clean_name = ticker.replace(".JK", "").replace("^JKSE", "IHSG")

            results.append({
                "ticker": clean_name,
                "price": last_close,
                "rsi": last_rsi,
                "rsi_status": rsi_status,
                "ma20": last_ma20,
                "support": sup_val,
                "resistance": res_val,
                "snd_status": snd_status,
                "vol_ratio": vol_ratio,
                "vol_status": vol_status,
                "macd_status": macd_status,
                "signal": signal
            })

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
