const STOCKS_JSON_URL = './data.json'; 

async function fetchStockNews() {
  const container = document.getElementById("stockListContainer");
  if (!container) return;

  try {
    const response = await fetch(STOCKS_JSON_URL);
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

    const data = await response.json();
    renderStockCards(data.stocks);
  } catch (error) {
    console.error("Gagal memuat data saham:", error);
    container.innerHTML = `<p class="error-msg">Gagal memuat info saham terbaru.</p>`;
  }
}

function renderStockCards(stockList) {
  const container = document.getElementById("stockListContainer");
  
  if (!stockList || stockList.length === 0) {
    container.innerHTML = `<p>Tidak ada data saham.</p>`;
    return;
  }

  // Render menggunakan tabel ringkas agar ringan di browser
  const rows = stockList.map(item => {
    const signalClass = item.signal === 'BULLISH' ? 'text-green' : (item.signal === 'BEARISH' ? 'text-red' : 'text-gray');
    
    return `
      <tr>
        <td><strong>${item.ticker}</strong></td>
        <td>Rp${item.price.toLocaleString("id-ID")}</td>
        <td>Rp${item.open.toLocaleString("id-ID")}</td>
        <td>Rp${item.high.toLocaleString("id-ID")}</td>
        <td>Rp${item.low.toLocaleString("id-ID")}</td>
        <td class="${signalClass}"><strong>${item.signal}</strong></td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table class="stock-table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Price (Close)</th>
          <th>Open</th>
          <th>High</th>
          <th>Low</th>
          <th>Signal</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

document.addEventListener("DOMContentLoaded", fetchStockNews);
