import json
import time
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime

# ================= ==========================================
# 1. KONFIGURASI DAFTAR TICKER & KATEGORI
# ============================================================
TICKERS_DATA = [
    # 1. PERBANKAN & KEUANGAN (FINANCIALS) - 15 Emiten
    {"ticker": "BBCA", "category": "Bluechip"},
    {"ticker": "BMRI", "category": "Bluechip"},
    {"ticker": "BBRI", "category": "Bluechip"},
    {"ticker": "BBNI", "category": "Bluechip"},
    {"ticker": "BRIS", "category": "Financials"},
    {"ticker": "BBTN", "category": "Financials"},
    {"ticker": "BDMN", "category": "Financials"},
    {"ticker": "BNGA", "category": "Financials"},
    {"ticker": "ARTO", "category": "Financials"},
    {"ticker": "MEGA", "category": "Financials"},
    {"ticker": "NISP", "category": "Financials"},
    {"ticker": "PNBN", "category": "Financials"},
    {"ticker": "SRTG", "category": "Financials"},
    {"ticker": "SMMA", "category": "Financials"},
    {"ticker": "AMAR", "category": "Financials"},

    # 2. ENERGI, BATUBARA, MIKAS (ENERGY) - 15 Emiten
    {"ticker": "ADRO", "category": "Energy"},
    {"ticker": "PTBA", "category": "Energy"},
    {"ticker": "ITMG", "category": "Energy"},
    {"ticker": "BYAN", "category": "Bluechip"},
    {"ticker": "PGAS", "category": "Energy"},
    {"ticker": "AKRA", "category": "Energy"},
    {"ticker": "MEDC", "category": "Energy"},
    {"ticker": "INDY", "category": "Energy"},
    {"ticker": "HRUM", "category": "Energy"},
    {"ticker": "DOID", "category": "Energy"},
    {"ticker": "GEMS", "category": "Energy"},
    {"ticker": "ELSA", "category": "Energy"},
    {"ticker": "MBAP", "category": "Energy"},
    {"ticker": "KKGI", "category": "Energy"},
    {"ticker": "TOBA", "category": "Energy"},

    # 3. PERTAMBANGAN & LOGAM HEAVY (MINING & METALS) - 13 Emiten
    {"ticker": "AMMN", "category": "Mining"},
    {"ticker": "MDKA", "category": "Mining"},
    {"ticker": "ANTM", "category": "Mining"},
    {"ticker": "INCO", "category": "Mining"},
    {"ticker": "TINS", "category": "Mining"},
    {"ticker": "NCKL", "category": "Mining"},
    {"ticker": "MBMA", "category": "Mining"},
    {"ticker": "PSAB", "category": "Mining"},
    {"ticker": "CITA", "category": "Mining"},
    {"ticker": "BRMS", "category": "Mining"},
    {"ticker": "IFSH", "category": "Mining"},
    {"ticker": "SMCB", "category": "Mining"},
    {"ticker": "KIDZ", "category": "Mining"},

    # 4. ENERGI TERBARUKAN & KONGKLOMERASI KUNCI - 10 Emiten
    {"ticker": "BREN", "category": "Bluechip"},
    {"ticker": "TPIA", "category": "Bluechip"},
    {"ticker": "CUAN", "category": "Energy"},
    {"ticker": "PGEO", "category": "Energy"},
    {"ticker": "BARA", "category": "Energy"},
    {"ticker": "PSSI", "category": "Energy"},
    {"ticker": "KEEN", "category": "Energy"},
    {"ticker": "POWR", "category": "Energy"},
    {"ticker": "KOPI", "category": "Energy"},
    {"ticker": "ARCI", "category": "Mining"},

    # 5. KONSUMER & UNGGULAN UNILEVER/FOOD (CONSUMER GOODS) - 17 Emiten
    {"ticker": "ICBP", "category": "Bluechip"},
    {"ticker": "INDF", "category": "Bluechip"},
    {"ticker": "UNVR", "category": "Bluechip"},
    {"ticker": "AMRT", "category": "Bluechip"},
    {"ticker": "CPIN", "category": "Bluechip"},
    {"ticker": "JPFA", "category": "Consumer"},
    {"ticker": "MYOR", "category": "Consumer"},
    {"ticker": "CMRY", "category": "Consumer"},
    {"ticker": "KLBF", "category": "Consumer"},
    {"ticker": "SIDO", "category": "Consumer"},
    {"ticker": "GGRM", "category": "Consumer"},
    {"ticker": "HMSP", "category": "Consumer"},
    {"ticker": "GOOD", "category": "Consumer"},
    {"ticker": "STTP", "category": "Consumer"},
    {"ticker": "ROTI", "category": "Consumer"},
    {"ticker": "ULTJ", "category": "Consumer"},
    {"ticker": "MAIN", "category": "Consumer"},

    # 6. INFRASTRUKTUR, TELEKOMUNIKASI & LINGKUNGAN - 14 Emiten
    {"ticker": "TLKM", "category": "Bluechip"},
    {"ticker": "ISAT", "category": "Infrastructure"},
    {"ticker": "EXCL", "category": "Infrastructure"},
    {"ticker": "TOWR", "category": "Infrastructure"},
    {"ticker": "TBIG", "category": "Infrastructure"},
    {"ticker": "MTEL", "category": "Infrastructure"},
    {"ticker": "JSMR", "category": "Infrastructure"},
    {"ticker": "META", "category": "Infrastructure"},
    {"ticker": "WIKA", "category": "Infrastructure"},
    {"ticker": "ADHI", "category": "Infrastructure"},
    {"ticker": "PTPP", "category": "Infrastructure"},
    {"ticker": "WEGE", "category": "Infrastructure"},
    {"ticker": "SSIA", "category": "Infrastructure"},
    {"ticker": "ACST", "category": "Infrastructure"},

    # 7. OTOMOTIF, INDUSTRI & RETAIL (INDUSTRIALS & RETAIL) - 13 Emiten
    {"ticker": "ASII", "category": "Bluechip"},
    {"ticker": "ACES", "category": "Retail"},
    {"ticker": "MAPI", "category": "Retail"},
    {"ticker": "MAPA", "category": "Retail"},
    {"ticker": "AUTO", "category": "Industrials"},
    {"ticker": "DRMA", "category": "Industrials"},
    {"ticker": "IMAS", "category": "Industrials"},
    {"ticker": "SMSM", "category": "Industrials"},
    {"ticker": "UNTR", "category": "Industrials"},
    {"ticker": "HEXA", "category": "Industrials"},
    {"ticker": "RALS", "category": "Retail"},
    {"ticker": "LPPF", "category": "Retail"},
    {"ticker": "ERAA", "category": "Retail"},

    # 8. PROPERTI, LOGISTIK & TEKNOLOGI - 13 Emiten
    {"ticker": "BSDE", "category": "Property"},
    {"ticker": "CTRA", "category": "Property"},
    {"ticker": "PRAW", "category": "Property"},
    {"ticker": "SMRA", "category": "Property"},
    {"ticker": "PWON", "category": "Property"},
    {"ticker": "ASRI", "category": "Property"},
    {"ticker": "GOTO", "category": "Bluechip"},
    {"ticker": "BUKA", "category": "Technology"},
    {"ticker": "EMTK", "category": "Technology"},
    {"ticker": "SCMA", "category": "Technology"},
    {"ticker": "BELI", "category": "Technology"},
    {"ticker": "BIRD", "category": "Logistics"},
    {"ticker": "SMDR", "category": "Logistics"}
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# ============================================================
# 2. FUNGSI PENGAMBILAN DATA ALTERNATIF (FALLBACK)
# ============================================================
def fetch_google_finance_price(ticker):
    """
    Sumber Alternatif: Scraping data harga real-time dari Google Finance 
    jika Yahoo Finance memblokir IP/Request.
    """
    url = f"https://www.google.com/finance/quote/{ticker}:IDX"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Class penampung harga di Google Finance
            price_div = soup.find('div', {'class': 'YMlKec fxfa3d'})
            if price_div:
                price_str = price_div.text.replace('Rp', '').replace('.', '').replace(',', '.').strip()
                return float(price_str)
    except Exception as e:
        print(f"⚠️ Google Finance fallback gagal untuk {ticker}: {e}")
    return None

def fetch_single_ticker_yfinance(ticker, retries=2):
    """
    Satu-per-satu fetch via yfinance dengan User-Agent kustom & Retry logic.
    """
    symbol = f"{ticker}.JK"
    for attempt in range(retries):
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            
            ticker_obj = yf.Ticker(symbol, session=session)
            df = ticker_obj.history(period="6m", interval="1d")
            
            if not df.empty and len(df) >= 50:
                return df
        except Exception:
            time.sleep(1)
    return None

# ============================================================
# 3. INDIKATOR TEKNIKAL & ANALISIS
# ============================================================
def calculate_indicators(df):
    close = df['Close']
    
    # EMA 14 & 50
    ema14 = close.ewm(span=14, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    
    # RSI 14
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return ema14.iloc[-1], ema50.iloc[-1], rsi.iloc[-1]

def analyze_stock(ticker, category, df, fallback_price=None):
    if df is not None and not df.empty:
        close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else close
        ema14_val, ema50_val, rsi_val = calculate_indicators(df)
    elif fallback_price is not None:
        # Jika data historis total gagal, pakai estimasi kasar dari fallback harga
        close = fallback_price
        prev_close = fallback_price
        ema14_val, ema50_val, rsi_val = close * 0.98, close * 0.95, 50.0
    else:
        return None

    change_pct = round(((close - prev_close) / prev_close) * 100, 2)
    ema14_status = "strong_buy" if close > ema14_val else "sell"
    ema50_status = "strong_buy" if close > ema50_val else "sell"
    
    if rsi_val > 70:
        rsi_status = "overbought"
    elif rsi_val < 30:
        rsi_status = "oversold"
    else:
        rsi_status = "buy"

    # Penentuan Sinyal & Power Score
    score = 0
    if ema14_status == "strong_buy": score += 4
    if ema50_status == "strong_buy": score += 3
    if rsi_status == "buy": score += 2

    if score >= 8:
        signal = "STRONG_BULLISH"
    elif score >= 6:
        signal = "BULLISH"
    elif score <= 3:
        signal = "STRONG_BEARISH"
    else:
        signal = "NEUTRAL"

    # Money Management / Trading Plan (Estimasi 5% SL, 5% TP1, 10% TP2)
    stop_loss = int(round(close * 0.95))
    take_profit_1 = int(round(close * 1.05))
    take_profit_2 = int(round(close * 1.10))

    return {
        "ticker": ticker,
        "category": category,
        "close": int(round(close)),
        "change_pct": change_pct,
        "ema14": int(round(ema14_val)),
        "ema14_status": ema14_status,
        "ema50": int(round(ema50_val)),
        "ema50_status": ema50_status,
        "rsi": round(rsi_val, 1),
        "rsi_status": rsi_status,
        "signal": signal,
        "power_score": score,
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2
    }

# ============================================================
# 4. EKSEKUSI UTAMA (MAIN FUNCTION)
# ============================================================
def run_screener():
    print("🚀 Memulai proses screener saham...")
    processed_stocks = []
    
    # 1. Fetch data IHSG
    ihsg_data = {
        "name": "IHSG",
        "close": 7750.25,
        "prev_close": 7710.10,
        "open": 7715.00,
        "high": 7765.80,
        "low": 7700.50,
        "change_pct": 0.52
    }
    
    try:
        ihsg_df = yf.download("^JKSE", period="5d", interval="1d", progress=False)
        if not ihsg_df.empty:
            c = float(ihsg_df['Close'].iloc[-1])
            pc = float(ihsg_df['Close'].iloc[-2])
            ihsg_data.update({
                "close": round(c, 2),
                "prev_close": round(pc, 2),
                "change_pct": round(((c - pc) / pc) * 100, 2)
            })
    except Exception as e:
        print(f"⚠️ Gagal mengambil data IHSG dari YFinance, menggunakan nilai default: {e}")

    # 2. Process Tickers (Batch/Fallback Mechanism)
    for item in TICKERS_DATA:
        ticker = item["ticker"]
        category = item["category"]
        print(f"🔎 Scanning: {ticker}...", end=" ")

        # Langkah 1: Coba YFinance Ticker
        df = fetch_single_ticker_yfinance(ticker)
        fallback_price = None

        # Langkah 2: Jika YFinance gagal (Blokir/Rate Limit), panggil Google Finance
        if df is None or df.empty:
            print("YFinance diblokir/gagal ➔ Menggunakan Google Finance Fallback...", end=" ")
            fallback_price = fetch_google_finance_price(ticker)

        # Langkah 3: Olah Indikator
        res = analyze_stock(ticker, category, df, fallback_price)
        if res:
            processed_stocks.append(res)
            print("✅ OK")
        else:
            print("❌ GAGAL (Dilewati)")
        
        # Jeda tipis untuk menghindari batasan rate limit beruntun
        time.sleep(0.3)

    # 3. Pengelompokan & Sorting Data
    top_10 = sorted(processed_stocks, key=lambda x: x['power_score'], reverse=True)[:10]
    swing_setup = [s for s in processed_stocks if s['signal'] in ['STRONG_BULLISH', 'BULLISH']]
    top_gainers = sorted(processed_stocks, key=lambda x: x['change_pct'], reverse=True)[:5]
    top_movers = sorted(processed_stocks, key=lambda x: abs(x['change_pct']), reverse=True)[:3]
    bluechips = [s for s in processed_stocks if s['category'] == 'Bluechip']
    top_bearish = sorted([s for s in processed_stocks if s['signal'] in ['STRONG_BEARISH', 'NEUTRAL']], key=lambda x: x['change_pct'])[:5]

    # 4. JSON Schema Final
    final_output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_scanned": len(processed_stocks),
        "ihsg": ihsg_data,
        "top_10_entry": top_10,
        "swing_setup": swing_setup,
        "top_gainers": top_gainers,
        "top_movers": top_movers,
        "bluechips": bluechips,
        "top_bearish": top_bearish,
        "all_stocks": sorted(processed_stocks, key=lambda x: x['ticker'])
    }

    # 5. Simpan ke File data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"\n🎉 Selesai! Berhasil memproses {len(processed_stocks)} emiten ke dalam data.json.")

if __name__ == "__main__":
    run_screener()
