import json
import random
from datetime import datetime

# Daftar sampel saham IHSG
TICKERS = [
    ("BBCA", "Bank Central Asia Tbk"),
    ("BBRI", "Bank Rakyat Indonesia Tbk"),
    ("BMRI", "Bank Mandiri (Persero) Tbk"),
    ("BBNI", "Bank Negara Indonesia Tbk"),
    ("TLKM", "Telkom Indonesia Tbk"),
    ("ASII", "Astra International Tbk"),
    ("AMMN", "Amman Mineral Internasional Tbk"),
    ("ADRO", "Adaro Energy Indonesia Tbk"),
    ("PGAS", "Perusahaan Gas Negara Tbk"),
    ("BRIS", "Bank Syariah Indonesia Tbk")
]

def generate_stock_data():
    stocks = []
    for ticker, name in TICKERS:
        price = random.randint(50, 12000)
        change = round(random.uniform(-4.0, 8.0), 2)
        turnover = random.randint(1_000_000_000, 500_000_000_000)
        
        ema20 = int(price * random.uniform(0.95, 1.02))
        ema50 = int(price * random.uniform(0.90, 0.98))
        rsi = random.randint(35, 80)
        vol_ratio = round(random.uniform(0.8, 4.5), 1)
        high52 = int(price * random.uniform(1.01, 1.25))
        
        # Penentuan Bandarmology & Signal
        if rsi >= 60 and vol_ratio >= 2.5:
            bandarmology = "AKUMULASI"
            signal = "STRONG BUY"
        elif rsi >= 50:
            bandarmology = "NEUTRAL"
            signal = "BUY"
        else:
            bandarmology = "DISTRIBUSI"
            signal = "SELL"

        entry = int(price * 0.98)
        r1 = int(price * 1.05)
        cl1 = int(price * 0.94)

        stocks.append({
            "ticker": ticker,
            "name": name,
            "price": price,
            "change": change,
            "turnover": turnover,
            "ema20": ema20,
            "ema50": ema50,
            "rsi": rsi,
            "volRatio": vol_ratio,
            "high52": high52,
            "bandarmology": bandarmology,
            "entry": entry,
            "r1": r1,
            "cl1": cl1,
            "signal": signal
        })

    data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "stocks": stocks
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Data berhasil diperbarui dan disimpan ke data.json")

if __name__ == "__main__":
    generate_stock_data()
