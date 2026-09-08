const DATA_URL = './data.json';
let currentStyle = 'scalping';

async function initScreener() {
  const container = document.getElementById("screenerContainer");
  try {
    const response = await fetch(`${DATA_URL}?t=${new Date().getTime()}`);
    if (!response.ok) throw new Error("File data.json tidak ditemukan.");
    
    const data = await response.json();
    
    // Render Peringatan Pasar
    if (data.market_status) {
      renderMarketWarning(data.market_status);
    }
    
    // Render Tabel Utama
    renderTable(data[currentStyle] || []);
    
    // Event Listener Tombol Header
    setupButtons(data);

  } catch (error) {
    console.error("Error loading screener:", error);
    if (container) {
      container.innerHTML = `<div style="color:red; padding:20px; font-weight:bold;">Gagal memuat data. Pastikan file data.json sudah digenerate oleh fetch_data.py.</div>`;
    }
  }
}

function renderMarketWarning(status) {
  const warningContainer = document.getElementById("marketWarning");
  if (!warningContainer || !status.warning) return;

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
      renderTable(allData[currentStyle] || []);
    };
  });
}

// Format Indikator dengan Panah Hijau (▲) atau Garis Abu-abu (▬)
function formatInd(ind) {
  if (!ind) return '';
  if (ind.active) {
    return `<div style="color:#198754; font-weight:bold;">&#9650; ${ind.name}: <span style="color:#333; font-weight:normal;">${ind.val}</span></div>`;
  } else {
    return `<div style="color:#adb5bd;">&#9644; ${ind.name}: <span>${ind.val}</span></div>`;
  }
}

function renderTable(stockList) {
  const container = document.getElementById("screenerContainer");
  if (!container) return;

  if (!stockList || stockList.length === 0) {
    container.innerHTML = `<div style="padding:20px; background:white; border-radius:8px;">Tidak ada data saham untuk kategori ini. Jalankan script Python terlebih dahulu.</div>`;
    return;
  }

  const rows = stockList.map(item => {
    const isLayak = item.status && item.status.includes("LAYAK");
    const bgBadge = isLayak ? '#198754' : '#6c757d';
    const inds = item.indicators || {};

    const entry = item.entry_levels || [0, 0, 0];
    const tp = item.tp_levels || [0, 0, 0];
    const cl = item.cl_levels || [0, 0, 0];

    return `
      <tr>
        <td><strong>${item.ticker}</strong></td>
        <td>Rp${item.price ? item.price.toLocaleString("id-ID") : 0}</td>
        <td><span class="badge" style="background-color:${bgBadge};">${item.status}</span></td>
        
        <!-- Deretan Kolom Indikator (Termasuk Indikator Baru) -->
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
          L1: Rp${entry[0].toLocaleString("id-ID")}<br>
          L2: Rp${entry[1].toLocaleString("id-ID")}<br>
          L3: Rp${entry[2].toLocaleString("id-ID")}
        </td>

        <!-- Target TP 3 Level -->
        <td style="color:#198754; font-size:12px;">
          TP1: Rp${tp[0].toLocaleString("id-ID")}<br>
          TP2: Rp${tp[1].toLocaleString("id-ID")}<br>
          TP3: Rp${tp[2].toLocaleString("id-ID")}
        </td>

        <!-- Cut Loss 3 Level -->
        <td style="color:#dc3545; font-size:12px;">
          CL1: Rp${cl[0].toLocaleString("id-ID")}<br>
          CL2: Rp${cl[1].toLocaleString("id-ID")}<br>
          CL3: Rp${cl[2].toLocaleString("id-ID")}
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
