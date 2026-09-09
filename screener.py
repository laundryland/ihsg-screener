import json
import pandas as pd
import yfinance as yf
from datetime import datetime

TICKERS_BASE = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK",
    "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", "BUKA.JK", "CPIN.JK",
    "EMTK.JK", "EXCL.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK",
    "INTP.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MIKA.JK",
    "MNCN.JK", "PGAS.JK", "PTBA.JK", "PTPP.JK", "SIDO.JK", "SMGR.JK", "TPIA.JK", "TLKM.JK",
    "TOWR.JK", "UNTR.JK", "UNVR.JK", "WIKA.JK", "BSDE.JK", "CTRA.JK", "PWON.JK", "SMRA.JK",
    "BFIN.JK", "BNGA.JK", "BDMN.JK", "PNLF.JK", "TINS.JK", "NCKL.JK", "AMMN.JK", "NFXS.JK",
    "CMRY.JK", "HEAL.JK", "MTEL.JK", "AUTO.JK", "DRMA.JK", "GJTL.JK", "MAPA.JK", "NSSI.JK",
    "AVIA.JK", "BIRD.JK", "ERAA.JK", "ENRG.JK", "ESSA.JK", "HAIS.JK", "IMAS.JK",
    "IRRA.JK", "KAEF.JK", "MYOR.JK", "PEGE.JK", "RAAM.JK", "RALS.JK", "ROTI.JK", "SCMA.JK",
    "SMSM.JK", "TAPG.JK", "TKIM.JK", "TOBA.JK", "TSPC.JK", "WOOD.JK", "BUMI.JK", "DEWA.JK",
    "BRMS.JK", "PANI.JK", "CUAN.JK", "BREN.JK", "CGAS.JK", "PSAB.JK", "DOOH.JK", "HUMI.JK"
]

def fetch_top_gainers():
    return ["FILM.JK", "SMCB.JK", "MARK.JK", "SSMS.JK", "SIMP.JK"]

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_screener():
    all_tickers = list(set(TICKERS_BASE + fetch_top_gainers()))
    
    # Safely fetch IHSG
    ihsg_change = 0.0
    try:
        ihsg = yf.Ticker("^JKSE").history(period="5d")
        if len(ihsg) >= 2:
            ihsg_change = round(((ihsg['Close'].iloc[-1] - ihsg['Close'].iloc[-2]) / ihsg['Close'].iloc[-2]) * 100, 2)
    except Exception as e:
        print(f"Gagal mengambil data IHSG: {e}")

    stocks_data = []

    print("Mengunduh data pasar...")
    for ticker in all_tickers:
        try:
            df = yf.Ticker(ticker).history(period="3mo")
            if df.empty or len(df) < 30:
                continue

            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['RSI'] = calculate_rsi(df)
            df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            price = float(curr['Close'])
            change_pct = float(((price - prev['Close']) / prev['Close']) * 100)
            
            vol_avg = float(curr['Vol_Avg']) if pd.notnull(curr['Vol_Avg']) else 0
            vol_ratio = float(curr['Volume'] / vol_avg) if vol_avg > 0 else 1.0

            stocks_data.append({
                "ticker": ticker.replace(".JK", ""),
                "price": round(price, 2),
                "change": round(change_pct, 2),
                "rsi": round(float(curr['RSI']), 2) if pd.notnull(curr['RSI']) else 50.0,
                "ema20": round(float(curr['EMA20']), 2),
                "ema50": round(float(curr['EMA50']), 2),
                "vol_ratio": round(vol_ratio, 2),
                "tp": round(price * 1.05, 2),
                "sl": round(price * 0.95, 2)
            })
        except Exception as e:
            # Skip ticker jika terjadi error agar script tidak berhenti
            continue

    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ihsg": ihsg_change,
        "stocks": stocks_data
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Selesai! {len(stocks_data)} emiten berhasil disimpan.")

if __name__ == "__main__":
    run_screener()
