const STOCKS_JSON_URL = './data.json';
let cachedStocksData = [];

// 1. Fungsi Peringatan Jam Pasar Bursa Efek Indonesia (BEI)
function checkMarketStatus() {
  const statusContainer = document.getElementById("marketStatusAlert");
  if (!statusContainer) return;

  const now = new Date();
  // Konversi Waktu ke WIB (UTC+7)
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  const wib = new Date(utc + (3600000 * 7));
  
  const day = wib.getDay(); // 0: Mgg, 1: Sen, ..., 5: Jum, 6: Sab
  const hours = wib.getHours();
  const minutes = wib.getMinutes();
  const timeInMinutes = hours * 60 + minutes;

  let statusHtml = "";

  // Hari Akhir Pekan (Sabtu - Minggu)
  if (day === 0 || day === 6) {
    statusHtml = `<div class="alert alert-warning">🔴 PASAR TUTUP (Akhir Pekan). Analisis digunakan untuk persiapan pekan depan.</div>`;
  } else {
    // Jam Kerja Sesi BEI (Sesi 1: 09:00 - 12:00, Sesi 2: 13:30 - 15:50)
    const session1Start = 9 * 60;
    const session1End = 12 * 60;
    const session2Start = 13 * 60 + 30;
    const session2End = 15 * 60 + 50;

    if (timeInMinutes >= session1Start && timeInMinutes < session1End) {
      statusHtml = `<div class="alert alert-success">🟢 PASAR BUKA (Sesi I). Waktu aktif trading.</div>`;
    } else if (timeInMinutes >= session1End && timeInMinutes < session2Start) {
      statusHtml = `<div class="alert alert-info">🟡 ISTIRAHAT PASAR (Sesi I Selesai). Hindari Entry Terburu-buru.</div>`;
    } else if (timeInMinutes >= session2Start && timeInMinutes < session2End) {
      statusHtml = `<div class="alert alert-success">🟢 PASAR BUKA (Sesi II). Persiapan jelang penutupan.</div>`;
    } else {
      statusHtml = `<div class="alert alert-danger">🔴 PASAR TUTUP. Gunakan data untuk analisis post-market.</div>`;
    }
  }

  statusContainer.innerHTML = statusHtml;
}

// 2. Mengambil Data JSON
async function fetchStockNews() {
  const container = document.getElementById("stockListContainer");
  if (!container) return;

  try {
    const response = await fetch(STOCKS_JSON_URL);
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

    const data = await response.json();
    cachedStocksData = data.stocks;
    
    renderStockCards();
  } catch (error) {
    console.error("Gagal memuat data saham:", error);
    container.innerHTML = `<p class="error-msg">Gagal memuat info saham terbaru.</p>`;
  }
}

// 3. Render Tabel Berdasarkan Dropdown Timeframe/Strategi
function renderStockCards() {
  const container = document.getElementById("stockListContainer");
  const strategyFilter = document.getElementById("strategyFilter")?.value || "swing";
  
  if (!cachedStocksData || cachedStocksData.length === 0) {
    container.innerHTML = `<p>Tidak ada data saham yang tersedia.</p>`;
    return;
  }

  // Pemetaan Informasi Indikator yang Dipakai
  const indicatorInfo = {
    scalping: "Indikator Terpasang: EMA 9/21 + RSI 14 (TF 15m)",
    swing: "Indikator Terpasang: EMA 20/50 + MACD + ATR 14 (TF 1D)",
    investasi: "Indikator Terpasang: MA 50/200 + Stoch RSI + Fundamental (TF 1D/1W)"
  };

  const rows = cachedStocksData.map(item => {
    const signal = item.signals[strategyFilter] || "NEUTRAL";
    const signalClass = signal === 'BULLISH' ? 'badge-green' : (signal === 'BEARISH' ? 'badge-red' : 'badge-gray');
    const layakBadge = item.layak_beli ? `<span class="badge-success">YA</span>` : `<span class="badge-dark">TIDAK</span>`;

    return `
      <tr>
        <td><strong>${item.ticker}</strong></td>
        <td>Rp${item.price.toLocaleString("id-ID")}</td>
        <td>
          <small>Pullback: Rp${item.entry_ref.pullback}</small><br>
          <small>Breakout: Rp${item.entry_ref.breakout}</small>
        </td>
        <td><span class="${signalClass}">${signal}</span></td>
        <td>${layakBadge}</td>
        <td>
          <small>TP1: Rp${item.tp[0]}</small><br>
          <small>TP2: Rp${item.tp[1]}</small><br>
          <small>TP3: Rp${item.tp[2]}</small>
        </td>
        <td>
          <small>CL1: Rp${item.cl[0]}</small><br>
          <small>CL2: Rp${item.cl[1]}</small><br>
          <small>CL3: Rp${item.cl[2]}</small>
        </td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <div class="strategy-info-box">${indicatorInfo[strategyFilter]}</div>
    <table class="stock-table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Harga (Close)</th>
          <th>Ref. Entry</th>
          <th>Sinyal Tren</th>
          <th>Layak Beli</th>
          <th>Target Profit (TP)</th>
          <th>Cut Loss (CL)</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

// Inisialisasi Event Listener
document.addEventListener("DOMContentLoaded", () => {
  checkMarketStatus();
  fetchStockNews();

  const filterSelect = document.getElementById("strategyFilter");
  if (filterSelect) {
    filterSelect.addEventListener("change", renderStockCards);
  }
});
