let globalData = {};
let currentTab = 'swing_setup';
let pantauanList = JSON.parse(localStorage.getItem('pantauan_stocks') || '[]');
let searchTimeout = null;
let dynamicFetchedStocks = {};

// Cek Operasional Bursa (Senin-Jumat, 08:45 s/d 16:30 WIB)
function isMarketOpen() {
    const now = new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Jakarta" }));
    const day = now.getDay(); 
    if (day === 0 || day === 6) return false; // Sabtu & Minggu Tutup

    const hours = now.getHours();
    const minutes = now.getMinutes();
    const timeNum = hours * 100 + minutes;

    // Open: 08.45 WIB, Close: 16.30 WIB (30m setelah Tutup Pasar)
    return timeNum >= 845 && timeNum <= 1630;
}

function updateMarketBadge() {
    const badge = document.getElementById('market-status-badge');
    if (isMarketOpen()) {
        badge.innerText = "PASAR BUKA (LIVE 30s)";
        badge.className = "text-[10px] px-2 py-0.5 rounded font-bold bg-green-500/20 text-green-400 border border-green-500/40 animate-signal-blink";
    } else {
        badge.innerText = "PASAR TUTUP";
        badge.className = "text-[10px] px-2 py-0.5 rounded font-bold bg-gray-800 text-gray-400 border border-gray-700";
    }
}

async function loadData() {
    updateMarketBadge();
    try {
        const response = await fetch('data.json?t=' + new Date().getTime());
        if (!response.ok) throw new Error("Gagal memuat data.json");
        
        globalData = await response.json();
        const dateStr = new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' });
        document.getElementById('last-updated').innerText = 'Diperbarui: ' + dateStr + ' WIB';
        
        renderIHSG(globalData.ihsg || {});
        updateTabCounts();
        renderTop10Entry(globalData.top_10_entry || []);
        renderCurrentTab();
    } catch (error) {
        console.error(error);
        document.getElementById('last-updated').innerText = 'Error: Gagal memuat data';
    }
}

function renderIHSG(ihsg) {
    if (!ihsg || ihsg.close === undefined) return;
    const chgPct = ihsg.change_pct || 0;
    const ihsgCard = document.getElementById('ihsg-card');

    if (chgPct > 0) ihsgCard.className = "mb-6 bg-emerald-950/40 border border-emerald-500/40 rounded-xl p-4 shadow-lg transition-colors duration-500";
    else if (chgPct < 0) ihsgCard.className = "mb-6 bg-rose-950/40 border border-rose-500/40 rounded-xl p-4 shadow-lg transition-colors duration-500";
    else ihsgCard.className = "mb-6 bg-gray-800/60 border border-gray-700/60 rounded-xl p-4 shadow-lg transition-colors duration-500";

    const isPositive = chgPct >= 0;
    const changeClass = isPositive ? 'bg-green-500/20 text-green-400 border-green-500/40' : 'bg-red-500/20 text-red-400 border-red-500/40';
    const closeColorClass = isPositive ? 'text-green-400' : 'text-red-400';
    const changeSign = isPositive ? '+' : '';

    document.getElementById('ihsg-header-close').innerText = ihsg.close ? ihsg.close.toLocaleString('id-ID') : '0.00';
    const headerPct = document.getElementById('ihsg-header-pct');
    headerPct.innerText = `${changeSign}${ihsg.change_pct}%`;
    headerPct.className = `font-bold px-2 py-0.5 rounded text-xs border ${changeClass}`;

    document.getElementById('ihsg-col-prev').innerText = ihsg.prev_close ? ihsg.prev_close.toLocaleString('id-ID') : '-';
    document.getElementById('ihsg-col-open').innerText = ihsg.open ? ihsg.open.toLocaleString('id-ID') : '-';
    document.getElementById('ihsg-col-low').innerText = ihsg.low ? ihsg.low.toLocaleString('id-ID') : '-';
    document.getElementById('ihsg-col-high').innerText = ihsg.high ? ihsg.high.toLocaleString('id-ID') : '-';
    
    const colClose = document.getElementById('ihsg-col-close');
    colClose.innerText = ihsg.close ? ihsg.close.toLocaleString('id-ID') : '-';
    colClose.className = `py-2.5 px-3 font-bold ${closeColorClass}`;
}

