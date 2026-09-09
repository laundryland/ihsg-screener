import json
import random
from datetime import datetime

# Daftar acuan harga wajar (Baseline Price) untuk mencegah harga melambung
BASE_STOCKS = [
    {"ticker": "BBCA", "name": "Bank Central Asia Tbk", "base_price": 10250},
    {"ticker": "BBRI", "name": "Bank Rakyat Indonesia Tbk", "base_price": 5150},
    {"ticker": "BMRI", "name": "Bank Mandiri (Persero) Tbk", "base_price": 7150},
    {"ticker": "BBNI", "name": "Bank Negara Indonesia Tbk", "base_price": 5450},
    {"ticker": "TLKM", "name": "Telkom Indonesia Tbk", "base_price": 3820},
    {"ticker": "ASII", "name": "Astra International Tbk", "base_price": 5200},
    {"ticker": "AMMN", "name": "Amman Mineral Internasional Tbk", "base_price": 11800},
    {"ticker": "ADRO", "name": "Adaro Energy Indonesia Tbk", "base_price": 3650},
    {"ticker": "PGAS", "name": "Perusahaan Gas Negara Tbk", "base_price": 1540},
    {"ticker": "BRIS", "name": "Bank Syariah Indonesia Tbk", "base_price": 2950}
]

def generate_stock_data():
    unique_stocks = {}
    
    for item in BASE_STOCKS:
        ticker = item["ticker"]
        # Skip jika ticker duplikat
        if ticker in unique_stocks:
            continue
            
        base = item["base_price"]
        # Variasi harga wajar maksimal ±3% dari harga acuan
        price = int(base * random.uniform(0.97, 1.03))
        change = round(random.uniform(-3.5, 4.5), 2)
        turnover = random.randint(5_000_000_000, 350_000_000_000)
        
        ema20 = int(price * random.uniform(0.97, 1.01))
        ema50 = int(price * random.uniform(0.93, 0.98))
        rsi = random.randint(40, 75)
        vol_ratio = round(random.uniform(1.0, 3.5), 1)
        high52 = int(price * random.uniform(1.01, 1.10))
        
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

        entry = int(price * 0.99)
        r1 = int(price * 1.04)
        cl1 = int(price * 0.95)

        unique_stocks[ticker] = {
            "ticker": ticker,
            "name": item["name"],
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
        }

    data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "stocks": list(unique_stocks.values())
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Data {len(data['stocks'])} emiten berhasil diperbarui tanpa duplikat.")

if __name__ == "__main__":
    generate_stock_data()
