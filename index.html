<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SH4NDY's SWING SCREENER</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- CSS Independen -->
    <link rel="stylesheet" href="styles.css">
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen p-3 sm:p-6 font-sans">
    <div class="max-w-7xl mx-auto">
        
        <!-- Sticky Main Header -->
        <header class="sticky top-0 z-50 bg-gray-900/95 backdrop-blur pt-2 pb-4 mb-4 border-b border-gray-800 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div>
                <h1 class="text-xl sm:text-2xl font-bold text-green-400 flex items-center gap-2">
                    📈 SH4NDY's SWING SCREENER
                </h1>
                <div class="flex items-center gap-2 mt-0.5">
                    <p class="text-gray-400 text-xs" id="last-updated">Status: Memuat data...</p>
                    <span id="market-status-badge" class="text-[10px] px-2 py-0.5 rounded font-bold bg-gray-800 text-gray-400">PASAR TUTUP</span>
                </div>
            </div>

            <!-- Search Area -->
            <div class="flex flex-col items-end gap-1 w-full lg:w-auto">
                <div class="flex items-center gap-2 w-full lg:w-auto">
                    <div class="relative flex-1 lg:w-72">
                        <input 
                            type="text" 
                            id="search-input" 
                            placeholder="Cari Kode Saham (cth: BNBR)..." 
                            class="w-full bg-gray-800 text-white placeholder-gray-500 border border-gray-700 rounded-lg pl-3 pr-14 py-2 text-sm focus:outline-none focus:border-green-500 transition-colors uppercase"
                            oninput="liveSearch()"
                            onkeyup="handleSearch(event)"
                        />
                        <button id="clear-search-btn" onclick="clearSearchInput()" class="hidden absolute right-8 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-400 text-xs font-bold p-1">✕</button>
                        <button onclick="executeSearch(true)" class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-green-400 p-1" title="Cari / Tambah ke Pantauan">🔍</button>
                    </div>

                    <button onclick="reloadPage()" class="bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 p-2 rounded-lg transition-all" title="Reload Halaman">
                        <svg id="reload-icon" class="w-5 h-5 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    </button>
                </div>
                <div id="search-status-text" class="text-[11px] text-gray-400 min-h-[16px] px-1 transition-all"></div>
            </div>
        </header>

        <!-- Section IHSG -->
        <section id="ihsg-card" class="mb-6 bg-gray-800/60 border border-gray-700/60 rounded-xl p-4 shadow-lg transition-colors duration-500">
            <div class="flex items-center justify-between mb-3">
                <h3 class="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                    🏛️ Indeks Harga Saham Gabungan (IHSG)
                </h3>
                <div class="flex items-center gap-2">
                    <span id="ihsg-header-close" class="font-bold text-base text-gray-100">0.00</span>
                    <span id="ihsg-header-pct" class="font-bold px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">0.00%</span>
                </div>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-center text-sm border-collapse">
                    <thead>
                        <tr class="bg-gray-800/80 text-gray-400 text-xs uppercase border-b border-gray-700">
                            <th class="py-2 px-3">PREV</th>
                            <th class="py-2 px-3">O (Open)</th>
                            <th class="py-2 px-3">L (Low)</th>
                            <th class="py-2 px-3">H (High)</th>
                            <th class="py-2 px-3">C (Close)</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-700/50">
                        <tr class="font-semibold text-gray-200">
                            <td class="py-2.5 px-3 text-gray-400" id="ihsg-col-prev">0.00</td>
                            <td class="py-2.5 px-3 text-blue-400" id="ihsg-col-open">0.00</td>
                            <td class="py-2.5 px-3 text-red-400" id="ihsg-col-low">0.00</td>
                            <td class="py-2.5 px-3 text-green-400" id="ihsg-col-high">0.00</td>
                            <td class="py-2.5 px-3 font-bold" id="ihsg-col-close">0.00</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Dynamic Filter Tabs -->
        <div class="sticky top-[73px] z-40 bg-gray-900/95 backdrop-blur py-2 mb-6 border-b border-gray-800 flex flex-wrap gap-2" id="tabs-container">
            <button id="tab-swing_setup" onclick="switchTab('swing_setup')" class="tab-btn bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 shadow-md">
                🎯 Swing Setup <span id="count-swing_setup" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
            <button id="tab-top_gainers" onclick="switchTab('top_gainers')" class="tab-btn bg-gray-800 text-gray-300 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                🚀 Top Gainers <span id="count-top_gainers" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
            <button id="tab-top_movers" onclick="switchTab('top_movers')" class="tab-btn bg-gray-800 text-gray-300 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                🔥 Top Movers <span id="count-top_movers" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
            <button id="tab-bluechips" onclick="switchTab('bluechips')" class="tab-btn bg-gray-800 text-gray-300 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                💎 Bluechip <span id="count-bluechips" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
            <button id="tab-top_bearish" onclick="switchTab('top_bearish')" class="tab-btn bg-gray-800 text-gray-300 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                🔻 Terlemah <span id="count-top_bearish" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
            <button id="tab-all_stocks" onclick="switchTab('all_stocks')" class="tab-btn bg-gray-800 text-gray-300 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                🌐 Semua Emiten <span id="count-all_stocks" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
            <button id="tab-pantauan" onclick="switchTab('pantauan')" class="tab-btn bg-gray-800 text-gray-300 hover:bg-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                👁️ Pantauan <span id="count-pantauan" class="bg-black/30 px-1.5 py-0.5 rounded-full">0</span>
            </button>
        </div>

        <!-- Top 10 Entry Signal -->
        <section class="mb-6 bg-gradient-to-r from-gray-850 via-gray-800 to-gray-850 border border-green-500/30 rounded-xl p-4 shadow-xl">
            <div class="flex items-center justify-between mb-3 border-b border-gray-700/60 pb-2">
                <div class="flex items-center gap-2">
                    <span class="text-lg">🔥</span>
                    <h2 class="text-sm font-bold text-green-400 tracking-wide">Top 10 Entry Signal Terkuat</h2>
                </div>
                <span class="text-[10px] bg-green-500/20 text-green-300 border border-green-500/40 px-2 py-0.5 rounded-full">Auto-Ranked</span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead>
                        <tr class="text-gray-400 uppercase border-b border-gray-700/50">
                            <th class="py-2 px-2"># Rank</th>
                            <th class="py-2 px-2">Ticker</th>
                            <th class="py-2 px-2 text-center">Trend</th>
                            <th class="py-2 px-2">Closing</th>
                            <th class="py-2 px-2">Change (%)</th>
                            <th class="py-2 px-2 text-red-400">Cut Loss</th>
                            <th class="py-2 px-2 text-green-400">TP 1</th>
                            <th class="py-2 px-2 text-green-400">TP 2</th>
                            <th class="py-2 px-2 text-center">Signal Power</th>
                        </tr>
                    </thead>
                    <tbody id="top-10-data" class="divide-y divide-gray-700/40"></tbody>
                </table>
            </div>
        </section>

        <!-- Tampilan Desktop (Tabel) -->
        <div class="hidden md:block overflow-x-auto bg-gray-800 rounded-xl border border-gray-700 shadow-xl">
            <table class="w-full text-left border-collapse text-xs">
                <thead>
                    <tr class="bg-gray-850 border-b border-gray-700 text-gray-400 uppercase tracking-wider">
                        <th class="p-3">Ticker</th>
                        <th class="p-3">Closing</th>
                        <th class="p-3">Change (%)</th>
                        <th class="p-3 text-right">EMA 14</th>
                        <th class="p-3 text-center w-6"></th>
                        <th class="p-3 text-center">Trend</th>
                        <th class="p-3 text-right">EMA 50</th>
                        <th class="p-3 text-center w-6"></th>
                        <th class="p-3 text-right">RSI (14)</th>
                        <th class="p-3 text-center w-6"></th>
                        <th class="p-3 text-red-400">Cut Loss</th>
                        <th class="p-3 text-green-400">TP 1</th>
                        <th class="p-3 text-green-400">TP 2</th>
                        <th class="p-3 text-center">Signal Power</th>
                        <th class="p-3 text-center">Aksi</th>
                    </tr>
                </thead>
                <tbody id="screener-data-desktop" class="divide-y divide-gray-700"></tbody>
            </table>
        </div>

        <!-- Tampilan Mobile (Cards) -->
        <div class="block md:hidden space-y-2.5" id="screener-data-mobile"></div>

    </div>

    <!-- Modal Popup Detail Mobile -->
    <div id="mobile-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-gray-800 border border-gray-700 rounded-xl max-w-sm w-full p-5 shadow-2xl relative animate-fade-in">
            <button onclick="closeModal()" class="absolute right-4 top-4 text-gray-400 hover:text-white font-bold text-lg">✕</button>
            <div id="modal-content"></div>
        </div>
    </div>

    <!-- Script Pendukung -->
    <script src="screener.js"></script>
</body>
</html>