function updateTabCounts() {
    const categories = ['swing_setup', 'top_gainers', 'top_movers', 'bluechips', 'top_bearish', 'all_stocks'];
    categories.forEach(cat => {
        const el = document.getElementById('count-' + cat);
        if (el && globalData[cat]) el.innerText = globalData[cat].length;
    });
    const pEl = document.getElementById('count-pantauan');
    if (pEl) pEl.innerText = pantauanList.length;
}

function renderDot(status) {
    let colorClass = 'bg-gray-500';
    let blinkClass = '';
    if (status === 'buy') colorClass = 'bg-green-500';
    else if (status === 'strong_buy') { colorClass = 'bg-green-400'; blinkClass = 'animate-signal-blink'; }
    else if (status === 'sell') colorClass = 'bg-red-500';
    else if (status === 'strong_sell') { colorClass = 'bg-red-500'; blinkClass = 'animate-signal-blink'; }
    return `<span class="inline-block w-2.5 h-2.5 rounded-full ${colorClass} ${blinkClass}" title="Status: ${status}"></span>`;
}

function renderTrendIcon(ema14, ema50) {
    if (!ema14 || !ema50) return '-';
    return ema14 >= ema50 ? '💚' : '💔';
}

function renderPowerBoxes(signal, powerScore) {
    const pct = (powerScore || 5) * 10;
    let boxColor = 'bg-gray-600', isBlink = false, iconHtml = '⏳';
    
    if (signal === 'STRONG_BULLISH') { boxColor = 'bg-green-400'; isBlink = true; iconHtml = '<span class="inline-block animate-signal-blink">🚀</span>'; }
    else if (signal === 'BULLISH') { boxColor = 'bg-green-500'; iconHtml = '🚀'; }
    else if (signal === 'STRONG_BEARISH') { boxColor = 'bg-red-500'; isBlink = true; iconHtml = '<span class="inline-block w-2.5 h-2.5 bg-red-500 rounded-full animate-signal-blink"></span>'; }
    else if (signal === 'BEARISH') { boxColor = 'bg-red-500'; iconHtml = '<span class="inline-block w-2.5 h-2.5 bg-red-500 rounded-full"></span>'; }

    let boxesHtml = '<div class="flex items-center gap-0.5">';
    for (let i = 1; i <= 10; i++) {
        const active = i <= (powerScore || 5);
        boxesHtml += `<span class="w-1.5 h-3.5 rounded-sm ${active ? boxColor : 'bg-gray-700'} ${isBlink && active ? 'animate-signal-blink' : ''}"></span>`;
    }
    boxesHtml += '</div>';

    return `
        <div class="flex items-center justify-center gap-1.5">
            <span class="text-[10px] font-bold text-gray-400 min-w-[28px] text-right">${pct}%</span>
            ${boxesHtml}
            <span class="text-xs flex items-center justify-center w-4 h-4">${iconHtml}</span>
        </div>
    `;
}

function renderTop10Entry(items) {
    const container = document.getElementById('top-10-data');
    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = `<tr><td colspan="9" class="text-center p-3 text-gray-500">Belum ada sinyal entry.</td></tr>`;
        return;
    }

    items.forEach((item, index) => {
        const isPositive = (item.change_pct || 0) >= 0;
        const changeClass = isPositive ? 'text-green-400' : 'text-red-400';
        const changeSign = isPositive ? '+' : '';
        const trendIcon = renderTrendIcon(item.ema14, item.ema50);

        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-750/50 transition-colors';
        row.innerHTML = `
            <td class="py-2 px-2 font-extrabold text-green-400">#${index + 1}</td>
            <td class="py-2 px-2 font-bold text-yellow-400">
                ${item.ticker} <span class="text-[9px] bg-gray-700 text-gray-300 px-1 py-0.5 rounded ml-0.5">${item.category}</span>
            </td>
            <td class="py-2 px-2 text-center text-sm">${trendIcon}</td>
            <td class="py-2 px-2 font-medium">${item.close ? item.close.toLocaleString('id-ID') : '-'}</td>
            <td class="py-2 px-2 font-semibold ${changeClass}">${changeSign}${item.change_pct}%</td>
            <td class="py-2 px-2 text-red-400">${item.stop_loss ? item.stop_loss.toLocaleString('id-ID') : '-'}</td>
            <td class="py-2 px-2 text-green-400">${item.take_profit_1 ? item.take_profit_1.toLocaleString('id-ID') : '-'}</td>
            <td class="py-2 px-2 text-green-400">${item.take_profit_2 ? item.take_profit_2.toLocaleString('id-ID') : '-'}</td>
            <td class="py-2 px-2 text-center">${renderPowerBoxes(item.signal, item.power_score)}</td>
        `;
        container.appendChild(row);
    });
}

