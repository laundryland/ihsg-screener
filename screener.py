import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

RAW_STOCKS = [
    "^JKSE", "TPIA.JK", "CUAN.JK", "SRSN.JK", "LABA.JK", "PACK.JK", "AMMN.JK", "ENRG.JK", 
    "INCO.JK", "INDY.JK", "PTRO.JK", "BREN.JK", "BUVA.JK", "ARTO.JK", "INDF.JK", 
    "ADRO.JK", "KBLV.JK", "PTBA.JK", "ITMG.JK", "HRUM.JK", "AKRA.JK", "MEDC.JK", 
    "PGAS.JK", "ANTM.JK", "MDKA.JK", "MBMA.JK", "NCKL.JK", "TINS.JK", "BRMS.JK", 
    "DEWA.JK", "AADI.JK", "BYAN.JK", "BULL.JK", "HUMI.JK", "DSSA.JK", "CBRE.JK", 
    "DOOH.JK", "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "BBTN.JK", 
    "BDMN.JK", "BNGA.JK", "GOTO.JK", "EMTK.JK", "SCMA.JK", "BUKA.JK", "TLKM.JK", 
    "ISAT.JK", "EXCL.JK", "JSMR.JK", "INET.JK", "WIFI.JK", "BACH.JK", "MDIA.JK", 
    "DATA.JK", "MTDL.JK", "ICBP.JK", "UNVR.JK", "MYOR.JK", "AMRT.JK", "ACES.JK", 
    "AGAR.JK", "MUTU.JK", "NIKL.JK", "KLBF.JK", "BSDE.JK", "CTRA.JK", "PWON.JK", 
    "KOTA.JK", "JGLE.JK", "BAPA.JK", "KOKA.JK", "CDIA.JK", "ROCK.JK", "MWOP.JK", 
    "DL.JK", "WBSA.JK", "SMRA.JK", "ASII.JK", "UNTR.JK", "BNBR.JK"
]

STOCKS = list(dict.fromkeys(RAW_STOCKS))

SECTOR_MAP = {
    "BBCA": "Perbankan", "BBRI": "Perbankan", "BMRI": "Perbankan", "BBNI": "Perbankan", 
    "BRIS": "Perbankan", "ARTO": "Perbankan", "BBTN": "Perbankan", "BDMN": "Perbankan", "BNGA": "Perbankan",
    "ADRO": "Energi", "PTBA": "Energi", "ITMG": "Energi", "HRUM": "Energi", 
    "AKRA": "Energi", "MEDC": "Energi", "PGAS": "Energi", "ENRG": "Energi", "BYAN": "Energi",
    "INDY": "Energi", "CUAN": "Energi", "BREN": "Energi", "AMMN": "Tambang",
    "ANTM": "Tambang", "INCO": "Tambang", "MDKA": "Tambang", "MBMA": "Tambang", 
    "NCKL": "Tambang", "TINS": "Tambang", "BRMS": "Tambang", "DEWA": "Tambang", "AADI": "Tambang",
    "DSSA": "Energi", "BULL": "Energi", "HUMI": "Energi", "CBRE": "Energi", "PTRO": "Energi",
    "GOTO": "Teknologi", "EMTK": "Teknologi", "BUKA": "Teknologi", "INET": "Teknologi",
    "WIFI": "Teknologi", "DATA": "Teknologi", "MTDL": "Teknologi", "KBLV": "Teknologi",
    "SCMA": "Media", "MDIA": "Media", "DOOH": "Media", "BACH": "Media", "LABA": "Teknologi",
    "TLKM": "Industri", "ISAT": "Industri", "EXCL": "Industri", "JSMR": "Industri",
    "ASII": "Industri", "UNTR": "Industri", "BNBR": "Industri", "NIKL": "Industri",
    "TPIA": "Industri", "SRSN": "Industri", "PACK": "Industri",
    "ICBP": "Konsumer", "INDF": "Konsumer", "UNVR": "Konsumer", "MYOR": "Konsumer", 
    "AMRT": "Konsumer", "ACES": "Konsumer", "AGAR": "Konsumer", "MUTU": "Konsumer", "KLBF": "Konsumer",
    "BSDE": "Properti", "CTRA": "Properti", "PWON": "Properti", "KOTA": "Properti",
    "JGLE": "Properti", "BAPA": "Properti", "KOKA": "Properti", "CDIA": "Properti",
    "ROCK": "Properti", "BUVA": "Properti", "MWOP": "Properti", "DL": "Properti", 
    "WBSA": "Properti", "SMRA": "Properti"
}

