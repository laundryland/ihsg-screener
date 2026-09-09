import json
import os
import tempfile
import time

# Memastikan lokasi file tersimpan di folder yang sama dengan skrip
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "data.json")


def save_json_atomically(data, target_path):
    """Menulis ke file sementara dulu agar data.json tidak korup saat reload."""
    target_dir = os.path.dirname(target_path)
    with tempfile.NamedTemporaryFile(
        "w", dir=target_dir, delete=False, encoding="utf-8"
    ) as tf:
        json.dump(data, tf, indent=2, ensure_ascii=False)
        temp_file_path = tf.name
    os.replace(temp_file_path, target_path)


def calculate_bandarmology_score(item):
    """Menghitung skor kombinasi Bandarmologi + Indikator Teknikal (0 - 100%)."""
    score = 50  # Baseline Netral

    bandar = str(item.get("bandarmology", "NEUTRAL")).upper()

    # Konversi harga dan indikator secara aman agar angka tidak kacau/NaN
    try:
        rsi = float(item.get("rsi", 50))
    except (ValueError, TypeError):
        rsi = 50.0

    try:
        price = float(item.get("price", 0))
    except (ValueError, TypeError):
        price = 0.0

    try:
        ema20 = float(item.get("ema20", 0))
    except (ValueError, TypeError):
        ema20 = 0.0

    try:
        vol_ratio = float(item.get("volRatio", 1.0))
    except (ValueError, TypeError):
        vol_ratio = 1.0

    # 1. Analisis Bandarmologi (+/- 25)
    if "BIG ACCUM" in bandar or "STRONG BUY" in bandar:
        score += 25
    elif "ACCUM" in bandar or "BUY" in bandar:
        score += 15
    elif "BIG DIST" in bandar or "STRONG SELL" in bandar:
        score -= 25
    elif "DIST" in bandar or "SELL" in bandar:
        score -= 15

    # 2. Analisis RSI (+/- 15)
    if 50 <= rsi <= 65:
        score += 15
    elif rsi > 70:
        score += 5
    elif 35 <= rsi < 50:
        score -= 10
    elif rsi < 30:
        score -= 15

    # 3. Analisis Trend EMA (+/- 10)
    if price > ema20 and ema20 > 0:
        score += 10
    elif price < ema20 and ema20 > 0:
        score -= 10

    # 4. Volume Ratio (+/- 10)
    if vol_ratio >= 1.5:
        score += 10
    elif vol_ratio < 0.5:
        score -= 5

    # Batasi rentang skor 0 - 100
    score = max(0, min(100, score))

    # Penentuan Signal
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
    """Menghapus kolom tak terpakai dan mempertahankan seluruh data harga asli."""
    # Hapus hanya kolom yang diminta
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

    # Pastikan ticker valid
    if not ticker:
        return None

    # Kalkulasi skor dan sinyal
    power_score, signal = calculate_bandarmology_score(cleaned)
    cleaned["powerScore"] = power_score
    cleaned["signal"] = signal

    return cleaned


def fetch_all_stocks():
    """GANTI BAGIAN INI DENGAN LOGIKA SCRAPING / DATA ASLI KAMU.

    Pastikan fungsi ini mengembalikan daftar seluruh emiten (termasuk BNBR,
    JGLE, dll).
    """
    # JIKA KAMU MEMBACA DARI FILE JSON ASLI/LAIN, UNCOMMENT & SESUAIKAN BARIS DI BAWAH:
    # if os.path.exists("raw_data.json"):
    #     with open("raw_data.json", "r") as f:
    #         return json.load(f)

    return []  # Selalu hubungkan dengan return data asli kamu di sini


def run_screener():
    print("Memulai pemrosesan screener...")
    raw_stocks = fetch_all_stocks()

    if not raw_stocks:
        print(
            "Peringatan: Data mentah kosong. Sambungkan fungsi `fetch_all_stocks()` dengan sumber data utama kamu."
        )
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
            f"Sukses! {len(valid_stocks)} emiten berhasil diproses tanpa ada yang hilang."
        )


if __name__ == "__main__":
    run_screener()
