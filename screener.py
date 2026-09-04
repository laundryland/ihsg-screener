import json
from datetime import datetime
import yfinance as yf

# Daftar ticker saham IHSG terkemuka
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK",
    "ASII.JK", "ICBP.JK", "INDF.JK", "UNVR.JK", "AMRT.JK",
    "GOTO.JK", "PGAS.JK", "PTBA.JK", "ADRO.JK", "ANTM.JK"
]

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def run_screener():
    results = []
    print("Memulai analisis saham IHSG...")

    for ticker in TICKERS:
        try:
            # Download data saham
            df = yf.download(ticker, period="6mo", progress=False)

            if df.empty or len(df) < 50:
                print(f"Data {ticker} tidak cukup, dilewati.")
                continue

            # Ambil kolom Close
            close_prices = df['Close']
            if hasattr(close_prices, 'squeeze'):
                close_prices = close_prices.squeeze()

            ma20_series = close_prices.rolling(window=20).mean()
            ma50_series = close_prices.rolling(window=50).mean()
            rsi_series = calculate_rsi(close_prices)

            last_close = float(close_prices.iloc[-1])
            last_rsi = float(rsi_series.iloc[-1])
            last_ma20 = float(ma20_series.iloc[-1])
            last_ma50 = float(ma50_series.iloc[-1])

            # Evaluasi Sinyal
            signal = "NEUTRAL"
            if last_rsi < 35 or (last_close > last_ma20 and last_ma20 > last_ma50):
                signal = "BUY"
            elif last_rsi > 70 or (last_close < last_ma20 and last_ma20 < last_ma50):
                signal = "SELL"

            clean_name = ticker.replace(".JK", "")

            results.append({
                "ticker": clean_name,
                "price": round(last_close, 2),
                "rsi": round(last_rsi, 2),
                "ma20": round(last_ma20, 2),
                "ma50": round(last_ma50, 2),
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
