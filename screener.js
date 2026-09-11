import os
import json
import time
from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf

# Timezone Jakarta (WIB)
WIB = pytz.timezone('Asia/Jakarta')

# Master List 110 Emiten Potensial & Likuid (BEI/IDX)
TICKERS = [
    # --- BLUECHIP / BIG CAPS (15) ---
    {"ticker": "BBCA", "category": "Bluechip"}, {"ticker": "BBRI", "category": "Bluechip"},
    {"ticker": "BMRI", "category": "Bluechip"}, {"ticker": "BBNI", "category": "Bluechip"},
    {"ticker": "TLKM", "category": "Bluechip"}, {"ticker": "ASII", "category": "Bluechip"},
    {"ticker": "UNVR", "category": "Bluechip"}, {"ticker": "ICBP", "category": "Bluechip"},
    {"ticker": "INDF", "category": "Bluechip"}, {"ticker": "AMRT", "category": "Bluechip"},
    {"ticker": "TPIA", "category": "Bluechip"}, {"ticker": "BREN", "category": "Bluechip"},
    {"ticker": "BYAN", "category": "Bluechip"}, {"ticker": "CPIN", "category": "Bluechip"},
    {"ticker": "GOTO", "category": "Bluechip"},

    # --- ENERGY & COAL (15) ---
    {"ticker": "ADRO", "category": "Energy"}, {"ticker": "PTBA", "category": "Energy"},
    {"ticker": "ITMG", "category": "Energy"}, {"ticker": "MEDC", "category": "Energy"},
    {"ticker": "PGAS", "category": "Energy"}, {"ticker": "AKRA", "category": "Energy"},
    {"ticker": "BUMI", "category": "Energy"}, {"ticker": "HRUM", "category": "Energy"},
    {"ticker": "INDY", "category": "Energy"}, {"ticker": "DOID", "category": "Energy"},
    {"ticker": "ENRG", "category": "Energy"}, {"ticker": "ABMM", "category": "Energy"},
    {"ticker": "TOBA", "category": "Energy"}, {"ticker": "DEWA", "category": "Energy"},
    {"ticker": "MBSS", "category": "Energy"},

    # --- METALS & MINING (12) ---
    {"ticker": "ANTM", "category": "Mining"}, {"ticker": "INCO", "category": "Mining"},
    {"ticker": "AMMN", "category": "Mining"}, {"ticker": "CUAN", "category": "Mining"},
    {"ticker": "BRMS", "category": "Mining"}, {"ticker": "MBMA", "category": "Mining"},
    {"ticker": "NCKL", "category": "Mining"}, {"ticker": "PSAB", "category": "Mining"},
    {"ticker": "MDKA", "category": "Mining"}, {"ticker": "TINS", "category": "Mining"},
    {"ticker": "DKFT", "category": "Mining"}, {"ticker": "CITA", "category": "Mining"},

    # --- BANKING & FINANCIALS (12) ---
    {"ticker": "BRIS", "category": "Financials"}, {"ticker": "BBTN", "category": "Financials"},
    {"ticker": "BDMN", "category": "Financials"}, {"ticker": "BNGA", "category": "Financials"},
    {"ticker": "ARTO", "category": "Financials"}, {"ticker": "BBYB", "category": "Financials"},
    {"ticker": "BJTM", "category": "Financials"}, {"ticker": "BJBR", "category": "Financials"},
    {"ticker": "PNBN", "category": "Financials"}, {"ticker": "PNBS", "category": "Financials"},
    {"ticker": "NISP", "category": "Financials"}, {"ticker": "MEGA", "category": "Financials"},

    # --- CONSUMER GOODS & POULTRY (12) ---
    {"ticker": "MYOR", "category": "Consumer"}, {"ticker": "JPFA", "category": "Consumer"},
    {"ticker": "MAIN", "category": "Consumer"}, {"ticker": "CMRY", "category": "Consumer"},
    {"ticker": "STTP", "category": "Consumer"}, {"ticker": "ULTJ", "category": "Consumer"},
    {"ticker": "SIDO", "category": "Consumer"}, {"ticker": "GOOD", "category": "Consumer"},
    {"ticker": "ROTI", "category": "Consumer"}, {"ticker": "CAMP", "category": "Consumer"},
    {"ticker": "CLEO", "category": "Consumer"}, {"ticker": "KAEF", "category": "Consumer"},

    # --- RETAIL & HEALTHCARE (10) ---
    {"ticker": "ACES", "category": "Retail"}, {"ticker": "MAPI", "category": "Retail"},
    {"ticker": "MAPA", "category": "Retail"}, {"ticker": "LPPF", "category": "Retail"},
    {"ticker": "RALS", "category": "Retail"}, {"ticker": "HEAL", "category": "Healthcare"},
    {"ticker": "MIKA", "category": "Healthcare"}, {"ticker": "SILO", "category": "Healthcare"},
    {"ticker": "KLBF", "category": "Healthcare"}, {"ticker": "SAME", "category": "Healthcare"},

    # --- PROPERTY, REAL ESTATE & INFRASTRUCTURE (12) ---
    {"ticker": "BSDE", "category": "Property"}, {"ticker": "CTRA", "category": "Property"},
    {"ticker": "PWON", "category": "Property"}, {"ticker": "SMRA", "category": "Property"},
    {"ticker": "ASRI", "category": "Property"}, {"ticker": "PSSI", "category": "Property"},
    {"ticker": "JSMR", "category": "Infrastructure"}, {"ticker": "WIKA", "category": "Infrastructure"},
    {"ticker": "ADHI", "category": "Infrastructure"}, {"ticker": "PTPP", "category": "Infrastructure"},
    {"ticker": "WEGE", "category": "Infrastructure"}, {"ticker": "TOTL", "category": "Infrastructure"},

    # --- TELECOM, TECH & LOGISTICS (12) ---
    {"ticker": "EXCL", "category": "Telecom/Tech"}, {"ticker": "ISAT", "category": "Telecom/Tech"},
    {"ticker": "TOWR", "category": "Telecom/Tech"}, {"ticker": "TBIG", "category": "Telecom/Tech"},
    {"ticker": "MTEL", "category": "Telecom/Tech"}, {"ticker": "CENT", "category": "Telecom/Tech"},
    {"ticker": "EMTK", "category": "Telecom/Tech"}, {"ticker": "SCMA", "category": "Telecom/Tech"},
    {"ticker": "BUKA", "category": "Telecom/Tech"}, {"ticker": "MLPT", "category": "Telecom/Tech"},
    {"ticker": "ASSA", "category": "Logistics"}, {"ticker": "BIRD", "category": "Logistics"},

    # --- BASIC MATERIALS & HEAVY EQUIPMENT (10) ---
    {"ticker": "SMGR", "category": "Basic Material"}, {"ticker": "INTP", "category": "Basic Material"},
    {"ticker": "INKP", "category": "Basic Material"}, {"ticker": "TKIM", "category": "Basic Material"},
    {"ticker": "UNTR", "category": "Heavy Equipment"}, {"ticker": "HEXA", "category": "Heavy Equipment"},
    {"ticker": "KBLI", "category": "Basic Material"}, {"ticker": "AVIA", "category": "Basic Material"},
    {"ticker": "BRPT", "category": "Basic Material"}, {"ticker": "AUTO", "category": "Automotive"}
]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_ihsg():
    try:
        ihsg_df = yf.download("^JKSE", period="5d", interval="1d", progress=False)
        if ihsg_df.empty or len(ihsg_df) < 2:
            return {"name": "IHSG", "close": 0, "prev_close": 0, "open": 0, "high": 0, "low": 0, "change_pct": 0}
        
        if isinstance(ihsg_df.columns, pd.MultiIndex):
            ihsg_df.columns = ihsg_df.columns.get_level_values(0)

        close = float(ihsg_df['Close'].iloc[-1])
        prev_close = float(ihsg_df['Close'].iloc[-2])
        return {
            "name": "IHSG",
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "open": round(float(ihsg_df['Open'].iloc[-1]), 2),
            "high": round(float(ihsg_df['High'].iloc[-1]), 2),
            "low": round(float(ihsg_df['Low'].iloc[-1]), 2),
            "change_pct": round(((close - prev_close) / prev_close) * 100, 2)
        }
    except Exception as e:
        print(f"Error fetching IHSG: {e}")
        return {"name": "IHSG", "close": 0, "prev_close": 0, "open": 0, "high": 0, "low": 0, "change_pct": 0}

