import json
import datetime
import yfinance as yf
import pandas as pd

# 1. Daftar Ticker Utama + Otomatis Format Suffix .JK
TICKERS_BASE = [
    "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "AMMN", "BREN", "TPIA", "ADRO", 
    "PGAS", "GOTO", "BRIS", "UNVR", "ICBP", "INDF", "CPIN", "JPFA", "KLBF", "MIKA", 
    "MDKA", "MBMA", "ANTM", "INCO", "PTBA", "ITMG", "HRUM", "MEDC", "AKRA", "CUAN", 
    "BUMI", "BRMS", "ENRG", "DEWA", "DOOID", "BSDE", "CTRA", "PRAW", "SMRA", "PTPP", 
    "ADHI", "WIKA", "JSMR", "PGEO", "ISAT", "EXCL", "TOWR", "TBIG", "INKP", "TKIM", 
    "SMGR", "INTP", "GGRM", "HMSP", "PANI", "FILM", "BFIN", "PNBN", "BNGA", "BBTN", 
    "ARTO", "MEDP", "ACES", "MAPI", "MAPA", "ERAA", "KPGP", "SSIA", "SIDO", "MYOR", 
    "CMRY", "AMRT", "DOOH", "STRT", "SOLA", "WIFI", "HUMI", "LEAD", "PTRO", "CGAS", 
    "ASHA", "AUTO", "GJTL", "SMSM", "SILO", "SAME", "IRRA", "KAEF", "INAF", "ELSA", 
    "MBSS", "SMDR", "TMAS", "BIRD", "ASSA", "GTVN", "WOOD", "APLN", "ASRI", "MDLN", 
    "BEST", "DMAS", "KIJA", "LPKR", "LPCK"
]

def fetch_top_gainers():
    """Mengambil saham top gainers dari yfinance"""
    try:
        gainers = yf.TradingData().get_gainers()
        # Filter ticker yang dari bursa Indonesia (.JK)
        jk_gainers = [t.replace('.JK', '') for t in gainers.index if t.endswith('.JK')]
        return jk_gainers
    except Exception as e:
        print(f"Warning: Gagal mengambil top gainers ({e}), menggunakan daftar default.")
        return []

def calculate_rsi(series, period=14):
    """Kalkulasi RSI 14-period"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def process_stock(ticker_symbol):
    formatted_ticker = ticker_symbol if ticker_symbol.endswith('.JK') else f"{ticker_symbol}.JK"
    clean_ticker = ticker_symbol.replace('.JK', '')

    try:
        stock = yf.Ticker(formatted_ticker)
        df = stock.history(period="1y")

        if df.empty or len(df) < 50:
            return None

        # Data Harga & Indikator Teknikal
        close_series = df['Close']
        current_price = int(close_series.iloc[-1])
        prev_price = close_series.iloc[-2]
        change_pct = round(((current_price - prev_price) / prev_price) * 100, 2)

        # 1. Vol Ratio
        vol_today = df['Volume'].iloc[-1]
        vol_avg_20 = df['Volume'].tail(20).mean()
        vol_ratio = round(vol_today / vol_avg_20, 2) if vol_avg_20 > 0 else 0.0

        # 2. RSI 14
        rsi_series = calculate_rsi(close_series)
        current_rsi = round(rsi_series.iloc[-1], 1) if not pd.isna(rsi_series.iloc[-1]) else 50.0

        # 3. EMA 20 & 50
        ema20 = round(close_series.ewm(span=20, adjust=False).mean().iloc[-1], 1)
        ema50 = round(close_series.ewm(span=50, adjust=False).mean().iloc[-1], 1)

        # 4. 52-Week High
        high_52 = int(df['High'].max())

        # Support / Resistance & Stop Loss Sederhana
        entry_price = current_price
        r1 = int(current_price * 1.05)
        cl1 = int(current_price * 0.95)

        # Nama Perusahaan (fallback ke ticker jika kosong)
        info = stock.info
        name = info.get('shortName') or info.get('longName') or clean_ticker

        return {
            "ticker": clean_ticker,
            "name": name,
            "price": current_price,
            "change": change_pct,
            "rsi": current_rsi,
            "ema20": ema20,
            "ema50": ema50,
            "volRatio": vol_ratio,
            "high52": high_52,
            "bandarmology": "NEUTRAL",  # Dipantau manual
            "entry": entry_price,
            "r1": r1,
            "cl1": cl1
        }
    except Exception as e:
        print(f"Gagal memproses {ticker_symbol}: {e}")
        return None

def main():
    # Gabungkan ticker bawaan + top gainers (tanpa duplikasi)
    top_gainers = fetch_top_gainers()
    all_tickers = list(set(TICKERS_BASE + top_gainers))
    
    print(f"Total emiten yang diproses: {len(all_tickers)}")
    
    stocks_data = []
    for ticker in all_tickers:
        result = process_stock(ticker)
        if result:
            stocks_data.append(result)

    # Susun payload JSON akhir
    output = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stocks": stocks_data
    }

    # Simpan ke data.json
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("Berhasil memperbarui data.json!")

if __name__ == "__main__":
    main()
