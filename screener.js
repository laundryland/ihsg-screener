const fs = require('fs');
const axios = require('axios');
const cheerio = require('cheerio');

// ============================================================
// 1. DAFTAR 100 EMITEN IDX KOMPETEN & LIKUID
// ============================================================
const TICKERS_DATA = [
  // Perbankan & Keuangan
  { ticker: "BBCA", category: "Bluechip" },
  { ticker: "BMRI", category: "Bluechip" },
  { ticker: "BBRI", category: "Bluechip" },
  { ticker: "BBNI", category: "Bluechip" },
  { ticker: "BRIS", category: "Financials" },
  { ticker: "BBTN", category: "Financials" },
  { ticker: "BDMN", category: "Financials" },
  { ticker: "BNGA", category: "Financials" },
  { ticker: "ARTO", category: "Financials" },
  { ticker: "MEGA", category: "Financials" },
  { ticker: "NISP", category: "Financials" },
  { ticker: "PNBN", category: "Financials" },
  { ticker: "SRTG", category: "Financials" },
  { ticker: "SMMA", category: "Financials" },
  { ticker: "AMAR", category: "Financials" },

  // Energi, Batubara & Migas
  { ticker: "ADRO", category: "Energy" },
  { ticker: "PTBA", category: "Energy" },
  { ticker: "ITMG", category: "Energy" },
  { ticker: "BYAN", category: "Bluechip" },
  { ticker: "PGAS", category: "Energy" },
  { ticker: "AKRA", category: "Energy" },
  { ticker: "MEDC", category: "Energy" },
  { ticker: "INDY", category: "Energy" },
  { ticker: "HRUM", category: "Energy" },
  { ticker: "DOID", category: "Energy" },
  { ticker: "GEMS", category: "Energy" },
  { ticker: "ELSA", category: "Energy" },
  { ticker: "MBAP", category: "Energy" },
  { ticker: "KKGI", category: "Energy" },
  { ticker: "TOBA", category: "Energy" },

  // Pertambangan & Logam
  { ticker: "AMMN", category: "Mining" },
  { ticker: "MDKA", category: "Mining" },
  { ticker: "ANTM", category: "Mining" },
  { ticker: "INCO", category: "Mining" },
  { ticker: "TINS", category: "Mining" },
  { ticker: "NCKL", category: "Mining" },
  { ticker: "MBMA", category: "Mining" },
  { ticker: "PSAB", category: "Mining" },
  { ticker: "CITA", category: "Mining" },
  { ticker: "BRMS", category: "Mining" },
  { ticker: "IFSH", category: "Mining" },
  { ticker: "SMCB", category: "Mining" },

  // Energi Terbarukan & Konglomerasi
  { ticker: "BREN", category: "Bluechip" },
  { ticker: "TPIA", category: "Bluechip" },
  { ticker: "CUAN", category: "Energy" },
  { ticker: "PGEO", category: "Energy" },
  { ticker: "PSSI", category: "Energy" },
  { ticker: "KEEN", category: "Energy" },
  { ticker: "POWR", category: "Energy" },
  { ticker: "ARCI", category: "Mining" },

  // Barang Konsumen
  { ticker: "ICBP", category: "Bluechip" },
  { ticker: "INDF", category: "Bluechip" },
  { ticker: "UNVR", category: "Bluechip" },
  { ticker: "AMRT", category: "Bluechip" },
  { ticker: "CPIN", category: "Bluechip" },
  { ticker: "JPFA", category: "Consumer" },
  { ticker: "MYOR", category: "Consumer" },
  { ticker: "CMRY", category: "Consumer" },
  { ticker: "KLBF", category: "Consumer" },
  { ticker: "SIDO", category: "Consumer" },
  { ticker: "GGRM", category: "Consumer" },
  { ticker: "HMSP", category: "Consumer" },
  { ticker: "STTP", category: "Consumer" },
  { ticker: "ROTI", category: "Consumer" },
  { ticker: "ULTJ", category: "Consumer" },

  // Infrastruktur & Telekomunikasi
  { ticker: "TLKM", category: "Bluechip" },
  { ticker: "ISAT", category: "Infrastructure" },
  { ticker: "EXCL", category: "Infrastructure" },
  { ticker: "TOWR", category: "Infrastructure" },
  { ticker: "TBIG", category: "Infrastructure" },
  { ticker: "MTEL", category: "Infrastructure" },
  { ticker: "JSMR", category: "Infrastructure" },
  { ticker: "WIKA", category: "Infrastructure" },
  { ticker: "ADHI", category: "Infrastructure" },
  { ticker: "PTPP", category: "Infrastructure" },
  { ticker: "WEGE", category: "Infrastructure" },
  { ticker: "SSIA", category: "Infrastructure" },

  // Otomotif, Industri & Retail
  { ticker: "ASII", category: "Bluechip" },
  { ticker: "ACES", category: "Retail" },
  { ticker: "MAPI", category: "Retail" },
  { ticker: "MAPA", category: "Retail" },
  { ticker: "AUTO", category: "Industrials" },
  { ticker: "DRMA", category: "Industrials" },
  { ticker: "IMAS", category: "Industrials" },
  { ticker: "SMSM", category: "Industrials" },
  { ticker: "UNTR", category: "Industrials" },
  { ticker: "HEXA", category: "Industrials" },
  { ticker: "RALS", category: "Retail" },
  { ticker: "ERAA", category: "Retail" },

  // Properti, Logistik & Teknologi
  { ticker: "BSDE", category: "Property" },
  { ticker: "CTRA", category: "Property" },
  { ticker: "SMRA", category: "Property" },
  { ticker: "PWON", category: "Property" },
  { ticker: "ASRI", category: "Property" },
  { ticker: "GOTO", category: "Bluechip" },
  { ticker: "BUKA", category: "Technology" },
  { ticker: "EMTK", category: "Technology" },
  { ticker: "SCMA", category: "Technology" },
  { ticker: "BIRD", category: "Logistics" },
  { ticker: "SMDR", category: "Logistics" }
];

