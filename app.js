// Path ke file JSON lokal di repositori GitHub kamu
const IPO_JSON_URL = './ipo.json'; 

// Fungsi untuk mengambil data dari ipo.json
async function fetchIPONews() {
  const tickerContainer = document.getElementById("ipoTickerContainer");
  if (!tickerContainer) return;

  try {
    // Beri timestamp pada URL query agar browser tidak membaca dari cache lama
    const response = await fetch(`${IPO_JSON_URL}?t=${new Date().getTime()}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const ipoList = await response.json();
    renderIPOTicker(ipoList);
  } catch (error) {
    console.error("Gagal memuat data IPO:", error);
    tickerContainer.innerHTML = `<span class="text-error">Gagal memuat info IPO terbaru.</span>`;
  }
}

// Fungsi untuk me-render data IPO menjadi Running Text (Marquee)
function renderIPOTicker(ipoList) {
  const tickerContainer = document.getElementById("ipoTickerContainer");
  
  if (!ipoList || ipoList.length === 0) {
    tickerContainer.innerHTML = `<span>Tidak ada emiten IPO dalam waktu dekat.</span>`;
    return;
  }

  // Format penggabungan item IPO dengan pemisah '|'
  const tickerItems = ipoList.map(item => {
    return `🔥 <strong>${item.nama} (${item.ticker})</strong> — Tgl IPO: ${item.tgl_ipo} <span class="badge">[${item.status}]</span>`;
  }).join("&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;");

  // Masukkan ke dalam container animasi
  tickerContainer.innerHTML = `<div class="ipo-ticker-text">${tickerItems}</div>`;
}

// Panggil fungsi saat halaman dimuat
document.addEventListener("DOMContentLoaded", () => {
  fetchIPONews();
});
