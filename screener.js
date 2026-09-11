import os
import json
import time
from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf

# Timezone Jakarta (WIB)
WIB = pytz.timezone('Asia/Jakarta')

# Daftar Emiten Pilihan (Master List)
TICKERS_MASTER = [
    # Bluechip
    {"ticker": "BBCA", "category": "Bluechip"}, {"ticker": "BBRI", "category": "Bluechip"},
    {"ticker": "BMRI", "category": "Bluechip"}, {"ticker": "BBNI", "category": "Bluechip"},
    {"ticker": "TLKM", "category": "Bluechip"}, {"ticker": "ASII", "category": "Bluechip"},
    {"ticker": "UNVR", "category": "Bluechip"}, {"ticker": "ICBP", "category": "Bluechip"},
    {"ticker": "INDF", "category": "Bluechip"}, {"ticker": "AMRT", "category": "Bluechip"},
    {"ticker": "TPIA", "category": "Bluechip"}, {"ticker": "BREN", "category": "Bluechip"},
    {"ticker": "GOTO", "category": "Bluechip"},
    # Energy & Mining
    {"ticker": "ADRO", "category": "IDX Liquid"}, {"ticker": "PTBA", "category": "IDX Liquid"},
    {"ticker": "ITMG", "category": "IDX Liquid"}, {"ticker": "MEDC", "category": "IDX Liquid"},
    {"ticker": "ANTM", "category": "IDX Liquid"}, {"ticker": "INCO", "category": "IDX Liquid"},
    {"ticker": "PGAS", "category": "IDX Liquid"}, {"ticker": "AKRA", "category": "IDX Liquid"},
    {"ticker": "AMMN", "category": "IDX Liquid"}, {"ticker": "CUAN", "category": "IDX Liquid"},
    {"ticker": "BRMS", "category": "IDX Liquid"}, {"ticker": "BUMI", "category": "IDX Liquid"},
    # Banking & Finance
    {"ticker": "BRIS", "category": "IDX Liquid"}, {"ticker": "BBTN", "category": "IDX Liquid"},
    {"ticker": "BDMN", "category": "IDX Liquid"}, {"ticker": "BNGA", "category": "IDX Liquid"},
    {"ticker": "ARTO", "category": "IDX Liquid"}, {"ticker": "BBYB", "category": "IDX Liquid"},
    # Telecommunication & Tech
    {"ticker": "EXCL", "category": "IDX Liquid"}, {"ticker": "ISAT", "category": "IDX Liquid"},
    {"ticker": "TOWR", "category": "IDX Liquid"},
    # Consumer & Property
    {"ticker": "MYOR", "category": "IDX Liquid"}, {"ticker": "ACES", "category": "IDX Liquid"},
    {"ticker": "MAPI", "category": "IDX Liquid"}, {"ticker": "BSDE", "category": "IDX Liquid"},
    {"ticker": "CTRA", "category": "IDX Liquid"}, {"ticker": "PWON", "category": "IDX Liquid"},
    {"ticker": "SMGR", "category": "IDX Liquid"}, {"ticker": "UNTR", "category": "IDX Liquid"}
]

