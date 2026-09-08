// Path dihubungkan kembali ke data.json
const STOCKS_JSON_URL = './data.json'; 

// Fungsi mengambil data saham secara efisien
async function fetchStockNews() {
  const tickerContainer = document.getElementById("ipoTickerContainer");
  if (!tickerContainer) return;

  try {
    // Menggunakan fetch standar agar ringan
    const response = await fetch(STOCKS_JSON_URL);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    
    // Langsung merender data saham
    renderStockTicker(data.stocks);
  } catch (error) {
    console.error("Gagal memuat data saham:", error);
    tickerContainer.innerHTML = `<span>Gagal memuat info saham.</span>`;
  }
}

// Fungsi merender running text
function renderStockTicker(stockList) {
  const tickerContainer = document.getElementById("ipoTickerContainer");
  
  if (!stockList || stockList.length === 0) {
    tickerContainer.innerHTML = `<span>Data saham tidak tersedia.</span>`;
    return;
  }

  // Menggunakan properti ticker, price, dan signal dari data.json
  const tickerItems = stockList.map(item => {
    return `<strong>${item.ticker}</strong>: Rp${item.price.toLocaleString("id-ID")} [${item.signal}]`;
  }).join("&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;");

  tickerContainer.innerHTML = `<div class="ipo-ticker-text">${tickerItems}</div>`;
}

// Jalankan ketika dokumen siap
document.addEventListener("DOMContentLoaded", fetchStockNews);
