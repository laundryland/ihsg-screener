import json
import os
import tempfile
import time

# Memastikan path penulisan file selalu absolut terhadap folder skrip ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "data.json")


def save_json_atomically(data, target_path):
    """Menulis data ke file sementara (temp) lalu menimpa file utama secara atomic.

    Mencegah berkas data.json korup/terpotong saat di-reload oleh browser.
    """
    target_dir = os.path.dirname(target_path)
    with tempfile.NamedTemporaryFile(
        "w", dir=target_dir, delete=False, encoding="utf-8"
    ) as tf:
        json.dump(data, tf, ensure_ascii=False, separators=(",", ":"))
        temp_file_path = tf.name

    os.replace(temp_file_path, target_path)


def calculate_bandarmology_analysis(
    bandarmology_label, rsi, price, ema20, ema50, vol_ratio
):
    """Mengkalkulasikan analisis Bandarmology gabungan dengan indikator RSI, EMA, dan Volume.

    Mengembalikan Power Score (0 - 100), Status Signal, dan Visual Power Meter.
    """
    score = 50  # Base Score Neutral

    # 1. Bobot Bandarmology
    label_upper = str(bandarmology_label).upper()
    if "ACCUM" in label_upper or "BIG ACC" in label_upper:
        score += 25
    elif "DIST" in label_upper or "BIG DIST" in label_upper:
        score -= 25

    # 2. Bobot RSI (Momentum)
    if 40 <= rsi <= 65:  # Zone bullish sehat
        score += 15
    elif rsi > 70:  # Overbought
        score -= 10
    elif rsi < 30:  # Oversold (peluang reversal)
        score += 5

    # 3. Bobot Tren EMA (EMA20 vs EMA50 & Price)
    if price > ema20 and ema20 > ema50:  # Strong Uptrend
        score += 15
    elif price < ema20 and ema20 < ema50:  # Downtrend
        score -= 15

    # 4. Bobot Rasio Volume
    if vol_ratio >= 1.5:  # Lonjakan volume signifikan
        score += 10
    elif vol_ratio < 0.5:
        score -= 5

    # Clamp score antara 0 hingga 100
    final_score = max(0, min(100, score))

    # Tentukan Sinyal berdasarkan Power Score
    if final_score >= 75:
        signal = "STRONG BUY"
    elif final_score >= 60:
        signal = "BUY"
    elif final_score <= 35:
        signal = "SELL"
    else:
        signal = "NEUTRAL"

    # Indikator visual 10-box power meter
    filled_boxes = round(final_score / 10)
    power_meter = "█" * filled_boxes + "░" * (10 - filled_boxes)

    return {
        "score": final_score,
        "signal": signal,
        "powerMeter": power_meter,
    }


def clean_and_enrich_stock(raw_stock):
    """Menghapus kolom yang tidak terpakai, menghitung indikator teknikal gabungan,

    dan memvalidasi kelayakan data emiten.
    """
    # Hapus kolom yang tidak terpakai
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
    price = cleaned.get("price", 0)

    # Filter data tidak valid
    if not ticker or price <= 0:
        return None

    # Ekstrak nilai indikator
    bandarmology = cleaned.get("bandarmology", "NEUTRAL")
    rsi = cleaned.get("rsi", 50.0)
    ema20 = cleaned.get("ema20", price)
    ema50 = cleaned.get("ema50", price)
    vol_ratio = cleaned.get("volRatio", 1.0)

    # Kalkulasi gabungan Bandarmology & indikator
    analysis = calculate_bandarmology_analysis(
        bandarmology, rsi, price, ema20, ema50, vol_ratio
    )

    # Tambahkan hasil kalkulasi ke dictionary emiten
    cleaned["powerScore"] = analysis["score"]
    cleaned["signal"] = analysis["signal"]
    cleaned["powerMeter"] = analysis["powerMeter"]

    return cleaned