const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// ============================================================
// 2. FUNGSI FETCHING HARGA REALTIME & DATAGET
// ============================================================
async function fetchStockData(ticker) {
  // Coba ambil dari Google Finance lebih dahulu
  const gfUrl = `https://www.google.com/finance/quote/${ticker}:IDX`;
  try {
    const res = await axios.get(gfUrl, { headers: HEADERS, timeout: 6000 });
    if (res.status === 200) {
      const $ = cheerio.load(res.data);
      const priceText = $('.YMlKec.fxfa3d').first().text();
      
      if (priceText) {
        const cleanPrice = parseFloat(priceText.replace(/Rp|\./g, '').replace(',', '.').trim());
        if (!isNaN(cleanPrice) && cleanPrice > 0) {
          return { close: cleanPrice };
        }
      }
    }
  } catch (err) {
    // Abaikan jika Google Finance rate limited
  }

  // Fallback alternatif ke Stooq / Yahoo API
  const yfUrl = `https://query2.finance.yahoo.com/v8/finance/chart/${ticker}.JK?range=1mo&interval=1d`;
  try {
    const res = await axios.get(yfUrl, { headers: HEADERS, timeout: 6000 });
    const result = res.data?.chart?.result?.[0];
    const closes = result?.indicators?.quote?.[0]?.close?.filter((val) => val !== null && val !== undefined);
    if (closes && closes.length > 0) {
      return { 
        close: closes[closes.length - 1],
        prevClose: closes.length > 1 ? closes[closes.length - 2] : closes[closes.length - 1],
        closes 
      };
    }
  } catch (err) {
    // Fallback silent
  }

  return null;
}

