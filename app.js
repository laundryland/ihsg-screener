const DATA_URL = './data.json';
let currentStyle = 'scalping';

async function initScreener() {
  try {
    const response = await fetch(`${DATA_URL}?t=${new Date().getTime()}`);
    if (!response.ok) throw new Error("Gagal mengambil data JSON.");
    
    const data = await response.json();
    
    renderMarketWarning(data.market_status);
    renderTable(data[currentStyle]);
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
    <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; border: 1px solid #ffeeba;">
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

function formatIndicatorBadge(ind) {
  if (ind.active) {
    return `<span style="color:#28a745; font-weight:bold;">🟢 ⬆️ ${ind.val}</span>`;
  } else {
    return `<span style="color:#a0a0a0; font-weight:normal;">⚪ ➖ ${ind.val}</span>`;
  }
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
    const inds = item.indicators;

    return `
      <tr>
        <td><strong>${item.ticker}</strong></td>
        <td>Rp${item.price.toLocaleString("id-ID")}</td>
        <td><span style="background-color:${statusColor}; color:white; padding:4px 8px; border-radius:4px; font-size:12px;">${item.status}</span></td>
        
        <!-- Kolom Indikator Terpakai & Pertimbangan -->
        <td style="font-size:12px; line-height:1.6;">
          ${formatIndicatorBadge(inds.ema_cross)}<br>
          ${formatIndicatorBadge(inds.rsi)}<br>
          ${formatIndicatorBadge(inds.macd)}<br>
          ${formatIndicatorBadge(inds.vol_sma)}<br>
          ${formatIndicatorBadge(inds.sma50)}
        </td>

        <!-- Kolom Entry 3 Level -->
        <td style="font-size:12px;">
          L1: Rp${item.entry_levels[0].toLocaleString("id-ID")}<br>
          L2: Rp${item.entry_levels[1].toLocaleString("id-ID")}<br>
          L3: Rp${item.entry_levels[2].toLocaleString("id-ID")}
        </td>

        <!-- Kolom TP 3 Level -->
        <td style="color:#28a745; font-size:12px;">
          TP1: Rp${item.tp_levels[0].toLocaleString("id-ID")}<br>
          TP2: Rp${item.tp_levels[1].toLocaleString("id-ID")}<br>
          TP3: Rp${item.tp_levels[2].toLocaleString("id-ID")}
        </td>

        <!-- Kolom Cut Loss 3 Level -->
        <td style="color:#dc3545; font-size:12px;">
          CL1: Rp${item.cl_levels[0].toLocaleString("id-ID")}<br>
          CL2: Rp${item.cl_levels[1].toLocaleString("id-ID")}<br>
          CL3: Rp${item.cl_levels[2].toLocaleString("id-ID")}
        </td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table border="1" cellpadding="8" cellspacing="0" style="width:100%; border-collapse:collapse; text-align:left;">
      <thead>
        <tr style="background-color:#f8f9fa; font-size:13px;">
          <th>Ticker</th>
          <th>Harga</th>
          <th>Status</th>
          <th>Status Indikator (🟢 Terpakai | ⚪ Tidak/N/A)</th>
          <th>Entry Points</th>
          <th>Target TP</th>
          <th>Cut Loss</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

document.addEventListener("DOMContentLoaded", initScreener);
