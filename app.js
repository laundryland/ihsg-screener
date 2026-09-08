const DATA_URL = './data.json';
let currentStyle = 'scalping';
let globalData = null;

async function initScreener() {
  const container = document.getElementById("screenerContainer");
  try {
    const response = await fetch(`${DATA_URL}?t=${new Date().getTime()}`);
    if (!response.ok) throw new Error("Gagal mengambil data JSON.");
    
    globalData = await response.json();
    
    renderMarketWarning(globalData.market_status);
    renderTable(globalData[currentStyle]);
    setupFilterButtons();

  } catch (error) {
    console.error("Error:", error);
    container.innerHTML = `<p style="color:red; font-weight:bold;">Gagal memuat data screener.</p>`;
  }
}

function renderMarketWarning(status) {
  const warningContainer = document.getElementById("marketWarning");
  if (!warningContainer || !status) return;

  warningContainer.innerHTML = `
    <div style="background-color: #fff3cd; color: #856404; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-weight: bold; border: 1px solid #ffeeba;">
      ${status.warning}
    </div>
  `;
}

function setupFilterButtons() {
  const buttons = document.querySelectorAll('.style-btn');
  buttons.forEach(btn => {
    btn.onclick = (e) => {
      buttons.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      
      currentStyle = e.target.dataset.style;
      if (globalData) {
        renderTable(globalData[currentStyle]);
      }
    };
  });
}

// Render Panah Hijau atau Abu-Abu secara Presisi
function formatIndicatorItem(ind) {
  if (ind.active) {
    return `<div style="color:#198754; font-weight:bold; margin-bottom:2px;">
              <span style="display:inline-block; width:12px; color:#198754;">&#x25B2;</span> 
              ${ind.name}: <span style="color:#212529; font-weight:normal;">${ind.val}</span>
            </div>`;
  } else {
    return `<div style="color:#adb5bd; margin-bottom:2px;">
              <span style="display:inline-block; width:12px; color:#adb5bd;">&#x25AC;</span> 
              ${ind.name}: <span style="color:#6c757d;">${ind.val}</span>
            </div>`;
  }
}

function renderTable(stockList) {
  const container = document.getElementById("screenerContainer");
  if (!stockList || stockList.length === 0) {
    container.innerHTML = `<p>Tidak ada data saham untuk strategi ini.</p>`;
    return;
  }

  const rows = stockList.map(item => {
    const isLayak = item.status.includes("LAYAK");
    const statusBg = isLayak ? '#198754' : '#6c757d';
    const inds = item.indicators;

    // Kumpulan semua indikator
    const indicatorListHTML = Object.keys(inds).map(key => formatIndicatorItem(inds[key])).join('');

    return `
      <tr>
        <td><strong style="font-size:15px;">${item.ticker}</strong></td>
        <td><strong>Rp${item.price.toLocaleString("id-ID")}</strong></td>
        <td><span class="badge-status" style="background-color:${statusBg};">${item.status}</span></td>
        
        <!-- Kolom Seluruh Indikator dengan Tanda Panah -->
        <td style="font-size:12px; line-height:1.4;">
          ${indicatorListHTML}
        </td>

        <!-- Kolom Entry 3 Level -->
        <td style="font-size:12px; background:#f8f9fa;">
          L1: <strong>Rp${item.entry_levels[0].toLocaleString("id-ID")}</strong><br>
          L2: Rp${item.entry_levels[1].toLocaleString("id-ID")}<br>
          L3: Rp${item.entry_levels[2].toLocaleString("id-ID")}
        </td>

        <!-- Kolom Target TP 3 Level -->
        <td style="color:#198754; font-size:12px;">
          TP1: <strong>Rp${item.tp_levels[0].toLocaleString("id-ID")}</strong><br>
          TP2: Rp${item.tp_levels[1].toLocaleString("id-ID")}<br>
          TP3: Rp${item.tp_levels[2].toLocaleString("id-ID")}
        </td>

        <!-- Kolom Stop Loss / CL 3 Level -->
        <td style="color:#dc3545; font-size:12px;">
          CL1: <strong>Rp${item.cl_levels[0].toLocaleString("id-ID")}</strong><br>
          CL2: Rp${item.cl_levels[1].toLocaleString("id-ID")}<br>
          CL3: Rp${item.cl_levels[2].toLocaleString("id-ID")}
        </td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Harga</th>
          <th>Status</th>
          <th>Status Indikator (&#x25B2; Terpakai/Aktif | &#x25AC; Non-Aktif)</th>
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
