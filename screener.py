import json
import os
from datetime import datetime
import pandas as pd
import yfinance as yf

TICKERS = [
    # Bluechip / Big Cap
    {"ticker": "BBCA", "category": "Bluechip"}, {"ticker": "BBRI", "category": "Bluechip"},
    {"ticker": "BMRI", "category": "Bluechip"}, {"ticker": "BBNI", "category": "Bluechip"},
    {"ticker": "TLKM", "category": "Bluechip"}, {"ticker": "ASII", "category": "Bluechip"},
    {"ticker": "UNVR", "category": "Bluechip"}, {"ticker": "ICBP", "category": "Bluechip"},
    {"ticker": "INDF", "category": "Bluechip"}, {"ticker": "AMRT", "category": "Bluechip"},
    {"ticker": "TPIA", "category": "Bluechip"}, {"ticker": "BREN", "category": "Bluechip"},
    {"ticker": "BYAN", "category": "Bluechip"}, {"ticker": "CPIN", "category": "Bluechip"},
    {"ticker": "GOTO", "category": "Bluechip"}, {"ticker": "KLBF", "category": "Bluechip"},

    # Energy, Mining & Metals
    {"ticker": "ADRO", "category": "IDX Liquid"}, {"ticker": "PTBA", "category": "IDX Liquid"},
    {"ticker": "ITMG", "category": "IDX Liquid"}, {"ticker": "MEDC", "category": "IDX Liquid"},
    {"ticker": "ANTM", "category": "IDX Liquid"}, {"ticker": "INCO", "category": "IDX Liquid"},
    {"ticker": "PGAS", "category": "IDX Liquid"}, {"ticker": "AKRA", "category": "IDX Liquid"},
    {"ticker": "HRUM", "category": "IDX Liquid"}, {"ticker": "MBMA", "category": "IDX Liquid"},
    {"ticker": "NCKL", "category": "IDX Liquid"}, {"ticker": "AMMN", "category": "IDX Liquid"},
    {"ticker": "CUAN", "category": "IDX Liquid"}, {"ticker": "DOOID", "category": "IDX Liquid"},
    {"ticker": "INDY", "category": "IDX Liquid"}, {"ticker": "ELSA", "category": "IDX Liquid"},
    {"ticker": "ENRG", "category": "IDX Liquid"}, {"ticker": "BUMI", "category": "IDX Liquid"},
    {"ticker": "DEWA", "category": "IDX Liquid"}, {"ticker": "BRMS", "category": "IDX Liquid"},
    {"ticker": "HUMI", "category": "IDX Liquid"}, {"ticker": "BNBR", "category": "IDX Liquid"},
    {"ticker": "TINS", "category": "IDX Liquid"}, {"ticker": "PSAB", "category": "IDX Liquid"},

    # Banking & Financials
    {"ticker": "BRIS", "category": "IDX Liquid"}, {"ticker": "BBTN", "category": "IDX Liquid"},
    {"ticker": "BDMN", "category": "IDX Liquid"}, {"ticker": "BNGA", "category": "IDX Liquid"},
    {"ticker": "NISP", "category": "IDX Liquid"}, {"ticker": "PNBN", "category": "IDX Liquid"},
    {"ticker": "ARTO", "category": "IDX Liquid"}, {"ticker": "BBYB", "category": "IDX Liquid"},
    {"ticker": "BANK", "category": "IDX Liquid"}, {"ticker": "AGRO", "category": "IDX Liquid"},
    {"ticker": "BSIM", "category": "IDX Liquid"}, {"ticker": "MAYA", "category": "IDX Liquid"},

    # Telecom, Tech & Infrastructure
    {"ticker": "EXCL", "category": "IDX Liquid"}, {"ticker": "ISAT", "category": "IDX Liquid"},
    {"ticker": "TOWR", "category": "IDX Liquid"}, {"ticker": "TBIG", "category": "IDX Liquid"},
    {"ticker": "MTEL", "category": "IDX Liquid"}, {"ticker": "EMTK", "category": "IDX Liquid"},
    {"ticker": "SCMA", "category": "IDX Liquid"}, {"ticker": "BUKA", "category": "IDX Liquid"},
    {"ticker": "WIFI", "category": "IDX Liquid"}, {"ticker": "CENT", "category": "IDX Liquid"},
    {"ticker": "MLPT", "category": "IDX Liquid"}, {"ticker": "MTDL", "category": "IDX Liquid"},

    # Consumer & Healthcare
    {"ticker": "MYOR", "category": "IDX Liquid"}, {"ticker": "CMRY", "category": "IDX Liquid"},
    {"ticker": "ACES", "category": "IDX Liquid"}, {"ticker": "MAPI", "category": "IDX Liquid"},
    {"ticker": "MAPA", "category": "IDX Liquid"}, {"ticker": "RALS", "category": "IDX Liquid"},
    {"ticker": "LPPF", "category": "IDX Liquid"}, {"ticker": "ERAA", "category": "IDX Liquid"},
    {"ticker": "MIKA", "category": "IDX Liquid"}, {"ticker": "HEAL", "category": "IDX Liquid"},
    {"ticker": "SILO", "category": "IDX Liquid"}, {"ticker": "SIDO", "category": "IDX Liquid"},
    {"ticker": "TSPC", "category": "IDX Liquid"}, {"ticker": "KAEF", "category": "IDX Liquid"},
    {"ticker": "CLEO", "category": "IDX Liquid"}, {"ticker": "ULTJ", "category": "IDX Liquid"},

    # Property & Construction
    {"ticker": "BSDE", "category": "IDX Liquid"}, {"ticker": "CTRA", "category": "IDX Liquid"},
    {"ticker": "PWON", "category": "IDX Liquid"}, {"ticker": "SMRA", "category": "IDX Liquid"},
    {"ticker": "ASRI", "category": "IDX Liquid"}, {"ticker": "ADHI", "category": "IDX Liquid"},
    {"ticker": "PTPP", "category": "IDX Liquid"}, {"ticker": "WIKA", "category": "IDX Liquid"},
    {"ticker": "TOTL", "category": "IDX Liquid"}, {"ticker": "DILD", "category": "IDX Liquid"},

    # Industrial & Agro
    {"ticker": "SMGR", "category": "IDX Liquid"}, {"ticker": "INTP", "category": "IDX Liquid"},
    {"ticker": "UNTR", "category": "IDX Liquid"}, {"ticker": "AUTO", "category": "IDX Liquid"},
    {"ticker": "GJTL", "category": "IDX Liquid"}, {"ticker": "SMSM", "category": "IDX Liquid"},
    {"ticker": "MAIN", "category": "IDX Liquid"}, {"ticker": "JPFA", "category": "IDX Liquid"},
    {"ticker": "TAPG", "category": "IDX Liquid"}, {"ticker": "DSNG", "category": "IDX Liquid"},
    {"ticker": "SSMS", "category": "IDX Liquid"}, {"ticker": "LSIP", "category": "IDX Liquid"},
    {"ticker": "AALI", "category": "IDX Liquid"}, {"ticker": "ASSA", "category": "IDX Liquid"}
]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_swing_strategy(close, ema14, ema20, ema50, rsi):
    score = 0
    
    # Tren EMA 14 vs EMA 50 (Golden Cross vs Death Cross)
    ema_cross = "UP" if ema14 >= ema50 else "DOWN"

    if close > ema20:
        ema20_status = "strong_buy" if close >= ema20 * 1.02 else "buy"
        score += 2 if ema20_status == "strong_buy" else 1
    elif close < ema20:
        ema20_status = "strong_sell" if close <= ema20 * 0.98 else "sell"
        score -= 2 if ema20_status == "strong_sell" else 1
    else:
        ema20_status = "neutral"

    if ema20 > ema50:
        ema50_status = "strong_buy" if close > ema50 else "buy"
        score += 2 if ema50_status == "strong_buy" else 1
    elif ema20 < ema50:
        ema50_status = "strong_sell" if close < ema50 else "sell"
        score -= 2 if ema50_status == "strong_sell" else 1
    else:
        ema50_status = "neutral"

    if rsi >= 65:
        rsi_status = "strong_buy"
        score += 2
    elif 50 <= rsi < 65:
        rsi_status = "buy"
        score += 1
    elif 30 <= rsi <= 40:
        rsi_status = "sell"
        score -= 1
    elif rsi < 30:
        rsi_status = "strong_sell"
        score -= 2
    else:
        rsi_status = "neutral"

    if score >= 4:
        signal = "STRONG_BULLISH"
    elif score >= 1:
        signal = "BULLISH"
    elif score <= -4:
        signal = "STRONG_BEARISH"
    elif score <= -1:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    power_score = min(10, max(1, round(((score + 5) / 10) * 10)))

    return {
        "ema14": round(ema14, 2),
        "ema_cross": ema_cross,
        "ema20_status": ema20_status,
        "ema50_status": ema50_status,
        "rsi_status": rsi_status,
        "signal": signal,
        "power_score": power_score
    }