def clean_val(val, default=0):
    if isinstance(val, (pd.Series, np.ndarray)):
        val = val.item() if val.size == 1 else val[-1]
    if pd.isna(val) or np.isinf(val):
        return default
    return float(val)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def generate_trading_plan(price, support, resistance, vol_ratio, macd_status, rsi_val):
    # 1. SCALPING (Ketat & Cepat: Risk 1-1.5%)
    sc_entry = price
    sc_tp1 = round(price * 1.015)
    sc_tp2 = round(price * 1.03)
    sc_tp3 = round(price * 1.05)
    sc_cl1 = round(price * 0.99)
    sc_cl2 = round(price * 0.985)
    sc_cl3 = round(price * 0.98)

    # 2. SWING (Target Resisten & Support MA20: Risk 3-5%)
    sw_entry = price
    risk_sw = max(price - support, price * 0.03)
    sw_tp1 = round(price + (risk_sw * 1.0))
    sw_tp2 = round(price + (risk_sw * 1.8))
    sw_tp3 = round(resistance if resistance > price else price * 1.10)
    sw_cl1 = round(support)
    sw_cl2 = round(support * 0.98)
    sw_cl3 = round(support * 0.95)

    # 3. INVESTASI / LONG TERM (Nilai Wajar & Area Diskon: Risk 7-12%)
    inv_entry = f"{round(price * 0.98)} - {price}"
    inv_tp1 = round(price * 1.15)
    inv_tp2 = round(price * 1.30)
    inv_tp3 = round(price * 1.50)
    inv_cl1 = round(support * 0.92)
    inv_cl2 = round(support * 0.88)
    inv_cl3 = round(support * 0.82)

    return {
        "scalping": {"entry": sc_entry, "tp": [sc_tp1, sc_tp2, sc_tp3], "cl": [sc_cl1, sc_cl2, sc_cl3]},
        "swing": {"entry": sw_entry, "tp": [sw_tp1, sw_tp2, sw_tp3], "cl": [sw_cl1, sw_cl2, sw_cl3]},
        "investasi": {"entry": inv_entry, "tp": [inv_tp1, inv_tp2, inv_tp3], "cl": [inv_cl1, inv_cl2, inv_cl3]}
    }

def run_screener():
    print(f"Memulai unduh batch data untuk {len(STOCKS)} emiten...")
    data = yf.download(STOCKS, period="100d", interval="1d", group_by='ticker', progress=False)
    results = []

    for ticker_symbol in STOCKS:
        try:
            clean_name = "IHSG" if ticker_symbol == "^JKSE" else ticker_symbol.replace(".JK", "")
            df = data[ticker_symbol].copy() if len(STOCKS) > 1 else data.copy()
            df.dropna(how='all', inplace=True)

            if df.empty or len(df) < 5:
                continue

            close_prices, open_prices = df['Close'], df['Open']
            high_prices, low_prices = df['High'], df['Low']
            volumes = df['Volume']

            last_close = round(clean_val(close_prices.iloc[-1]))
            last_open = round(clean_val(open_prices.iloc[-1]))
            last_high = round(clean_val(high_prices.iloc[-1]))
            last_low = round(clean_val(low_prices.iloc[-1]))
            prev_close = round(clean_val(close_prices.iloc[-2])) if len(close_prices) > 1 else last_open

            ma20 = clean_val(close_prices.rolling(window=min(20, len(close_prices))).mean().iloc[-1])
            support = round(clean_val(low_prices.rolling(window=min(20, len(low_prices))).min().iloc[-1]))
            resistance = round(clean_val(high_prices.rolling(window=min(20, len(high_prices))).max().iloc[-1]))

            rsi_series = calculate_rsi(close_prices, 14)
            rsi_val = clean_val(rsi_series.iloc[-1], default=50)
            rsi_status = "BUY" if rsi_val <= 38 else ("SELL" if rsi_val >= 62 else "NEUTRAL")

            macd, macd_sig = calculate_macd(close_prices)
            macd_status = "BUY" if clean_val(macd.iloc[-1]) > clean_val(macd_sig.iloc[-1]) else "SELL"

            vol_ma20 = clean_val(volumes.rolling(window=min(20, len(volumes))).mean().iloc[-1], default=1)
            vol_ratio = round(clean_val(volumes.iloc[-1]) / vol_ma20, 2) if vol_ma20 > 0 else 1.0
            vol_status = "BUY" if vol_ratio >= 1.2 else ("SELL" if vol_ratio <= 0.8 else "NEUTRAL")

            fibo_rsi_status = "OVER SOLD" if rsi_val <= 30 else ("OVER BOUGHT" if rsi_val >= 70 else "NORMAL")

            buy_score = (1 if rsi_status == "BUY" else 0) + (1 if macd_status == "BUY" else 0) + (1 if vol_status == "BUY" else 0)
            sell_score = (1 if rsi_status == "SELL" else 0) + (1 if macd_status == "SELL" else 0) + (1 if vol_status == "SELL" else 0)

            signal = "NETRAL"
            if (last_close >= resistance and vol_ratio > 1.2) or buy_score == 3:
                signal = "STRONG BUY"
            elif buy_score >= 2 or (last_close > ma20 and macd_status == "BUY"):
                signal = "BUY"
            elif (last_close <= support and vol_ratio > 1.2) or sell_score == 3:
                signal = "STRONG SELL"
            elif sell_score >= 2 or (last_close < support):
                signal = "SELL"

            plans = generate_trading_plan(last_close, support, resistance, vol_ratio, macd_status, rsi_val)

            results.append({
                "ticker": clean_name,
                "category": "Indeks Utama" if clean_name == "IHSG" else SECTOR_MAP.get(clean_name, "Lainnya"),
                "price": last_close,
                "prev_close": prev_close,
                "open": last_open,
                "high": last_high,
                "low": last_low,
                "rsi": round(rsi_val, 2),
                "rsi_status": rsi_status,
                "ma20": round(ma20),
                "support": support,
                "resistance": resistance,
                "vol_ratio": vol_ratio,
                "vol_status": vol_status,
                "macd_status": macd_status,
                "fibo_rsi_status": fibo_rsi_status,
                "signal": signal,
                "plans": plans,
                "visual_indicator_info": "Indikator Visual Sinyal Transaksi Saham.",
                "image_source": "tupungato / Getty Images"
            })
        except Exception as e:
            print(f"Gagal memproses {ticker_symbol}: {str(e)}")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"updated_at": datetime.now().isoformat(), "stocks": results}, f, indent=2, ensure_ascii=False)
    print("Selesai! Hasil disimpan ke data.json.")

if __name__ == "__main__":
    run_screener()
