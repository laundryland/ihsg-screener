import json
import os
import tempfile
import time

# Mengunci path agar selalu menyimpan di folder yang sama dengan skrip ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "data.json")


def save_json_atomically(data, target_path):
    """Menulis data ke file sementara lebih dulu, lalu menimpa file utama secara instan (atomic)

    agar file tidak korup/terpotong di browser saat di-reload.
    """
    target_dir = os.path.dirname(target_path)

    # 1. Tulis ke file sementara
    with tempfile.NamedTemporaryFile(
        "w", dir=target_dir, delete=False, encoding="utf-8"
    ) as tf:
        json.dump(data, tf, indent=2, ensure_ascii=False)
        temp_file_path = tf.name

    # 2. Ganti file utama secara instan setelah penulisan 100% selesai
    os.replace(temp_file_path, target_path)


def clean_stock_data(raw_stock):
    """Membersihkan kolom yang tidak terpakai dan memvalidasi data emiten."""
    # Kolom yang akan dihapus sesuai permintaan
    unused_keys = [
        "bluechip",
        "top_gainer",
        "topgainer",
        "high_volatility",
        "highvolatility",
        "volatility",
    ]

    cleaned = dict(raw_stock)

    # Hapus kolom yang tidak terpakai
    for key in unused_keys:
        cleaned.pop(key, None)

    ticker = cleaned.get("ticker")
    price = cleaned.get("price", 0)

    # Validasi: Emiten harus punya ticker dan harga yang valid (> 0)
    if not ticker or price <= 0:
        return None

    return cleaned


def fetch_all_stocks():
    """Ganti isi fungsi ini dengan logika penarikan/scraping data saham kamu yang asli."""
    # CONTOH: Jika kamu membaca dari file asal, masukan pustaka/pemanggilan kamu di sini.
    # Return harus berupa list of dictionary data saham mentah.
    return []


def run_screener():
    print("Memulai proses screener...")

    # 1. Ambil seluruh data mentah
    raw_stocks = fetch_all_stocks()

    if not raw_stocks:
        print(
            "Peringatan: Data mentah kosong! Pastikan fungsi penarik data sudah terhubung."
        )
        return

    valid_stocks = []
    seen_tickers = set()

    # 2. Iterasi seluruh emiten dari awal hingga akhir
    for item in raw_stocks:
        cleaned_item = clean_stock_data(item)

        if cleaned_item:
            ticker = cleaned_item["ticker"]

            # Mencegah duplikasi ticker agar data awal tidak tertimpa data kosong di belakang
            if ticker not in seen_tickers:
                seen_tickers.add(ticker)
                valid_stocks.append(cleaned_item)

    # 3. Susun payload JSON akhir
    output_data = {
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00"),
        "stocks": valid_stocks,
    }

    # 4. Simpan ke file jika ada data valid
    if valid_stocks:
        save_json_atomically(output_data, OUTPUT_FILE)
        print(
            f"Sukses! {len(valid_stocks)} emiten berhasil diproses dan disimpan ke {OUTPUT_FILE}"
        )
    else:
        print("Gagal: Tidak ada emiten valid yang berhasil diolah.")


if __name__ == "__main__":
    run_screener()
