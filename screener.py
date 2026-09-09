import json
import datetime
import yfinance as yf
import pandas as pd

# Daftar Ticker Khusus & Komprehensif (Bluechip, Popular, High Volatility/Gainer)
TICKERS_EXPANDED = [
    # Top Movers & Volatile / Penny Stocks
    "BNBR", "JGLE", "JARR", "BUMI", "DEWA", "BRMS", "ENRG", "DOOID", "GOTO", "STRT", 
    "HUMI", "LEAD", "CGAS", "SOLA", "WIFI", "PTRO", "CUAN", "PANI", "FILM", "DOOH",
    # Bluechip & Big Caps
    "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "AMMN", "BREN", "TPIA", "ADRO", 
    "PGAS", "BRIS", "UNVR", "ICBP", "INDF", "CPIN", "JPFA", "KLBF", "MIKA", "MDKA", 
    "MBMA", "ANTM", "INCO", "PTBA", "ITMG", "HRUM", "MEDC", "AKRA", "BSDE", "CTRA", 
    "PRAW", "SMRA", "PTPP", "ADHI", "WIKA", "JSMR", "PGEO", "ISAT", "EXCL", "TOWR", 
    "TBIG", "INKP", "TKIM", "SMGR", "INTP", "GGRM", "HMSP", "BFIN", "PNBN", "BNGA", 
    "BBTN", "ARTO", "MEDP", "ACES", "MAPI", "MAPA", "ERAA", "KPGP", "SSIA", "SIDO", 
    "MYOR", "CMRY", "AMRT", "AUTO", "GJTL", "SMSM", "SILO", "SAME", "IRRA", "KAEF", 
    "INAF", "ELSA", "MBSS", "SMDR", "TMAS", "BIRD", "ASSA", "GTVN", "WOOD", "APLN", 
    "ASRI", "MDLN", "BEST", "DMAS", "KIJA", "LPKR", "LPCK", "EMTK", "SCMA", "UNTR"
]

TICKERS_BLUECHIP_LIST = [
    "ACES", "ADRO", "AMRT", "ANTM", "ARTO", "ASII", "BBCA", "BBNI", "BBRI", "BBTN",
    "BMRI", "BRPT", "CPIN", "EMTK", "EXCL", "GOTO", "HRUM", "ICBP", "INDF", "INKP",
    "INTP", "ISAT", "ITMG", "JSMR", "KLBF", "MDKA", "MEDC", "MIKA", "MYOR", "PGAS",
    "PTBA", "SCMA", "SIDO", "SMGR", "TBIG", "TPIA", "TLKM", "TOWR", "UNVR", "UNTR"
]

def fetch_ihsg_data():
    """Mengambil Data Paten IHSG (^JKSE)"""
    try:
        ihsg = yf.Ticker("^JKSE")
        df = ihsg.history(period="5d")
        if not df.empty and len(df) >= 2:
            curr = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            chg = round(((curr - prev) / prev) * 100, 2)
            return {"price": int(curr), "change": chg}
    except Exception as e:
        print(f"Gagal mengambil data IHSG: {e}")
    return {"price": 0, "change": 0.0}

def fetch_top_gainers():
    try:
        gainers = yf.TradingData().get_gainers()
        return [t.replace('.JK', '') for t in gainers.index if t.endswith('.JK')]
    except Exception:
        return []

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def estimate_bandarmology(df):
    recent = df.tail(5)
    buy_vol = 0
    sell_vol = 0
    for i in range(len(recent)):
        c = recent['Close'].iloc[i]
        o = recent['Open'].iloc[i]
        v = recent['Volume'].iloc[i]
        if c >= o:
            buy_vol += v
        else:
            sell_vol += v
            
    if buy_vol > sell_vol * 1.4:
        return "AKUMULASI"
    elif sell_vol > buy_vol * 1.4:
        return "DISTRIBUSI"
    return "NEUTRAL"

def process_stock(ticker_symbol, top_gainers_set):
    formatted_ticker = ticker_symbol if ticker_symbol.endswith('.JK') else f"{ticker_symbol}.JK"
    clean_ticker = ticker_symbol.replace('.JK', '')

    try:
        stock = yf.Ticker(formatted_ticker)
        df = stock.history(period="6m")

        if df.empty or len(df) < 20:
            return None

        close_series = df['Close']
        raw_price = close_series.iloc[-1]
        current_price = int(raw_price) if not pd.isna(raw_price) else 0

        # Filter Likuiditas Minimum (Bisa disesuaikan agar emiten kecil tetap masuk)
        vol_today = df['Volume'].iloc[-1]
        turnover_today = current_price * vol_today
        if turnover_today < 200_000_000: # Min Transaksi Rp 200 Juta/hari
            return None

        raw_prev = close_series.iloc[-2]
        prev_price = float(raw_prev) if not pd.isna(raw_prev) else current_price
        change_pct = round(((current_price - prev_price) / prev_price) * 100, 2) if prev_price > 0 else 0.0

        vol_avg_20 = df['Volume'].tail(20).mean()
        vol_ratio = round(float(vol_today / vol_avg_20), 2) if vol_avg_20 > 0 else 0.0

        rsi_series = calculate_rsi(close_series)
        last_rsi = rsi_series.iloc[-1]
        current_rsi = round(float(last_rsi), 1) if not pd.isna(last_rsi) else 50.0

        ema20_val = close_series.ewm(span=20, adjust=False).mean().iloc[-1]
        ema50_val = close_series.ewm(span=50, adjust=False).mean().iloc[-1]
        
        ema20 = round(float(ema20_val), 1) if not pd.isna(ema20_val) else float(current_price)
        ema50 = round(float(ema50_val), 1) if not pd.isna(ema50_val) else float(current_price)

        stop_loss_dinamis = int(df['Low'].tail(5).min())
        target_price_dinamis = int(df['High'].tail(20).max())
        
        if stop_loss_dinamis >= current_price:
            stop_loss_dinamis = int(current_price * 0.95)
        if target_price_dinamis <= current_price:
            target_price_dinamis = int(current_price * 1.08)

        # Penentuan Kategori
        categories = ["ALL"]
        if clean_ticker in TICKERS_BLUECHIP_LIST:
            categories.append("BLUECHIP")
        if clean_ticker in top_gainers_set or change_pct >= 5.0:
            categories.append("TOP GAINERS")
        if vol_ratio >= 1.5 or abs(change_pct) >= 4.0:
            categories.append("HIGH VOLATILITY")

        return {
            "ticker": clean_ticker,
            "price": current_price,
            "change": change_pct,
            "rsi": current_rsi,
            "ema20": ema20,
            "ema50": ema50,
            "volRatio": vol_ratio,
            "bandarmology": estimate_bandarmology(df),
            "sl": stop_loss_dinamis,
            "tp": target_price_dinamis,
            "categories": categories
        }
    except Exception:
        return None

def main():
    ihsg_data = fetch_ihsg_data()
    top_gainers = fetch_top_gainers()
    top_gainers_set = set(top_gainers)
    
    combined_tickers = set(TICKERS_EXPANDED + top_gainers)
    all_tickers = sorted(list(combined_tickers))
    
    print(f"Memproses {len(all_tickers)} emiten IDX...")
    
    stocks_data = []
    for ticker in all_tickers:
        result = process_stock(ticker, top_gainers_set)
        if result:
            stocks_data.append(result)

    output = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ihsg": ihsg_data,
        "stocks": stocks_data
    }

    with open('data.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Data berhasil diperbarui! Total {len(stocks_data)} emiten masuk kriteria.")

if __name__ == "__main__":
    main()
