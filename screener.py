import json
import os
import tempfile
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "data.json")


def save_json_atomically(data, target_path):
    target_dir = os.path.dirname(target_path)
    with tempfile.NamedTemporaryFile(
        "w", dir=target_dir, delete=False, encoding="utf-8"
    ) as tf:
        json.dump(data, tf, indent=2, ensure_ascii=False)
        temp_file_path = tf.name
    os.replace(temp_file_path, target_path)


def calculate_bandarmology_score(item):
    """Menghitung skor gabungan (0 - 100%) berdasarkan Bandarmologi + RSI + EMA + Volume."""
    score = 50  # Base Neutral

    bandar = str(item.get("bandarmology", "NEUTRAL")).upper()
    rsi = float(item.get("rsi", 50))
    price = float(item.get("price", 0))
    ema20 = float(item.get("ema20", 0))
    vol_ratio = float(item.get("volRatio", 1.0))

    # 1. Bobot Bandarmologi (+/- 25)
    if "BIG ACCUM" in bandar or "STRONG BUY" in bandar:
        score += 25
    elif "ACCUM" in bandar or "BUY" in bandar:
        score += 15
    elif "BIG DIST" in bandar or "STRONG SELL" in bandar:
        score -= 25
    elif "DIST" in bandar or "SELL" in bandar:
        score -= 15

    # 2. Bobot RSI (+/- 15)
    if 50 <= rsi <= 65:
        score += 15  # Momentum Bullish sehat
    elif rsi > 70:
        score += 5  # Overbought
    elif 35 <= rsi < 50:
        score -= 10
    elif rsi < 30:
        score -= 15  # Oversold / Downtrend kuat

    # 3. Bobot Tren EMA20 (+/- 10)
    if price > ema20 and ema20 > 0:
        score += 10
    elif price < ema20 and ema20 > 0:
        score -= 10

    # 4. Bobot Konfirmasi Volume (+/- 10)
    if vol_ratio >= 1.5:
        score += 10
    elif vol_ratio < 0.5:
        score -= 5

    # Batasi skor pada rentang 0 - 100
    score = max(0, min(100, score))

    # Penentuan Label Signal & Power %
    if score >= 80:
        signal = "STRONG BUY"
    elif score >= 60:
        signal = "BUY"
    elif score <= 20:
        signal = "STRONG SELL"
    elif score <= 40:
        signal = "SELL"
    else:
        signal = "NEUTRAL"

    return score, signal


def clean_and_process_stock(raw_stock):
    unused_keys = [
        "bluechip",
        "top_gainer",
        "topgainer",
        "high_volatility",
        "highvolatility",
        "volatility",
    ]

    cleaned = dict(raw_stock)
    for key in unused_keys:
        cleaned.pop(key, None)

    ticker = cleaned.get("ticker")
    price = float(cleaned.get("price", 0))

    if not ticker or price <= 0:
        return None

    # Kalkulasi gabungan Bandarmologi + Teknikal
    power_score, signal = calculate_bandarmology_score(cleaned)
    cleaned["powerScore"] = power_score  # Nilai 0 - 100%
    cleaned["signal"] = signal

    return cleaned


def fetch_all_stocks():
    """Daftar emiten IDX termasuk penambahan BNBR, JGLE, dan Top Gainers."""
    # Tempatkan penarikan data/scraping aktual kamu di sini.
    # Sampel data untuk memastikan emiten awal dan baru hadir lengkap:
    return [
        {
            "ticker": "BNBR",
            "name": "Bakrie & Brothers Tbk",
            "price": 65,
            "change": 8.33,
            "rsi": 62.0,
            "ema20": 58.0,
            "volRatio": 2.1,
            "bandarmology": "BIG ACCUM",
        },
        {
            "ticker": "JGLE",
            "name": "Graha Andrasentra Propertindo Tbk",
            "price": 50,
            "change": 4.0,
            "rsi": 55.0,
            "ema20": 50.0,
            "volRatio": 1.8,
            "bandarmology": "ACCUM",
        },
        {
            "ticker": "BBCA",
            "name": "Bank Central Asia Tbk",
            "price": 6525,
            "change": -2.25,
            "rsi": 61.9,
            "ema20": 6501.0,
            "volRatio": 1.11,
            "bandarmology": "NEUTRAL",
        },
        {
            "ticker": "BBRI",
            "name": "Bank Rakyat Indonesia Tbk",
            "price": 3390,
            "change": -0.59,
            "rsi": 71.9,
            "ema20": 3256.9,
            "volRatio": 0.42,
            "bandarmology": "BUY",
        },
        {
            "ticker": "GOTO",
            "name": "GoTo Gojek Tokopedia Tbk",
            "price": 54,
            "change": 8.0,
            "rsi": 68.0,
            "ema20": 51.0,
            "volRatio": 3.2,
            "bandarmology": "BIG ACCUM",
        },
        {
            "ticker": "DOOH",
            "name": "Era Media Sejahtera Tbk",
            "price": 358,
            "change": 9.82,
            "rsi": 85.0,
            "ema20": 313.5,
            "volRatio": 2.5,
            "bandarmology": "BIG ACCUM",
        },
        {
            "ticker": "LEAD",
            "name": "Logindo Samudramakmur Tbk",
            "price": 117,
            "change": 8.33,
            "rsi": 55.2,
            "ema20": 109.9,
            "volRatio": 3.72,
            "bandarmology": "BUY",
        },
        {
            "ticker": "BUMI",
            "name": "Bumi Resources Tbk",
            "price": 222,
            "change": -1.77,
            "rsi": 72.2,
            "ema20": 199.6,
            "volRatio": 1.3,
            "bandarmology": "NEUTRAL",
        },
    ]


def run_screener():
    print("Memulai proses screener...")
    raw_stocks = fetch_all_stocks()

    if not raw_stocks:
        print("Data mentah kosong.")
        return

    valid_stocks = []
    seen_tickers = set()

    for item in raw_stocks:
        cleaned_item = clean_and_process_stock(item)
        if cleaned_item:
            ticker = cleaned_item["ticker"]
            if ticker not in seen_tickers:
                seen_tickers.add(ticker)
                valid_stocks.append(cleaned_item)

    output_data = {
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00"),
        "stocks": valid_stocks,
    }

    if valid_stocks:
        save_json_atomically(output_data, OUTPUT_FILE)
        print(
            f"Sukses! {len(valid_stocks)} emiten berhasil diproses dan disimpan."
        )


if __name__ == "__main__":
    run_screener()
