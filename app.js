const DATA_URL = './data.json';
let currentStyle = 'scalping';

async function initScreener() {
  const container = document.getElementById("screenerContainer");
  try {
    const response = await fetch(`${DATA_URL}?t=${new Date().getTime()}`);
    if (!response.ok) throw new Error("Gagal mengambil data JSON.");
    
    const data = await response.json();
    
    renderMarketWarning(data.market_status);
    renderTable(data[currentStyle]);
    setupButtons(data);

  } catch (error) {
    console.error("Error:", error);
    if (container) {
      container.innerHTML = `<p style="color:red; font-weight:bold;">Gagal memuat data. Pastikan file data.json tersedia.</p>`;
    }
  }
}

function renderMarketWarning(status) {
  const warningContainer = document.getElementById("marketWarning");
  if (!warningContainer || !status) return;

  warningContainer.innerHTML = `
    <div style="background-color: #fff3cd; color: #856404; padding: 10px 15px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; border: 1px solid #ffeeba;">
      ${status.warning}
    </div>
  `;
}

function setupButtons(allData) {
  const buttons = document.querySelectorAll('.style-btn');
  buttons.forEach(btn => {
    btn.onclick = (e) => {
      buttons.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      
      currentStyle = e.target.dataset.style;
      renderTable(allData[currentStyle]);
    };
  });
}

// Fungsi Format Tanda Panah & Indikator
function formatInd(ind) {
  if (!ind) return '';
  if (ind.active) {
    return `<div class="ind-active">&#9650; ${ind.name}: <span style="color:#333; font-weight:normal;">${ind.val}</span></div>`;
  } else {
    return `<div class="ind-inactive">&#9644; ${ind.name}: <span>${ind.val}</span></div>`;
  }
}

function renderTable(stockList) {
  const container = document.getElementById("screenerContainer");
  if (!container) return;

  if (!stockList || stockList.length === 0) {
    container.innerHTML = `<p>Tidak ada data saham untuk kategori ini.</p>`;
    return;
  }

  const rows = stockList.map(item => {
    const isLayak = item.status && item.status.includes("LAYAK");
    const bgBadge = isLayak ? '#198754' : '#6c757d';
    const inds = item.indicators || {};

    return `
      <tr>
        <td><strong>${item.ticker}</strong></td>
        <td>Rp${item.price ? item.price.toLocaleString("id-ID") : 0}</td>
        <td><span class="badge" style="background-color:${bgBadge};">${item.status}</span></td>
        
        <!-- Deretan Indikator (Termasuk Indikator Baru + Panah) -->
        <td style="font-size:12px; line-height:1.5;">
          ${formatInd(inds.ema_cross)}
          ${formatInd(inds.rsi)}
          ${formatInd(inds.stoch_rsi)}
          ${formatInd(inds.macd)}
          ${formatInd(inds.vol_sma)}
          ${formatInd(inds.bollinger)}
          ${formatInd(inds.sma50)}
        </td>

        <!-- Entry 3 Level -->
        <td style="font-size:12px;">
          L1: Rp${item.entry_levels[0].toLocaleString("id-ID")}<br>
          L2: Rp${item.entry_levels[1].toLocaleString("id-ID")}<br>
          L3: Rp${item.entry_levels[2].toLocaleString("id-ID")}
        </td>

        <!-- Target TP 3 Level -->
        <td style="color:#198754; font-size:12px;">
          TP1: Rp${item.tp_levels[0].toLocaleString("id-ID")}<br>
          TP2: Rp${item.tp_levels[1].toLocaleString("id-ID")}<br>
          TP3: Rp${item.tp_levels[2].toLocaleString("id-ID")}
        </td>

        <!-- Cut Loss 3 Level -->
        <td style="color:#dc3545; font-size:12px;">
          CL1: Rp${item.cl_levels[0].toLocaleString("id-ID")}<br>
          CL2: Rp${item.cl_levels[1].toLocaleString("id-ID")}<br>
          CL3: Rp${item.cl_levels[2].toLocaleString("id-ID")}
        </td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table border="1">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Harga</th>
          <th>Status</th>
          <th>Indikator (&#9650; Aktif | &#9644; Non-Aktif)</th>
          <th>Titik Entry</th>
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