def get_expanded_stock_list():
    """Mengembalikan daftar emiten yang diperluas mencakup BNBR, JGLE,

    serta deretan emiten top gainers & paling aktif di IDX.
    """
    # Masukkan seluruh list emiten kamu atau panggil fungsi scraper/fetcher aktual di sini
    return [
        # Emiten Tambahan Baru & Top Gainers/Active IDX
        {
            "ticker": "BNBR",
            "name": "Bakrie & Brothers Tbk.",
            "price": 62,
            "change": 8.77,
            "rsi": 68.2,
            "ema20": 55.4,
            "ema50": 52.1,
            "volRatio": 2.45,
            "high52": 98,
            "bandarmology": "BIG ACCUM",
            "entry": 62,
            "r1": 68,
            "cl1": 58,
        },
        {
            "ticker": "JGLE",
            "name": "Graha Andrasentra Propertindo Tbk",
            "price": 50,
            "change": 0.0,
            "rsi": 45.0,
            "ema20": 50.0,
            "ema50": 50.0,
            "volRatio": 0.8,
            "high52": 54,
            "bandarmology": "NEUTRAL",
            "entry": 50,
            "r1": 52,
            "cl1": 47,
        },
        {
            "ticker": "BUMI",
            "name": "Bumi Resources Tbk",
            "price": 222,
            "change": -1.77,
            "rsi": 72.2,
            "ema20": 199.6,
            "ema50": 186.1,
            "volRatio": 1.85,
            "high52": 484,
            "bandarmology": "ACCUM",
            "entry": 222,
            "r1": 233,
            "cl1": 210,
        },
        {
            "ticker": "BRMS",
            "name": "Bumi Resources Minerals Tbk.",
            "price": 695,
            "change": 4.11,
            "rsi": 64.0,
            "ema20": 690.8,
            "ema50": 652.6,
            "volRatio": 2.15,
            "high52": 1385,
            "bandarmology": "BIG ACCUM",
            "entry": 695,
            "r1": 729,
            "cl1": 660,
        },
        {
            "ticker": "DOOH",
            "name": "Era Media Sejahtera Tbk.",
            "price": 358,
            "change": 9.82,
            "rsi": 85.0,
            "ema20": 313.5,
            "ema50": 261.0,
            "volRatio": 3.20,
            "high52": 360,
            "bandarmology": "ACCUM",
            "entry": 358,
            "r1": 375,
            "cl1": 340,
        },
        {
            "ticker": "BBCA",
            "name": "Bank Central Asia Tbk",
            "price": 6525,
            "change": -2.25,
            "rsi": 61.9,
            "ema20": 6501.0,
            "ema50": 6359.1,
            "volRatio": 1.11,
            "high52": 8295,
            "bandarmology": "NEUTRAL",
            "entry": 6525,
            "r1": 6851,
            "cl1": 6198,
        },
        {
            "ticker": "BBRI",
            "name": "Bank Rakyat Indonesia (Persero)",
            "price": 3390,
            "change": -0.59,
            "rsi": 71.9,
            "ema20": 3256.9,
            "ema50": 3132.5,
            "volRatio": 0.42,
            "high52": 3865,
            "bandarmology": "DISTRIBUTION",
            "entry": 3390,
            "r1": 3559,
            "cl1": 3220,
        },
        {
            "ticker": "ADRO",
            "name": "Alamtri Resources Indonesia Tbk",
            "price": 2660,
            "change": -1.12,
            "rsi": 56.6,
            "ema20": 2645.2,
            "ema50": 2547.8,
            "volRatio": 0.63,
            "high52": 2860,
            "bandarmology": "NEUTRAL",
            "entry": 2660,
            "r1": 2793,
            "cl1": 2527,
        },
        {
            "ticker": "ANTM",
            "name": "ANTAM (Persero) Tbk.",
            "price": 3140,
            "change": 1.95,
            "rsi": 50.0,
            "ema20": 3098.0,
            "ema50": 3054.0,
            "volRatio": 0.97,
            "high52": 4631,
            "bandarmology": "ACCUM",
            "entry": 3140,
            "r1": 3297,
            "cl1": 2983,
        },
    ]


def run_screener():
    print("Memulai proses kalkulasi & pembaharuan screener...")

    raw_stocks = get_expanded_stock_list()
    processed_stocks = []
    seen_tickers = set()

    for item in raw_stocks:
        enriched_item = clean_and_enrich_stock(item)

        if enriched_item:
            ticker = enriched_item["ticker"]

            # Mencegah duplikasi data emiten
            if ticker not in seen_tickers:
                seen_tickers.add(ticker)
                processed_stocks.append(enriched_item)

    # Urutkan berdasarkan Power Score tertinggi (Top Screener)
    processed_stocks.sort(key=lambda x: x.get("powerScore", 0), reverse=True)

    output_payload = {
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00"),
        "totalStocks": len(processed_stocks),
        "stocks": processed_stocks,
    }

    if processed_stocks:
        save_json_atomically(output_payload, OUTPUT_FILE)
        print(
            f"Selesai! {len(processed_stocks)} emiten berhasil dihitung dan disimpan secara compact."
        )


if __name__ == "__main__":
    run_screener()