def fetch_real_data():
    symbol_map = {f"{item['ticker']}.JK": item for item in TICKERS}
    ticker_symbols = list(symbol_map.keys())
    all_download_tickers = ticker_symbols + ["^JKSE"]

    print("⚡ Mengunduh data emiten dan IHSG (^JKSE)...")
    download_data = yf.download(all_download_tickers, period="100d", interval="1d", group_by="ticker", progress=False)

    ihsg_data = {
        "name": "IHSG", "open": 0, "high": 0, "low": 0, "close": 0, "prev_close": 0, "change_pct": 0.0
    }

    try:
        if "^JKSE" in download_data and not download_data["^JKSE"].dropna().empty:
            df_ihsg = download_data["^JKSE"].dropna().copy()
            if len(df_ihsg) >= 2:
                latest_ihsg = df_ihsg.iloc[-1]
                prev_ihsg = df_ihsg.iloc[-2]
                c_val, p_val = float(latest_ihsg['Close']), float(prev_ihsg['Close'])
                chg = round(((c_val - p_val) / p_val) * 100, 2) if p_val > 0 else 0.0
                ihsg_data = {
                    "name": "IHSG",
                    "open": round(float(latest_ihsg['Open']), 2),
                    "high": round(float(latest_ihsg['High']), 2),
                    "low": round(float(latest_ihsg['Low']), 2),
                    "close": round(c_val, 2),
                    "prev_close": round(p_val, 2),
                    "change_pct": chg
                }
    except Exception as e:
        print(f"Gagal memuat IHSG: {e}")

    all_stocks = []
    for symbol, stock in symbol_map.items():
        try:
            if symbol in download_data and not download_data[symbol].dropna().empty:
                df = download_data[symbol].dropna().copy()
            else:
                continue

            if len(df) < 50:
                continue

            df['EMA14'] = df['Close'].ewm(span=14, adjust=False).mean()
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['RSI'] = calculate_rsi(df['Close'], 14)

            latest, previous = df.iloc[-1], df.iloc[-2]
            close, prev_close = float(latest['Close']), float(previous['Close'])
            
            if close <= 0 or prev_close <= 0:
                continue

            change_pct = round(((close - prev_close) / prev_close) * 100, 2)
            ema14, ema20, ema50 = float(latest['EMA14']), float(latest['EMA20']), float(latest['EMA50'])
            rsi = round(float(latest['RSI']), 1) if not pd.isna(latest['RSI']) else 50.0

            swing_res = calculate_swing_strategy(close, ema14, ema20, ema50, rsi)

            stop_loss = round(close * 0.95, 2)
            tp1 = round(close * 1.05, 2)
            tp2 = round(close * 1.10, 2)

            tp1_hit = close >= tp1
            tp2_hit = close >= tp2
            cl_hit = close <= stop_loss

            item = {
                "ticker": stock["ticker"],
                "close": round(close, 2),
                "change_pct": change_pct,
                "category": stock["category"],
                "ema14": round(ema14, 2),
                "ema_cross": swing_res["ema_cross"],
                "ema20": round(ema20, 2),
                "ema20_status": swing_res["ema20_status"],
                "ema50": round(ema50, 2),
                "ema50_status": swing_res["ema50_status"],
                "rsi": rsi,
                "rsi_status": swing_res["rsi_status"],
                "signal": swing_res["signal"],
                "power_score": swing_res["power_score"],
                "stop_loss": stop_loss,
                "take_profit_1": tp1,
                "take_profit_2": tp2,
                "tp1_hit": tp1_hit,
                "tp2_hit": tp2_hit,
                "cl_hit": cl_hit
            }
            all_stocks.append(item)
        except Exception:
            continue

    all_stocks = sorted(all_stocks, key=lambda x: (x["power_score"], x["change_pct"]), reverse=True)

    top_bearish = sorted(all_stocks, key=lambda x: (x["power_score"], x["change_pct"]))[:20]
    top_10_entry = [s for s in all_stocks if s["signal"] in ["STRONG_BULLISH", "BULLISH"]][:10]

    swing_setup = [s for s in all_stocks if s["signal"] in ["BULLISH", "STRONG_BULLISH"]]
    top_gainers = sorted(all_stocks, key=lambda x: x["change_pct"], reverse=True)[:20]
    top_movers = sorted(all_stocks, key=lambda x: abs(x["change_pct"]), reverse=True)[:20]
    bluechips = [s for s in all_stocks if s["category"] == "Bluechip"]

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_scanned": len(all_stocks),
        "ihsg": ihsg_data,
        "top_10_entry": top_10_entry,
        "swing_setup": swing_setup,
        "top_gainers": top_gainers,
        "top_movers": top_movers,
        "bluechips": bluechips,
        "top_bearish": top_bearish,
        "all_stocks": all_stocks
    }

    temp_filename, final_filename = "data.json.tmp", "data.json"
    with open(temp_filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    os.replace(temp_filename, final_filename)
    print(f"🚀 Berhasil! {len(all_stocks)} emiten tersimpan.")

if __name__ == "__main__":
    fetch_real_data()