def main():
    print(f"🚀 Memulai Screener Saham untuk {len(TICKERS)} emiten...")
    ihsg = fetch_ihsg()
    
    symbols_jk = [f"{t['ticker']}.JK" for t in TICKERS]
    try:
        df_all = yf.download(symbols_jk, period="6m", interval="1d", group_by='ticker', progress=False)
    except Exception as e:
        print(f"❌ Batch Download Error: {e}")
        return

    stocks = []
    for item in TICKERS:
        t_code = item['ticker']
        s_jk = f"{t_code}.JK"
        
        try:
            if s_jk not in df_all.columns:
                continue
            
            df = df_all[s_jk].dropna()

            if len(df) < 50: 
                continue

            close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change_pct = round(((close - prev_close) / prev_close) * 100, 2)

            ema14 = float(df['Close'].ewm(span=14, adjust=False).mean().iloc[-1])
            ema50 = float(df['Close'].ewm(span=50, adjust=False).mean().iloc[-1])
            rsi_series = calculate_rsi(df['Close'], 14)
            rsi = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0

            signal = "NEUTRAL"
            power_score = 5

            if close > ema14 and ema14 > ema50:
                if 40 <= rsi <= 68:
                    signal = "STRONG_BULLISH"
                    power_score = 9 if change_pct > 0 else 8
                else:
                    signal = "BULLISH"
                    power_score = 7
            elif close < ema14 and ema14 < ema50:
                if rsi < 40:
                    signal = "STRONG_BEARISH"
                    power_score = 1
                else:
                    signal = "BEARISH"
                    power_score = 3

            stocks.append({
                "ticker": t_code,
                "category": item['category'],
                "close": round(close),
                "change_pct": change_pct,
                "ema14": round(ema14),
                "ema14_status": "strong_buy" if close > ema14 else "sell",
                "ema50": round(ema50),
                "ema50_status": "strong_buy" if ema14 > ema50 else "sell",
                "rsi": round(rsi, 1),
                "rsi_status": "buy" if 40 <= rsi <= 65 else ("overbought" if rsi > 70 else "neutral"),
                "signal": signal,
                "power_score": power_score,
                "stop_loss": round(close * 0.95),       # Cut Loss -5%
                "take_profit_1": round(close * 1.05),   # TP1 +5%
                "take_profit_2": round(close * 1.10)    # TP2 +10%
            })
        except Exception as e:
            print(f"⚠️ Skip {t_code}: {e}")

    swing_setup = sorted([s for s in stocks if s['signal'] in ['STRONG_BULLISH', 'BULLISH']], key=lambda x: x['power_score'], reverse=True)
    
    output = {
        "last_updated": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_scanned": len(stocks),
        "ihsg": ihsg,
        "top_10_entry": swing_setup[:10],
        "swing_setup": swing_setup,
        "top_gainers": sorted(stocks, key=lambda x: x['change_pct'], reverse=True)[:15],
        "top_movers": sorted(stocks, key=lambda x: x['change_pct'], reverse=True)[:10],
        "bluechips": [s for s in stocks if s['category'] == 'Bluechip'],
        "top_bearish": sorted(stocks, key=lambda x: x['change_pct'])[:15],
        "all_stocks": sorted(stocks, key=lambda x: x['ticker'])
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Selesai! {len(stocks)} emiten berhasil diproses ke data.json.")

if __name__ == "__main__":
    main()