function renderCurrentTab() {
    const data = currentTab === 'pantauan' ? getPantauanData() : (globalData[currentTab] || []);
    renderDesktopTable(data);
    renderMobileCards(data);
}

function switchTab(tabKey) {
    currentTab = tabKey;
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-green-600', 'text-white', 'shadow-md');
        btn.classList.add('bg-gray-800', 'text-gray-300');
    });
    const activeBtn = document.getElementById('tab-' + tabKey);
    if(activeBtn) {
        activeBtn.classList.remove('bg-gray-800', 'text-gray-300');
        activeBtn.classList.add('bg-green-600', 'text-white', 'shadow-md');
    }
    renderCurrentTab();
}

function getPantauanData() {
    const all = globalData.all_stocks || [];
    return pantauanList.map(ticker => {
        if (dynamicFetchedStocks[ticker]) return dynamicFetchedStocks[ticker];
        const found = all.find(s => s.ticker === ticker);
        return found || { ticker: ticker, close: 0, change_pct: 0, category: 'Pantauan', signal: 'NEUTRAL', power_score: 5 };
    });
}

function renderDesktopTable(items) {
    const tbody = document.getElementById('screener-data-desktop');
    tbody.innerHTML = '';

    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="15" class="text-center p-6 text-gray-500">Tidak ada data emiten.</td></tr>`;
        return;
    }

    items.forEach(item => {
        const isPositive = (item.change_pct || 0) >= 0;
        const changeClass = isPositive ? 'text-green-400' : 'text-red-400';
        const changeSign = isPositive ? '+' : '';
        const trendIcon = renderTrendIcon(item.ema14, item.ema50);

        const row = document.createElement('tr');
        row.id = 'row-' + item.ticker;
        row.className = 'hover:bg-gray-750 transition-colors border-b border-gray-700/50';

        const isPantauanTab = currentTab === 'pantauan';
        const inPantauan = pantauanList.includes(item.ticker);

        row.innerHTML = `
            <td class="p-3 font-bold text-yellow-400 flex items-center gap-1.5">
                <span>${item.ticker}</span>
                <span class="text-[9px] bg-gray-700 text-gray-300 px-1 py-0.5 rounded">${item.category || 'IDX'}</span>
            </td>
            <td class="p-3 font-medium">${item.close ? item.close.toLocaleString('id-ID') : '-'}</td>
            <td class="p-3 font-semibold ${changeClass}">${changeSign}${item.change_pct}%</td>
            <td class="p-3 text-right text-gray-300">${item.ema14 ? item.ema14.toLocaleString('id-ID') : '-'}</td>
            <td class="p-3 text-center">${renderDot(item.ema14_status || 'neutral')}</td>
            <td class="p-3 text-center text-sm">${trendIcon}</td>
            <td class="p-3 text-right text-gray-300">${item.ema50 ? item.ema50.toLocaleString('id-ID') : '-'}</td>
            <td class="p-3 text-center">${renderDot(item.ema50_status || 'neutral')}</td>
            <td class="p-3 text-right text-gray-300">${item.rsi || '-'}</td>
            <td class="p-3 text-center">${renderDot(item.rsi_status || 'neutral')}</td>
            <td class="p-3 text-red-400 font-medium">${item.stop_loss ? item.stop_loss.toLocaleString('id-ID') : '-'}</td>
            <td class="p-3 text-green-400 font-medium">${item.take_profit_1 ? item.take_profit_1.toLocaleString('id-ID') : '-'}</td>
            <td class="p-3 text-green-400 font-medium">${item.take_profit_2 ? item.take_profit_2.toLocaleString('id-ID') : '-'}</td>
            <td class="p-3 text-center">${renderPowerBoxes(item.signal || 'NEUTRAL', item.power_score || 5)}</td>
            <td class="p-3 text-center">
                <div class="flex items-center justify-center gap-1.5">
                    <button onclick="copyTicker('${item.ticker}')" class="bg-gray-700 hover:bg-gray-600 text-gray-200 p-1 rounded text-xs" title="Copy Ticker">📋</button>
                    ${isPantauanTab ? 
                        `<button onclick="removeFromPantauan('${item.ticker}')" class="bg-red-900/60 hover:bg-red-700 text-red-300 p-1 rounded text-xs">❌</button>` :
                        `<button onclick="addToPantauan('${item.ticker}')" class="${inPantauan ? 'bg-green-800 text-green-300' : 'bg-gray-700 hover:bg-gray-600 text-gray-200'} p-1 rounded text-xs">${inPantauan ? '✓' : '👁️+'}</button>`
                    }
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderMobileCards(items) {
    const container = document.getElementById('screener-data-mobile');
    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = `<div class="text-center p-6 text-gray-500 bg-gray-800 rounded-xl border border-gray-700">Tidak ada emiten.</div>`;
        return;
    }

    items.forEach(item => {
        const isPositive = (item.change_pct || 0) >= 0;
        const changeClass = isPositive ? 'text-green-400' : 'text-red-400';
        const changeSign = isPositive ? '+' : '';
        const trendIcon = renderTrendIcon(item.ema14, item.ema50);

        const card = document.createElement('div');
        card.id = 'm-card-' + item.ticker;
        card.className = 'bg-gray-800 border border-gray-700 rounded-xl p-3 flex items-center justify-between shadow-md active:bg-gray-750 transition-all cursor-pointer';
        card.onclick = (e) => {
            if (e.target.tagName === 'BUTTON') return;
            openModal(item);
        };

        const isPantauanTab = currentTab === 'pantauan';
        const inPantauan = pantauanList.includes(item.ticker);

        card.innerHTML = `
            <div class="flex flex-col gap-1 w-full">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-1.5">
                        <span class="font-bold text-yellow-400 text-base">${item.ticker}</span>
                        <span class="text-sm">${trendIcon}</span>
                        <span class="text-[9px] bg-gray-700 text-gray-300 px-1 py-0.5 rounded">${item.category || 'IDX'}</span>
                    </div>
                    <div class="text-right">
                        <span class="font-bold text-gray-100 text-sm">${item.close ? item.close.toLocaleString('id-ID') : '-'}</span>
                        <span class="text-xs font-semibold ${changeClass} ml-1.5">${changeSign}${item.change_pct}%</span>
                    </div>
                </div>

                <div class="flex items-center justify-between mt-1 pt-2 border-t border-gray-700/60">
                    <div>${renderPowerBoxes(item.signal || 'NEUTRAL', item.power_score || 5)}</div>
                    <div class="flex items-center gap-1">
                        <button onclick="copyTicker('${item.ticker}')" class="bg-gray-700 text-gray-200 px-2 py-1 rounded text-xs">📋</button>
                        ${isPantauanTab ? 
                            `<button onclick="removeFromPantauan('${item.ticker}')" class="bg-red-900/60 text-red-300 px-2 py-1 rounded text-xs">❌</button>` :
                            `<button onclick="addToPantauan('${item.ticker}')" class="${inPantauan ? 'bg-green-800 text-green-300' : 'bg-gray-700 text-gray-200'} px-2 py-1 rounded text-xs">${inPantauan ? '✓' : '👁️+'}</button>`
                        }
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function openModal(item) {
    const isPositive = (item.change_pct || 0) >= 0;
    const changeClass = isPositive ? 'text-green-400' : 'text-red-400';
    const changeSign = isPositive ? '+' : '';
    const trendIcon = renderTrendIcon(item.ema14, item.ema50);

    const contentHtml = `
        <div class="space-y-4 text-xs">
            <div class="border-b border-gray-700 pb-2">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-bold text-yellow-400 flex items-center gap-2">
                        ${item.ticker} <span>${trendIcon}</span>
                        <span class="text-xs text-gray-400 font-normal">(${item.category || 'IDX'})</span>
                    </h3>
                    <span class="text-sm font-bold ${changeClass}">${changeSign}${item.change_pct}%</span>
                </div>
                <p class="text-gray-300 text-sm font-semibold mt-1">Harga Closing: ${item.close ? item.close.toLocaleString('id-ID') : '-'}</p>
            </div>

            <div class="space-y-2">
                <p class="text-gray-400 font-semibold uppercase text-[10px]">Indikator Strategi Swing</p>
                <div class="grid grid-cols-2 gap-2 bg-gray-850 p-2.5 rounded-lg border border-gray-700">
                    <div>EMA 14: <span class="font-bold text-gray-200">${item.ema14 ? item.ema14.toLocaleString('id-ID') : '-'}</span> ${renderDot(item.ema14_status)}</div>
                    <div>EMA 50: <span class="font-bold text-gray-200">${item.ema50 ? item.ema50.toLocaleString('id-ID') : '-'}</span> ${renderDot(item.ema50_status)}</div>
                    <div class="col-span-2">RSI (14): <span class="font-bold text-gray-200">${item.rsi || '-'}</span> ${renderDot(item.rsi_status)}</div>
                </div>
            </div>

            <div class="space-y-1">
                <p class="text-gray-400 font-semibold uppercase text-[10px]">Power Signal Score</p>
                <div class="bg-gray-850 p-2.5 rounded-lg border border-gray-700 flex justify-center">
                    ${renderPowerBoxes(item.signal, item.power_score)}
                </div>
            </div>

            <div class="space-y-2">
                <p class="text-gray-400 font-semibold uppercase text-[10px]">Trading Plan</p>
                <div class="bg-gray-850 p-2.5 rounded-lg border border-gray-700 space-y-1.5">
                    <div class="flex justify-between text-red-400 font-semibold">
                        <span>Cut Loss (SL):</span>
                        <span>${item.stop_loss ? item.stop_loss.toLocaleString('id-ID') : '-'}</span>
                    </div>
                    <div class="flex justify-between text-green-400 font-semibold">
                        <span>Take Profit 1 (TP1):</span>
                        <span>${item.take_profit_1 ? item.take_profit_1.toLocaleString('id-ID') : '-'}</span>
                    </div>
                    <div class="flex justify-between text-green-400 font-semibold">
                        <span>Take Profit 2 (TP2):</span>
                        <span>${item.take_profit_2 ? item.take_profit_2.toLocaleString('id-ID') : '-'}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('modal-content').innerHTML = contentHtml;
    document.getElementById('mobile-modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('mobile-modal').classList.add('hidden');
}

function copyTicker(ticker) {
    navigator.clipboard.writeText(ticker);
    const statusEl = document.getElementById('search-status-text');
    statusEl.className = "text-[11px] text-green-400 font-semibold min-h-[16px] px-1";
    statusEl.innerText = `✓ Kode emiten ${ticker} berhasil dicopy!`;
    setTimeout(() => { statusEl.innerText = ''; }, 2000);
}

function addToPantauan(ticker) {
    if (!pantauanList.includes(ticker)) {
        pantauanList.push(ticker);
        localStorage.setItem('pantauan_stocks', JSON.stringify(pantauanList));
        updateTabCounts();
        renderCurrentTab();
    }
}

function removeFromPantauan(ticker) {
    pantauanList = pantauanList.filter(t => t !== ticker);
    localStorage.setItem('pantauan_stocks', JSON.stringify(pantauanList));
    updateTabCounts();
    renderCurrentTab();
}

// Fetch Dinamis YFinance untuk Saham Pencarian
async function fetchYFinanceRealtime(ticker) {
    try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}.JK?interval=1d&range=3m`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Emiten tidak ditemukan");
        const json = await res.json();
        const result = json.chart.result[0];
        const quotes = result.indicators.quote[0].close;
        const validQuotes = quotes.filter(v => v !== null);

        if (validQuotes.length < 14) throw new Error("Data historis tidak cukup");

        const close = Math.round(validQuotes[validQuotes.length - 1]);
        const prevClose = Math.round(validQuotes[validQuotes.length - 2]);
        const changePct = parseFloat((((close - prevClose) / prevClose) * 100).toFixed(2));

        const k14 = 2 / (14 + 1);
        let ema14 = validQuotes[0];
        for (let i = 1; i < validQuotes.length; i++) ema14 = (validQuotes[i] * k14) + (ema14 * (1 - k14));

        const k50 = 2 / (50 + 1);
        let ema50 = validQuotes[0];
        for (let i = 1; i < validQuotes.length; i++) ema50 = (validQuotes[i] * k50) + (ema50 * (1 - k50));

        ema14 = Math.round(ema14);
        ema50 = Math.round(ema50);

        return {
            ticker: ticker,
            close: close,
            change_pct: changePct,
            category: 'YFinance Live',
            ema14: ema14,
            ema14_status: close > ema14 ? "buy" : "sell",
            ema50: ema50,
            ema50_status: ema14 > ema50 ? "buy" : "sell",
            rsi: 50.0,
            rsi_status: "neutral",
            signal: ema14 >= ema50 ? "BULLISH" : "BEARISH",
            power_score: ema14 >= ema50 ? 7 : 3,
            stop_loss: Math.round(close * 0.95),
            take_profit_1: Math.round(close * 1.05),
            take_profit_2: Math.round(close * 1.10)
        };
    } catch (err) {
        console.error("Gagal mengambil data dari YFinance:", err);
        return null;
    }
}

function liveSearch() {
    clearTimeout(searchTimeout);
    const statusEl = document.getElementById('search-status-text');
    const clearBtn = document.getElementById('clear-search-btn');
    const input = document.getElementById('search-input').value.trim().toUpperCase();

    if (!input) {
        statusEl.innerText = '';
        clearBtn.classList.add('hidden');
        return;
    }

    clearBtn.classList.remove('hidden');
    statusEl.className = "text-[11px] text-gray-400 min-h-[16px] px-1";
    statusEl.innerText = `Mencari '${input}'...`;

    searchTimeout = setTimeout(() => { executeSearch(false); }, 300);
}

function clearSearchInput() {
    document.getElementById('search-input').value = '';
    document.getElementById('clear-search-btn').classList.add('hidden');
    document.getElementById('search-status-text').innerText = '';
}

function handleSearch(event) {
    if (event.key === 'Enter') executeSearch(true);
}

async function executeSearch(isManualClick = false) {
    const input = document.getElementById('search-input').value.trim().toUpperCase();
    const statusEl = document.getElementById('search-status-text');
    if (!input) return;

    let targetCategory = null;
    let targetStock = null;
    const categories = ['swing_setup', 'top_gainers', 'top_movers', 'bluechips', 'top_bearish', 'all_stocks'];

    for (const cat of categories) {
        if (globalData[cat]) {
            const found = globalData[cat].find(s => s.ticker === input);
            if (found) {
                targetCategory = cat;
                targetStock = found;
                break;
            }
        }
    }

    if (targetStock && targetCategory) {
        statusEl.className = "text-[11px] text-green-400 font-semibold min-h-[16px] px-1";
        statusEl.innerText = `✓ Emiten ${targetStock.ticker} ditemukan di kategori ${targetCategory.replace('_', ' ').toUpperCase()}`;

        if (currentTab !== targetCategory) switchTab(targetCategory);

        setTimeout(() => {
            const el = document.getElementById('row-' + targetStock.ticker) || document.getElementById('m-card-' + targetStock.ticker);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                el.classList.remove('animate-blink');
                void el.offsetWidth;
                el.classList.add('animate-blink');
            }
        }, 100);
    } else {
        if (isManualClick) {
            statusEl.className = "text-[11px] text-yellow-400 font-semibold min-h-[16px] px-1";
            statusEl.innerText = `🔄 Mengambil data realtime '${input}'...`;

            const liveStock = await fetchYFinanceRealtime(input);
            if (liveStock) {
                dynamicFetchedStocks[input] = liveStock;
                statusEl.className = "text-[11px] text-green-400 font-semibold min-h-[16px] px-1";
                statusEl.innerText = `✓ Data ${input} berhasil diambil dari YFinance.`;
            } else {
                statusEl.className = "text-[11px] text-yellow-400 font-semibold min-h-[16px] px-1";
                statusEl.innerText = `⚠️ ${input} ditambahkan ke Pantauan (Manual).`;
            }

            if (!pantauanList.includes(input)) {
                pantauanList.push(input);
                localStorage.setItem('pantauan_stocks', JSON.stringify(pantauanList));
                updateTabCounts();
            }

            switchTab('pantauan');
        }
    }
}

function reloadPage() {
    const icon = document.getElementById('reload-icon');
    icon.classList.add('rotate-180');
    setTimeout(() => loadData(), 300);
}

// Inisialisasi Pertama
loadData();

// Auto Refresh Tiap 30 Detik HANYA saat Jam Bursa Aktif
setInterval(() => {
    if (isMarketOpen()) {
        console.log("Jam Bursa Aktif: Refreshing data otomatis...");
        loadData();
    } else {
        updateMarketBadge();
    }
}, 30000);