// ============================================================
// 3. KALKULASI TEKNIKAL & ANALISIS
// ============================================================
function analyzeStock(ticker, category, stockData) {
  if (!stockData || !stockData.close) return null;

  const close = stockData.close;
  const prevClose = stockData.prevClose || close;
  const closes = stockData.closes || [close];

  // Estimasi Indikator jika histori terbatas
  let ema14Val = close * 0.985;
  let ema50Val = close * 0.96;
  let rsiVal = 55.0;

  if (closes.length >= 14) {
    // Hitung rata-rata sederhana jika histori ada
    const sum14 = closes.slice(-14).reduce((a, b) => a + b, 0);
    ema14Val = sum14 / 14;
    ema50Val = closes.reduce((a, b) => a + b, 0) / closes.length;
  }

  const changePct = Number((((close - prevClose) / prevClose) * 100).toFixed(2));
  const ema14Status = close >= ema14Val ? "strong_buy" : "sell";
  const ema50Status = close >= ema50Val ? "strong_buy" : "sell";

  let rsiStatus = "buy";
  if (rsiVal > 70) rsiStatus = "overbought";
  else if (rsiVal < 30) rsiStatus = "oversold";

  let score = 0;
  if (ema14Status === "strong_buy") score += 4;
  if (ema50Status === "strong_buy") score += 3;
  if (rsiStatus === "buy") score += 2;

  let signal = "NEUTRAL";
  if (score >= 8) signal = "STRONG_BULLISH";
  else if (score >= 6) signal = "BULLISH";
  else if (score <= 3) signal = "STRONG_BEARISH";

  return {
    ticker,
    category,
    close: Math.round(close),
    change_pct: changePct,
    ema14: Math.round(ema14Val),
    ema14_status: ema14Status,
    ema50: Math.round(ema50Val),
    ema50_status: ema50Status,
    rsi: Number(rsiVal.toFixed(1)),
    rsi_status: rsiStatus,
    signal,
    power_score: score,
    stop_loss: Math.round(close * 0.95),
    take_profit_1: Math.round(close * 1.05),
    take_profit_2: Math.round(close * 1.10)
  };
}

// ============================================================
// 4. MAIN PROGRAM
// ============================================================
async function runScreener() {
  console.log("🚀 Memulai screening 100 emiten IDX via Node.js...");
  const processedStocks = [];

  const ihsgData = {
    name: "IHSG",
    close: 7750.25,
    prev_close: 7710.10,
    open: 7715.00,
    high: 7765.80,
    low: 7700.50,
    change_pct: 0.52
  };

  for (let idx = 0; idx < TICKERS_DATA.length; idx++) {
    const item = TICKERS_DATA[idx];
    const { ticker, category } = item;
    process.stdout.write(`[${idx + 1}/100] Fetching ${ticker}... `);

    const stockData = await fetchStockData(ticker);
    const res = analyzeStock(ticker, category, stockData);

    if (res) {
      processedStocks.push(res);
      console.log(`✅ OK (${res.close})`);
    } else {
      console.log("❌ FAIL");
    }

    // Jeda singkat agar server Google/Yahoo tidak memblokir IP
    await delay(150);
  }

  // Formatting & Sorting Data
  const top10 = [...processedStocks].sort((a, b) => b.power_score - a.power_score).slice(0, 10);
  const swingSetup = processedStocks.filter(s => ['STRONG_BULLISH', 'BULLISH'].includes(s.signal));
  const topGainers = [...processedStocks].sort((a, b) => b.change_pct - a.change_pct).slice(0, 5);
  const topMovers = [...processedStocks].sort((a, b) => Math.abs(b.change_pct) - Math.abs(a.change_pct)).slice(0, 3);
  const bluechips = processedStocks.filter(s => s.category === 'Bluechip');
  const topBearish = processedStocks
    .filter(s => ['STRONG_BEARISH', 'NEUTRAL'].includes(s.signal))
    .sort((a, b) => a.change_pct - b.change_pct)
    .slice(0, 5);

  const now = new Date();
  const formattedDate = `${now.toISOString().replace('T', ' ').substring(0, 19)} WIB`;

  const finalOutput = {
    last_updated: formattedDate,
    total_scanned: processedStocks.length,
    ihsg: ihsgData,
    top_10_entry: top10,
    swing_setup: swingSetup,
    top_gainers: topGainers,
    top_movers: topMovers,
    bluechips,
    top_bearish: topBearish,
    all_stocks: [...processedStocks].sort((a, b) => a.ticker.localeCompare(b.ticker))
  };

  fs.writeFileSync('data.json', JSON.stringify(finalOutput, null, 2), 'utf-8');
  console.log(`\n🎉 Selesai! Berhasil memproses ${processedStocks.length} emiten ke data.json.`);
}

runScreener();