def calculate_rsi(series, period=14):
    """Kalkulasi RSI manual menggunakan Pandas"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def fetch_ihsg():
    """Mengambil Data IHSG (^JKSE)"""
    try:
        ihsg_df = yf.download("^JKSE", period="5d", interval="1d", progress=False)
        if ihsg_df.empty or len(ihsg_df) < 2:
            return {"name": "IHSG", "close": 0, "prev_close": 0, "open": 0, "high": 0, "low": 0, "change_pct": 0}
        
        # Flatten MultiIndex columns if needed
        if isinstance(ihsg_df.columns, pd.MultiIndex):
            ihsg_df.columns = ihsg_df.columns.get_level_values(0)

        close = float(ihsg_df['Close'].iloc[-1])
        prev_close = float(ihsg_df['Close'].iloc[-2])
        open_price = float(ihsg_df['Open'].iloc[-1])
        high_price = float(ihsg_df['High'].iloc[-1])
        low_price = float(ihsg_df['Low'].iloc[-1])
        
        change_pct = round(((close - prev_close) / prev_close) * 100, 2)
        
        return {
            "name": "IHSG",
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "change_pct": change_pct
        }
    except Exception as e:
        print(f"⚠️ Warning: Gagal mengambil data IHSG: {e}")
        return {"name": "IHSG", "close": 0, "prev_close": 0, "open": 0, "high": 0, "low": 0, "change_pct": 0}

def process_screener():
    print("🚀 Memulai pemprosesan Screener Saham...")
    
    # 1. Fetch IHSG
    ihsg_data = fetch_ihsg()

    # 2. Prepare Batch Download Tickers
    ticker_symbols = [f"{item['ticker']}.JK" for item in TICKERS_MASTER]
    ticker_map = {f"{item['ticker']}.JK": item for item in TICKERS_MASTER}

    print(f"📥 Mengunduh data untuk {len(ticker_symbols)} saham dari Yahoo Finance...")
    
    try:
        # Download semua saham sekaligus untuk efisiensi & menghindari rate limit
        df_all = yf.download(ticker_symbols, period="6m", interval="1d", group_by='ticker', progress=False)
    except Exception as e:
        print(f"❌ Error saat batch download: {e}")
        return

    processed_stocks = []

    for symbol_jk, meta in ticker_map.items():
        ticker_code = meta['ticker']
        
        try:
            # Ambil sub-dataframe untuk ticker bersangkutan
            if len(ticker_symbols) > 1:
                if symbol_jk not in df_all.columns.levels[0]:
                    continue
                df = df_all[symbol_jk].dropna()
            else:
                df = df_all.dropna()

            if len(df) < 50: # Minimal data untuk menghitung EMA50
                continue

            # Menghitung Indikator
            close_series = df['Close']
            df['EMA14'] = close_series.ewm(span=14, adjust=False).mean()
            df['EMA50'] = close_series.ewm(span=50, adjust=False).mean()
            df['RSI'] = calculate_rsi(close_series, 14)

            # Baris Terakhir & Penutupan Sebelumnya
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]

            close = float(last_row['Close'])
            prev_close = float(prev_row['Close'])
            
            if prev_close == 0:
                continue

            change_pct = round(((close - prev_close) / prev_close) * 100, 2)
            ema14 = float(last_row['EMA14'])
            ema50 = float(last_row['EMA50'])
            rsi = float(last_row['RSI']) if not pd.isna(last_row['RSI']) else 50.0

            # Penentuan Sinyal & Score
            signal = "NEUTRAL"
            power_score = 5

            if close > ema14 and ema14 > ema50:
                if rsi > 50 and rsi < 70:
                    signal = "STRONG_BULLISH"
                    power_score = 9 if change_pct > 0 else 8
                else:
                    signal = "BULLISH"
                    power_score = 7
            elif close < ema14 and ema14 < ema50:
                if rsi < 50:
                    signal = "STRONG_BEARISH"
                    power_score = 1 if change_pct < 0 else 2
                else:
                    signal = "BEARISH"
                    power_score = 3

            # Trading Plan Calculation
            stop_loss = round(close * 0.95)       # Cut loss -5%
            take_profit_1 = round(close * 1.05)   # TP1 +5%
            take_profit_2 = round(close * 1.10)   # TP2 +10%

            stock_obj = {
                "ticker": ticker_code,
                "category": meta['category'],
                "close": round(close),
                "change_pct": change_pct,
                "ema14": round(ema14),
                "ema14_status": "strong_buy" if close > ema14 else "sell",
                "ema50": round(ema50),
                "ema50_status": "strong_buy" if ema14 > ema50 else "sell",
                "rsi": round(rsi, 1),
                "rsi_status": "buy" if 40 <= rsi <= 65 else ("overbought" if rsi > 70 else "oversold"),
                "signal": signal,
                "power_score": power_score,
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2
            }
            processed_stocks.append(stock_obj)

        except Exception as err:
            print(f"⚠️ Skip {ticker_code} karena error: {err}")
            continue

    # 3. Kategori Output
    swing_setup = [s for s in processed_stocks if s['signal'] in ['STRONG_BULLISH', 'BULLISH']]
    swing_setup.sort(key=lambda x: x['power_score'], reverse=True)

    top_10_entry = swing_setup[:10]

    top_gainers = sorted(processed_stocks, key=lambda x: x['change_pct'], reverse=True)[:15]
    top_bearish = sorted(processed_stocks, key=lambda x: x['change_pct'])[:15]
    bluechips = [s for s in processed_stocks if s['category'] == 'Bluechip']
    
    # Sort All Stocks A-Z
    all_stocks = sorted(processed_stocks, key=lambda x: x['ticker'])

    output_data = {
        "last_updated": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB"),
        "ihsg": ihsg_data,
        "top_10_entry": top_10_entry,
        "swing_setup": swing_setup,
        "top_gainers": top_gainers,
        "top_movers": top_gainers[:10],
        "bluechips": bluechips,
        "top_bearish": top_bearish,
        "all_stocks": all_stocks
    }

    # 4. Save to data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Sukses! {len(processed_stocks)} saham berhasil diproses dan disimpan ke data.json.")

if __name__ == "__main__":
    process_screener()
