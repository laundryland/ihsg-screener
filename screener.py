import json
import pandas as pd
import yfinance as yf
from datetime import datetime

# Daftar emiten Bluechip & Utama
TICKERS_BASE = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK",
    "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", "BUKA.JK", "CPIN.JK",
    "EMTK.JK", "EXCL.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK",
    "INTP.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MIKA.JK",
    "MNCN.JK", "PGAS.JK", "PTBA.JK", "PTPP.JK", "SIDO.JK", "SMGR.JK", "TPIA.JK", "TLKM.JK",
    "TOWR.JK", "UNTR.JK", "UNVR.JK", "WIKA.JK", "BSDE.JK", "CTRA.JK", "PWON.JK", "SMRA.JK",
    "BFIN.JK", "BNGA.JK", "BDMN.JK", "PNLF.JK", "TINS.JK", "NCKL.JK", "AMMN.JK", "CMRY.JK",
    "HEAL.JK", "MTEL.JK", "AUTO.JK", "DRMA.JK", "GJTL.JK", "MAPA.JK", "AVIA.JK", "BIRD.JK",
    "ERAA.JK", "ENRG.JK", "ESSA.JK", "HAIS.JK", "IMAS.JK", "IRRA.JK", "KAEF.JK", "MYOR.JK",
    "PEGE.JK", "RAAM.JK", "RALS.JK", "ROTI.JK", "SCMA.JK", "SMSM.JK", "TAPG.JK", "TKIM.JK",
    "TOBA.JK", "TSPC.JK", "WOOD.JK", "BUMI.JK", "DEWA.JK", "BRMS.JK", "PANI.JK", "CUAN.JK",
    "BREN.JK", "CGAS.JK", "PSAB.JK", "DOOH.JK", "HUMI.JK"
]

def fetch_top_gainers():
    return ["FILM.JK", "SMCB.JK", "MARK.JK", "SSMS.JK", "SIMP.JK"]

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_screener():
    all_tickers = list(set(TICKERS_BASE + fetch_top_gainers()))
    
    # Ambil Data IHSG
    ihsg_change = 0.0
    try:
        ihsg_df = yf.Ticker("^JKSE").history(period="5d")
        if isinstance(ihsg_df.columns, pd.MultiIndex):
            ihsg_df.columns = ihsg_df.columns.get_level_values(0)
        if len(ihsg_df) >= 2:
            close_curr = float(ihsg_df['Close'].iloc[-1])
            close_prev = float(ihsg_df['Close'].iloc[-2])
            ihsg_change = round(((close_curr - close_prev) / close_prev) * 100, 2)
    except Exception as e:
        print(f"[WARN] Gagal mengambil IHSG: {e}")

    stocks_data = []
    print(f"Mengunduh data untuk {len(all_tickers)} emiten...")

    for ticker in all_tickers:
        try:
            df = yf.Ticker(ticker).history(period="3mo")
            
            # Meratakan MultiIndex jika ada
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if df.empty or len(df) < 30:
                continue

            # Bersihkan nilai NaN
            df = df.dropna(subset=['Close', 'Volume'])

            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            price = float(curr['Close'])
            prev_price = float(prev['Close'])
            change_pct = float(((price - prev_price) / prev_price) * 100)
            
            vol_avg = float(curr['Vol_Avg']) if pd.notnull(curr['Vol_Avg']) and curr['Vol_Avg'] > 0 else 1.0
            vol_ratio = float(curr['Volume'] / vol_avg)

            rsi_val = float(curr['RSI']) if pd.notnull(curr['RSI']) else 50.0

            stocks_data.append({
                "ticker": ticker.replace(".JK", ""),
                "price": round(price, 2),
                "change": round(change_pct, 2),
                "rsi": round(rsi_val, 2),
                "ema20": round(float(curr['EMA20']), 2),
                "ema50": round(float(curr['EMA50']), 2),
                "vol_ratio": round(vol_ratio, 2),
                "tp": round(price * 1.05, 2),
                "sl": round(price * 0.95, 2)
            })
        except Exception as e:
            # Lewati emiten yang bermasalah tanpa menghentikan program
            continue

    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ihsg": ihsg_change,
        "stocks": stocks_data
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"[SUCCESS] Berhasil memproses {len(stocks_data)} emiten ke data.json")

if __name__ == "__main__":
    run_screener()
