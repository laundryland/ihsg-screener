import json
import yfinance as yf

# Daftar saham yang ingin dipantau (^JKSE adalah simbol untuk IHSG)
STOCKS = ["^JKSE", "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "CUAN.JK", "TPIA.JK"]

def update_stock_data():
    stock_data = []
    
    for ticker_symbol in STOCKS:
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Mengambil data perdagangan hari ini/terakhir
            df = ticker.history(period="1d")
            
            if not df.empty:
                latest = df.iloc[-1]
                
                # Bersihkan simbol .JK untuk Ticker Tampilan
                display_ticker = ticker_symbol.replace(".JK", "")
                if display_ticker == "^JKSE":
                    display_ticker = "IHSG"

                open_price = float(latest["Open"])
                high_price = float(latest["High"])
                low_price = float(latest["Low"])
                close_price = float(latest["Close"])
                
                # Menentukan sinyal sederhana berdasarkan pergerakan harian
                price_change = close_price - open_price
                if price_change > 0:
                    signal = "BULLISH"
                elif price_change < 0:
                    signal = "BEARISH"
                else:
                    signal = "NEUTRAL"

                stock_data.append({
                    "ticker": display_ticker,
                    "price": round(close_price, 2),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "signal": signal
                })
        except Exception as e:
            print(f"Gagal mengambil data {ticker_symbol}: {e}")

    # Simpan data ke data.json
    output = {"stocks": stock_data}
    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    update_stock_data()
