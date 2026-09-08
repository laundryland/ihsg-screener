import json
import yfinance as yf
import pandas as pd
import numpy as np

STOCKS = ["^JKSE", "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "CUAN.JK", "TPIA.JK", "AMMN.JK", "ASII.JK"]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_screener_data():
    output_data = {
        "market_status": {
            "warning": "⏰ Waktu Pasar: Sesi 1 (09:00 - 12:00 WIB) | Sesi 2 (13:30 - 16:00 WIB). JANGAN ENTRY di Luar Jam Bursa!"
        },
        "scalping": [],
        "swing": [],
        "investing": []
    }

    for symbol in STOCKS:
        display_ticker = symbol.replace(".JK", "")
        if display_ticker == "^JKSE":
            display_ticker = "IHSG"

        try:
            ticker = yf.Ticker(symbol)
            
            # ==========================================
            # 1. SCALPING (15m) -> Utama: EMA 9/21, RSI
            # ==========================================
            df_scalp = ticker.history(period="5d", interval="15m")
            if not df_scalp.empty and len(df_scalp) >= 30:
                df_scalp['EMA9'] = df_scalp['Close'].ewm(span=9, adjust=False).mean()
                df_scalp['EMA21'] = df_scalp['Close'].ewm(span=21, adjust=False).mean()
                df_scalp['RSI'] = calculate_rsi(df_scalp['Close'], 14)

                latest = df_scalp.iloc[-1]
                close_p = round(latest['Close'], 2)
                ema9 = round(latest['EMA9'], 2)
                ema21 = round(latest['EMA21'], 2)
                rsi = round(latest['RSI'], 2)

                # Evaluasi Kriteria Indikator Utama
                cond_ema = (ema9 > ema21)
                cond_rsi = (45 <= rsi <= 65)
                is_layak = cond_ema and cond_rsi

                atr = (df_scalp['High'] - df_scalp['Low']).rolling(14).mean().iloc[-1]
                atr = max(atr, close_p * 0.01)

                output_data["scalping"].append({
                    "ticker": display_ticker,
                    "price": close_p,
                    "status": "LAYAK BELI" if is_layak else "WAIT & SEE",
                    "indicators": {
                        "ema_cross": {"val": f"EMA9({ema9}) > EMA21({ema21})", "active": cond_ema},
                        "rsi": {"val": f"RSI 14 ({rsi})", "active": cond_rsi},
                        "macd": {"val": "MACD N/A", "active": False},
                        "vol_sma": {"val": "Volume N/A", "active": False},
                        "sma50": {"val": "SMA50 N/A", "active": False}
                    },
                    "entry_levels": [close_p, round(close_p * 0.995, 2), round(close_p * 0.99, 2)],
                    "tp_levels": [round(close_p + (atr * 1.5), 2), round(close_p + (atr * 2.5), 2), round(close_p + (atr * 4.0), 2)],
                    "cl_levels": [round(close_p - (atr * 1.0), 2), round(close_p - (atr * 1.5), 2), round(close_p - (atr * 2.0), 2)]
                })

            # ==========================================
            # 2. SWING (1D) -> Utama: EMA 20/50, MACD, Vol SMA20
            # ==========================================
            df_swing = ticker.history(period="6m", interval="1d")
            if not df_swing.empty and len(df_swing) >= 50:
                df_swing['EMA20'] = df_swing['Close'].ewm(span=20, adjust=False).mean()
                df_swing['EMA50'] = df_swing['Close'].ewm(span=50, adjust=False).mean()
                df_swing['Vol_SMA20'] = df_swing['Volume'].rolling(window=20).mean()
                
                ema12 = df_swing['Close'].ewm(span=12, adjust=False).mean()
                ema26 = df_swing['Close'].ewm(span=26, adjust=False).mean()
                df_swing['MACD'] = ema12 - ema26
                df_swing['Signal'] = df_swing['MACD'].ewm(span=9, adjust=False).mean()
                df_swing['Hist'] = df_swing['MACD'] - df_swing['Signal']

                latest = df_swing.iloc[-1]
                close_p = round(latest['Close'], 2)
                ema20 = round(latest['EMA20'], 2)
                ema50 = round(latest['EMA50'], 2)
                macdh = round(latest['Hist'], 2)
                vol = latest['Volume']
                vol_sma = latest['Vol_SMA20']

                cond_ema = (ema20 > ema50)
                cond_macd = (macdh > 0)
                cond_vol = (vol > vol_sma)
                is_layak = cond_ema and cond_macd and cond_vol

                output_data["swing"].append({
                    "ticker": display_ticker,
                    "price": close_p,
                    "status": "LAYAK BELI" if is_layak else "WAIT & SEE",
                    "indicators": {
                        "ema_cross": {"val": f"EMA20({ema20}) > EMA50({ema50})", "active": cond_ema},
                        "rsi": {"val": "RSI N/A", "active": False},
                        "macd": {"val": f"MACD Hist ({macdh})", "active": cond_macd},
                        "vol_sma": {"val": f"Vol > SMA20 ({round(vol/vol_sma, 1)}x)", "active": cond_vol},
                        "sma50": {"val": "SMA50 N/A", "active": False}
                    },
                    "entry_levels": [close_p, ema20, ema50],
                    "tp_levels": [round(close_p * 1.05, 2), round(close_p * 1.10, 2), round(close_p * 1.20, 2)],
                    "cl_levels": [round(ema20 * 0.98, 2), round(ema50 * 0.97, 2), round(ema50 * 0.95, 2)]
                })

            # ==========================================
            # 3. INVESTING (1W) -> Utama: SMA 50, RSI (Accumulation)
            # ==========================================
            df_inv = ticker.history(period="2y", interval="1wk")
            if not df_inv.empty and len(df_inv) >= 50:
                df_inv['SMA50'] = df_inv['Close'].rolling(window=50).mean()
                df_inv['RSI'] = calculate_rsi(df_inv['Close'], 14)

                latest = df_inv.iloc[-1]
                close_p = round(latest['Close'], 2)
                sma50 = round(latest['SMA50'], 2) if not np.isnan(latest['SMA50']) else close_p
                rsi = round(latest['RSI'], 2)

                cond_sma = (close_p >= sma50)
                cond_rsi = (rsi < 50) # Diskon zone
                is_layak = cond_sma and cond_rsi

                output_data["investing"].append({
                    "ticker": display_ticker,
                    "price": close_p,
                    "status": "LAYAK AKUMULASI" if is_layak else "HOLD / WAITING",
                    "indicators": {
                        "ema_cross": {"val": "EMA N/A", "active": False},
                        "rsi": {"val": f"RSI Diskon ({rsi})", "active": cond_rsi},
                        "macd": {"val": "MACD N/A", "active": False},
                        "vol_sma": {"val": "Volume N/A", "active": False},
                        "sma50": {"val": f"Price >= SMA50({sma50})", "active": cond_sma}
                    },
                    "entry_levels": [close_p, round(close_p * 0.95, 2), round(close_p * 0.90, 2)],
                    "tp_levels": [round(close_p * 1.25, 2), round(close_p * 1.50, 2), round(close_p * 2.00, 2)],
                    "cl_levels": [round(close_p * 0.85, 2), round(close_p * 0.80, 2), round(close_p * 0.75, 2)]
                })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    with open("data.json", "w") as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    get_screener_data()