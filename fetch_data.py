import json
import yfinance as yf
import pandas as pd
import numpy as np

# Daftar Ticker (Termasuk IHSG)
STOCKS = ["^JKSE", "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "CUAN.JK", "TPIA.JK", "ASII.JK", "AMMN.JK"]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def process_stock(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    
    # Ambil Data Harian (1D) dan 15-Menit (15m)
    df_daily = ticker.history(period="1y", interval="1d")
    df_scalp = ticker.history(period="1mo", interval="15m")

    if df_daily.empty:
        return None

    # --- 1. Sinyal SCALPING (15m: EMA 9/21 + RSI 14) ---
    scalp_signal = "NEUTRAL"
    if not df_scalp.empty and len(df_scalp) >= 21:
        df_scalp['EMA9'] = df_scalp['Close'].ewm(span=9, adjust=False).mean()
        df_scalp['EMA21'] = df_scalp['Close'].ewm(span=21, adjust=False).mean()
        df_scalp['RSI'] = calculate_rsi(df_scalp['Close'], 14)
        
        last_s = df_scalp.iloc[-1]
        if last_s['EMA9'] > last_s['EMA21'] and last_s['RSI'] < 70:
            scalp_signal = "BULLISH"
        elif last_s['EMA9'] < last_s['EMA21'] or last_s['RSI'] > 70:
            scalp_signal = "BEARISH"

    # --- 2. Sinyal SWING (1D: EMA 20/50 + MACD + ATR) ---
    df_daily['EMA20'] = df_daily['Close'].ewm(span=20, adjust=False).mean()
    df_daily['EMA50'] = df_daily['Close'].ewm(span=50, adjust=False).mean()
    df_daily['ATR'] = calculate_atr(df_daily, 14)
    
    # MACD Calculation
    exp1 = df_daily['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df_daily['Close'].ewm(span=26, adjust=False).mean()
    df_daily['MACD'] = exp1 - exp2
    df_daily['Signal_Line'] = df_daily['MACD'].ewm(span=9, adjust=False).mean()
    
    last_d = df_daily.iloc[-1]
    swing_signal = "NEUTRAL"
    if last_d['EMA20'] > last_d['EMA50'] and last_d['MACD'] > last_d['Signal_Line']:
        swing_signal = "BULLISH"
    elif last_d['EMA20'] < last_d['EMA50'] and last_d['MACD'] < last_d['Signal_Line']:
        swing_signal = "BEARISH"

    # --- 3. Sinyal INVESTASI (1D/1W: MA 50/200 + Stoch RSI) ---
    df_daily['MA50'] = df_daily['Close'].rolling(window=50).mean()
    df_daily['MA200'] = df_daily['Close'].rolling(window=200).mean()
    
    invest_signal = "NEUTRAL"
    if pd.notnull(last_d['MA200']):
        if last_d['Close'] > last_d['MA200'] and last_d['MA50'] > last_d['MA200']:
            invest_signal = "BULLISH"
        elif last_d['Close'] < last_d['MA200']:
            invest_signal = "BEARISH"

    # --- KALKULASI TARGET ENTRY, TP & CL (Multi-Level) ---
    price = round(float(last_d['Close']), 2)
    atr = float(last_d['ATR']) if pd.notnull(last_d['ATR']) else price * 0.02
    
    display_ticker = ticker_symbol.replace(".JK", "")
    if display_ticker == "^JKSE": display_ticker = "IHSG"

    # Penentuan Titik Refrensi Entry Ideal
    entry_ideal = round(price * 0.995, 2)
    entry_breakout = round(price * 1.005, 2)

    # Multi-level Target berdasarkan Volatilitas (ATR)
    tp1 = round(price + (atr * 1.0), 2)
    tp2 = round(price + (atr * 2.0), 2)
    tp3 = round(price + (atr * 3.5), 2)

    cl1 = round(price - (atr * 1.0), 2)
    cl2 = round(price - (atr * 1.5), 2)
    cl3 = round(price - (atr * 2.5), 2)

    # Status Kategori LAYAK BELI
    layak_beli = False
    if swing_signal == "BULLISH" or (scalp_signal == "BULLISH" and invest_signal != "BEARISH"):
        layak_beli = True

    return {
        "ticker": display_ticker,
        "price": price,
        "open": round(float(last_d['Open']), 2),
        "high": round(float(last_d['High']), 2),
        "low": round(float(last_d['Low']), 2),
        "layak_beli": layak_beli,
        "entry_ref": {
            "pullback": entry_ideal,
            "breakout": entry_breakout
        },
        "signals": {
            "scalping": scalp_signal,
            "swing": swing_signal,
            "investasi": invest_signal
        },
        "tp": [tp1, tp2, tp3],
        "cl": [cl1, cl2, cl3]
    }

def update_all():
    results = []
    for symbol in STOCKS:
        try:
            res = process_stock(symbol)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Error {symbol}: {e}")

    with open("data.json", "w") as f:
        json.dump({"stocks": results}, f, indent=2)

if __name__ == "__main__":
    update_all()
