<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IHSG SH4NDY's SCREENER</title>
  
  <link rel="manifest" href="./manifest.json">
  <meta name="theme-color" content="#0f172a">
  <link rel="icon" type="image/png" sizes="192x192" href="./icon-192x192.png">
  <link rel="icon" type="image/png" sizes="512x512" href="./icon-512x512.png">
  <link rel="apple-touch-icon" href="./icon-192x192.png">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none; }
    body { background-color: #0f172a; color: #f8fafc; padding: 16px; padding-bottom: 40px; }
    
    header { text-align: center; margin-bottom: 16px; }
    h1 { font-size: 1.3rem; color: #38bdf8; letter-spacing: 0.5px; }
    .update-time { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

    .control-box { background: #1e293b; padding: 12px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 16px; }
    .form-row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
    input, select, button { padding: 8px 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 0.85rem; }
    input { flex: 1; min-width: 100px; text-transform: uppercase; }
    button { background: #0284c7; color: white; border: none; font-weight: bold; cursor: pointer; }
    button:active { opacity: 0.8; }
    .btn-danger { background: #dc2626; }
    .btn-action { padding: 4px 8px; font-size: 0.75rem; border-radius: 4px; background: #334155; }

    .group-tabs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; scrollbar-width: none; }
    .tab { padding: 6px 14px; background: #1e293b; border-radius: 20px; font-size: 0.8rem; white-space: nowrap; border: 1px solid #334155; color: #94a3b8; }
    .tab.active { background: #0284c7; color: #fff; border-color: #38bdf8; font-weight: bold; }

    .card-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
    .card { background: #1e293b; padding: 12px; border-radius: 12px; border: 1px solid #334155; position: relative; }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .ticker { font-weight: bold; font-size: 1.1rem; color: #fff; }
    .price { font-size: 1.1rem; font-weight: 600; margin-bottom: 6px; color: #f1f5f9; }
    
    .badge { padding: 3px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: bold; }
    .strong-r { background: #047857; color: #34d399; border: 1px solid #10b981; }
    .breakout-r { background: #15803d; color: #86efac; border: 1px solid #22c55e; }
    .strong-s { background: #881337; color: #fda4af; border: 1px solid #f43f5e; }
    .breakout-s { background: #b91c1c; color: #fca5a5; border: 1px solid #ef4444; }
    .buy { background: #166534; color: #4ade80; }
    .sell { background: #991b1b; color: #fca5a5; }
    .neutral { background: #334155; color: #94a3b8; }

    /* Indikator Bulatan Kecil */
    .dot-indicator { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-left: 2px; margin-right: 6px; vertical-align: middle; }
    .dot-buy { background-color: #22c55e; box-shadow: 0 0 5px #22c55e; }
    .dot-neutral { background-color: #64748b; box-shadow: 0 0 3px #64748b; }
    .dot-sell { background-color: #ef4444; box-shadow: 0 0 5px #ef4444; }

    /* Warna Teks SnD */
    .text-buy { color: #22c55e; font-weight: bold; }
    .text-sell { color: #ef4444; font-weight: bold; }
    .text-neutral { color: #94a3b8; }

    .group-tag { font-size: 0.68rem; color: #38bdf8; background: #0c4a6e; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 6px; }
    .stat { font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }

    .card-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px solid #334155; }
    .reorder-btns { display: flex; gap: 4px; }
  </style>
</head>
<body>

  <header>
    <h1>IHSG SH4NDY's SCREENER</h1>
    <p class="update-time" id="updateTime">Memuat data...</p>
  </header>

  <div class="control-box">
    <div class="form-row">
      <input type="text" id="newTicker" placeholder="Ticker (misal: BBCA / IHSG)">
      <select id="newGroup">
        <option value="Harian">Pantauan Harian</option>
        <option value="Konglomerat">Konglomerat</option>
        <option value="Perbankan">Perbankan</option>
        <option value="Volatil">Volatil</option>
        <option value="Watchlist">Watchlist</option>
      </select>
      <button onclick="addStock()">+ Tambah</button>
    </div>
  </div>

  <div class="group-tabs" id="groupTabs">
    <div class="tab active" onclick="filterGroup('ALL', this)">Semua</div>
    <div class="tab" onclick="filterGroup('Harian', this)">⚡ Pantauan Harian</div>
    <div class="tab" onclick="filterGroup('Konglomerat', this)">Konglomerat</div>
    <div class="tab" onclick="filterGroup('Perbankan', this)">Perbankan</div>
    <div class="tab" onclick="filterGroup('Volatil', this)">Volatil</div>
    <div class="tab" onclick="filterGroup('Watchlist', this)">Watchlist</div>
  </div>

  <div class="card-grid" id="stockGrid"></div>

  <script>
    let rawData = [];
    let stockOrder = JSON.parse(localStorage.getItem('stock_order')) || [];
    let customGroups = JSON.parse(localStorage.getItem('custom_groups')) || {};
    let liveFetchedData = {};
    let activeFilter = 'ALL';

    function formatWIB(timeStr) {
      if (!timeStr) return "-";
      if (timeStr.includes("WIB")) return timeStr;

      try {
        const date = new Date(timeStr);
        if (isNaN(date.getTime())) return timeStr;

        return date.toLocaleString('id-ID', {
          timeZone: 'Asia/Jakarta',
          day: '2-digit',
          month: 'long',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }) + " WIB";
      } catch (e) {
        return timeStr;
      }
    }

    function calculateRSI(closes, window = 14) {
      if (closes.length < window + 1) return 50;
      let gains = 0, losses = 0;
      for (let i = 1; i <= window; i++) {
        let diff = closes[i] - closes[i - 1];
        if (diff >= 0) gains += diff;
        else losses -= diff;
      }
      let avgGain = gains / window;
      let avgLoss = losses / window;
      if (avgLoss === 0) return 100;
      let rs = avgGain / avgLoss;
      return Math.round((100 - (100 / (1 + rs))) * 100) / 100;
    }

    async function fetchLiveStockData(ticker) {
      const yfSymbol = ticker === "IHSG" ? "^JKSE" : `${ticker}.JK`;
      const url = `https://query1.finance.yahoo.com/v8/finance/chart/${yfSymbol}?range=3mo&interval=1d`;

      try {
        const response = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
        const result = await response.json();
        const data = JSON.parse(result.contents).chart.result[0];

        const quotes = data.indicators.quote[0];
        const closes = quotes.close.filter(v => v !== null);
        const highs = quotes.high.filter(v => v !== null);
        const lows = quotes.low.filter(v => v !== null);
        const volumes = quotes.volume.filter(v => v !== null);

        if (closes.length < 20) return null;

        const lastClose = Math.round(closes[closes.length - 1] * 100) / 100;
        const sliceCloses = closes.slice(-20);
        const ma20 = Math.round((sliceCloses.reduce((a, b) => a + b, 0) / 20) * 100) / 100;
        
        const sliceVols = volumes.slice(-20);
        const volMa20 = sliceVols.reduce((a, b) => a + b, 0) / 20;
        const lastVol = volumes[volumes.length - 1];
        const volRatio = volMa20 > 0 ? Math.round((lastVol / volMa20) * 100) / 100 : 1.0;

        let volStatus = "NEUTRAL";
        if (volRatio >= 1.5) volStatus = "BUY";
        else if (volRatio < 0.7) volStatus = "SELL";

        const res20 = Math.max(...highs.slice(-21, -1));
        const sup20 = Math.min(...lows.slice(-21, -1));

        let sndStatus = "NEUTRAL";
        if (sup20 > 0 && lastClose <= (sup20 * 1.02)) sndStatus = "BUY";
        else if (res20 > 0 && lastClose >= (res20 * 0.98)) sndStatus = "SELL";

        const rsi = calculateRSI(closes);
        let rsiStatus = "NEUTRAL";
        if (rsi < 35) rsiStatus = "BUY";
        else if (rsi > 70) rsiStatus = "SELL";

        let signal = "NEUTRAL";
        if (lastClose > res20 && res20 > 0) {
          signal = volRatio >= 1.5 ? "SBR" : "Break R";
        } else if (lastClose < sup20 && sup20 > 0) {
          signal = volRatio >= 1.5 ? "SBS" : "Break S";
        } else if (rsiStatus === "BUY" || lastClose > ma20) {
          signal = "BUY";
        } else if (rsiStatus === "SELL" || lastClose < ma20) {
          signal = "SELL";
        }

        return {
          ticker: ticker,
          price: lastClose,
          rsi: rsi,
          rsi_status: rsiStatus,
          ma20: ma20,
          support: Math.round(sup20 * 100) / 100,
          resistance: Math.round(res20 * 100) / 100,
          snd_status: sndStatus,
          vol_ratio: volRatio,
          vol_status: volStatus,
          macd_status: "NEUTRAL",
          signal: signal
        };

      } catch (err) {
        console.error(`Gagal memuat live data untuk ${ticker}:`, err);
        return null;
      }
    }

    async function loadData() {
      try {
        const res = await fetch('./data.json?v=' + Date.now(), { cache: 'no-store' });
        const data = await res.json();
        
        const wibTime = formatWIB(data.updated_at);
        document.getElementById('updateTime').innerText = "Diperbarui: " + wibTime;
        
        rawData = data.stocks || [];

        if (stockOrder.length === 0) {
          stockOrder = rawData.map(s => s.ticker);
          saveState();
        }

        const missingTickers = stockOrder.filter(t => !rawData.some(s => s.ticker === t));
        for (let ticker of missingTickers) {
          const fetched = await fetchLiveStockData(ticker);
          if (fetched) {
            liveFetchedData[ticker] = fetched;
          }
        }

        render();
      } catch (e) {
        document.getElementById('updateTime').innerText = "Gagal memuat data.json";
      }
    }

    function render() {
      const grid = document.getElementById('stockGrid');
      grid.innerHTML = '';

      let orderedList = [];
      stockOrder.forEach(ticker => {
        let item = rawData.find(s => s.ticker === ticker) || liveFetchedData[ticker] || { 
          ticker, price: 0, rsi: 0, rsi_status: 'NEUTRAL', ma20: 0, support: 0, resistance: 0, snd_status: 'NEUTRAL', vol_ratio: 1.0, vol_status: 'NEUTRAL', macd_status: 'NEUTRAL', signal: 'NEUTRAL' 
        };
        orderedList.push(item);
      });

      orderedList.forEach((stock, index) => {
        const group = customGroups[stock.ticker] || 'Watchlist';
        
        if (activeFilter !== 'ALL' && group !== activeFilter) return;

        let badgeClass = 'neutral';
        if (stock.signal === 'SBR') badgeClass = 'strong-r';
        else if (stock.signal === 'Break R') badgeClass = 'breakout-r';
        else if (stock.signal === 'SBS') badgeClass = 'strong-s';
        else if (stock.signal === 'Break S') badgeClass = 'breakout-s';
        else if (stock.signal === 'BUY') badgeClass = 'buy';
        else if (stock.signal === 'SELL') badgeClass = 'sell';

        // Bulatan Indikator RSI
        let rsiDotClass = 'dot-neutral';
        if (stock.rsi_status === 'BUY') rsiDotClass = 'dot-buy';
        else if (stock.rsi_status === 'SELL') rsiDotClass = 'dot-sell';

        // Bulatan Indikator MACD
        let macdDotClass = 'dot-neutral';
        if (stock.macd_status === 'BUY') macdDotClass = 'dot-buy';
        else if (stock.macd_status === 'SELL') macdDotClass = 'dot-sell';

        // Bulatan Indikator Volume
        let volDotClass = 'dot-neutral';
        if (stock.vol_status === 'BUY') volDotClass = 'dot-buy';
        else if (stock.vol_status === 'SELL') volDotClass = 'dot-sell';

        // Warna Teks SnD (Tanpa Bulatan)
        let sndTextClass = 'text-neutral';
        if (stock.snd_status === 'BUY') sndTextClass = 'text-buy';
        else if (stock.snd_status === 'SELL') sndTextClass = 'text-sell';

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
          <div class="card-header">
            <span class="ticker">${stock.ticker}</span>
            <span class="badge ${badgeClass}">${stock.signal}</span>
          </div>
          <span class="group-tag">${group}</span>
          <div class="price">Rp ${Number(stock.price).toLocaleString('id-ID')}</div>
          <div class="stat">
            RSI: <span class="dot-indicator ${rsiDotClass}"></span>
            MACD: <span class="dot-indicator ${macdDotClass}"></span>
            Vol: <span class="dot-indicator ${volDotClass}"></span>
          </div>
          <div class="stat ${sndTextClass}">S: ${stock.support} | R: ${stock.resistance}</div>
          <div class="stat">Vol: ${stock.vol_ratio}x Rerata</div>

          <div class="card-actions">
            <div class="reorder-btns">
              <button class="btn-action" onclick="moveStock(${index}, -1)">▲</button>
              <button class="btn-action" onclick="moveStock(${index}, 1)">▼</button>
            </div>
            <button class="btn-action btn-danger" onclick="removeStock('${stock.ticker}')">Hapus</button>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    async function addStock() {
      const input = document.getElementById('newTicker');
      const groupSelect = document.getElementById('newGroup');
      let ticker = input.value.trim().toUpperCase();

      if (!ticker) return;

      if (!stockOrder.includes(ticker)) {
        stockOrder.push(ticker);
      }
      customGroups[ticker] = groupSelect.value;
      
      input.value = '';
      saveState();

      if (!rawData.some(s => s.ticker === ticker)) {
        document.getElementById('updateTime').innerText = `Memuat data live ${ticker}...`;
        const fetched = await fetchLiveStockData(ticker);
        if (fetched) liveFetchedData[ticker] = fetched;
        document.getElementById('updateTime').innerText = "Data siap!";
      }

      render();
    }

    function removeStock(ticker) {
      stockOrder = stockOrder.filter(t => t !== ticker);
      delete customGroups[ticker];
      delete liveFetchedData[ticker];
      saveState();
      render();
    }

    function moveStock(index, direction) {
      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= stockOrder.length) return;
      
      const temp = stockOrder[index];
      stockOrder[index] = stockOrder[newIndex];
      stockOrder[newIndex] = temp;
      
      saveState();
      render();
    }

    function filterGroup(group, el) {
      activeFilter = group;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      el.classList.add('active');
      render();
    }

    function saveState() {
      localStorage.setItem('stock_order', JSON.stringify(stockOrder));
      localStorage.setItem('custom_groups', JSON.stringify(customGroups));
    }

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js');
    }

    loadData();
  </script>
</body>
</html>
