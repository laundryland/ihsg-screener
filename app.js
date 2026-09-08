const DATA_URL = './data.json';
let currentStyle = 'scalping'; // Default mode

async function initScreener() {
  try {
    const response = await fetch(`${DATA_URL}?t=${new Date().getTime()}`);
    if (!response.ok) throw new Error("Gagal mengambil data JSON.");
    
    const data = await response.json();
    
    // 1. Render Peringatan Waktu Pasar
    renderMarketWarning(data.market_status);
    
    // 2. Render Tabel Saham Pertama Kali
    renderTable(data[currentStyle]);

    // 3. Pasang Event Listener Tombol Gaya Trading
    setupFilterButtons(data);

  } catch (error) {
    console.error("Error:", error);
    document.getElementById("screenerContainer").innerHTML = `<p style="color:red;">Gagal memuat data screener.</p>`;
  }
}

function renderMarketWarning(status) {
  const warningContainer = document.getElementById("marketWarning");
  if (!warningContainer) return;

  warningContainer.innerHTML = `
    <div style="background-color: #fff3cd; color: #856404; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; border: 1px solid #ffeeba;">
      ${status.warning}
    </div>
  `;
}

function setupFilterButtons(allData) {
  const buttons = document.querySelectorAll('.style-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      buttons.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      
      currentStyle = e.target.dataset.style;
      renderTable(allData[currentStyle]);
    });
  });
}

function renderTable(stockList) {
  const container = document.getElementById("screenerContainer");
  if (!stockList || stockList.length === 0) {
    container.innerHTML = `<p>Tidak ada data saham untuk kategori ini.</p>`;
    return;
  }

  const rows = stockList.map(item => {
    const isLayak = item.status.includes("LAYAK");
    const statusColor = isLayak ? '#28a745' : '#6c757d';

    return `
      <tr>
        <td><strong>${item.ticker}</strong></td>
        <td>Rp${item.price.toLocaleString("id-ID")}</td>
        <td><span style="background-color:${statusColor}; color:white; padding:4px 8px; border-radius:4px; font-size:12px;">${item.status}</span></td>
        <!-- Kolom Titik Entry 3 Level -->
        <td>
          <small>L1: Rp${item.entry_levels[0].toLocaleString("id-ID")}</small><br>
          <small>L2: Rp${item.entry_levels[1].toLocaleString("id-ID")}</small><br>
          <small>L3: Rp${item.entry_levels[2].toLocaleString("id-ID")}</small>
        </td>
        <!-- Kolom Take Profit 3 Level -->
        <td style="color:#28a745;">
          <small>TP1: Rp${item.tp_levels[0].toLocaleString("id-ID")}</small><br>
          <small>TP2: Rp${item.tp_levels[1].toLocaleString("id-ID")}</small><br>
          <small>TP3: Rp${item.tp_levels[2].toLocaleString("id-ID")}</small>
        </td>
        <!-- Kolom Cut Loss 3 Level -->
        <td style="color:#dc3545;">
          <small>CL1: Rp${item.cl_levels[0].toLocaleString("id-ID")}</small><br>
          <small>CL2: Rp${item.cl_levels[1].toLocaleString("id-ID")}</small><br>
          <small>CL3: Rp${item.cl_levels[2].toLocaleString("id-ID")}</small>
        </td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table border="1" cellpadding="8" cellspacing="0" style="width:100%; border-collapse:collapse; font-size:14px; text-align:left;">
      <thead>
        <tr style="background-color:#f8f9fa;">
          <th>Ticker</th>
          <th>Harga Terakhir</th>
          <th>Status Screener</th>
          <th>Titik Entry (3 Level)</th>
          <th>Target TP (3 Level)</th>
          <th>Stop Loss / CL (3 Level)</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

document.addEventListener("DOMContentLoaded", initScreener);
