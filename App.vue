<template>
  <div v-if="isFullScreenMap" class="fixed inset-0 z-[100] bg-white flex flex-col">
    <div class="p-4 bg-slate-900 text-white flex justify-between items-center shadow-lg">
      <h2 class="font-bold flex items-center gap-2">
        <i data-lucide="map"></i> 全螢幕地圖巡檢：{{ selectedAddress || '未選擇地點' }}
      </h2>
      <button @click="isFullScreenMap = false"
        class="bg-red-500 px-4 py-1.5 rounded-xl text-sm font-bold hover:bg-red-600 transition-all active:scale-95 shadow-md">
        退出全螢幕
      </button>
    </div>
    <div class="flex-1">
      <iframe v-if="selectedAddress" width="100%" height="100%" frameborder="0" style="border:0"
        :src="`https://maps.google.com/maps?q=${encodeURIComponent(selectedAddress)}&output=embed&hl=zh-TW&z=17`"
        allowfullscreen>
      </iframe>
    </div>
  </div>

  <div class="max-w-[1600px] mx-auto p-4 md:p-8" v-show="!initializing">
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-2">
          <i data-lucide="layout-dashboard" class="text-blue-600"></i>
          臺北市 1999 派工數據互動儀表板
        </h1>
        <p class="text-slate-500 mt-1 italic text-sm">
          即時數據連動 (總體：<b class="text-blue-600">{{ dbTotalCount.toLocaleString() }}</b> 筆 |
          已載入：<b class="text-indigo-600">{{ allData.length }}</b> 筆 |
          資料範圍：<b class="text-slate-700">{{ dataTimeRange }}</b>)
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button @click="loadMoreData" :disabled="loadingMore"
          class="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-xl hover:bg-blue-700 shadow-sm transition-all active:scale-95 disabled:opacity-50 font-bold">
          <i data-lucide="plus-circle" :class="{ 'animate-spin': loadingMore }"></i>
          {{ loadingMore ? '加載中...' : '查看更多' }}
        </button>
        <button @click="resetFilters"
          class="flex items-center gap-2 bg-white border px-5 py-2.5 rounded-xl hover:bg-slate-50 shadow-sm transition-all active:scale-95">
          <i data-lucide="rotate-ccw"></i> 重設所有條件
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div v-for="card in statCards" :key="card.id"
        class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
        <div class="text-slate-400 text-[10px] font-bold uppercase mb-1 flex items-center gap-1">
          <i :data-lucide="card.icon" class="w-3 h-3"></i> {{ card.label }}
        </div>
        <div class="text-slate-500 text-sm font-medium">{{ card.desc }}</div>
        <div class="text-2xl font-black text-slate-800 mt-1 truncate">{{ card.value }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <h3 class="font-bold text-slate-800 mb-6 flex items-center gap-2">
          <i data-lucide="bar-chart-3" class="text-orange-500"></i> 行政區分佈統計
        </h3>
        <div class="h-[300px]"><canvas id="districtChart"></canvas></div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center justify-between mb-6">
          <h3 class="font-bold text-slate-800 flex items-center gap-2">
            <i data-lucide="pie-chart" class="text-indigo-500"></i> 核心類別分析
          </h3>
          <div class="group relative">
            <i data-lucide="help-circle"
              class="w-5 h-5 text-slate-400 cursor-help hover:text-indigo-500 transition-colors"></i>
            <div
              class="absolute right-0 top-6 w-80 bg-slate-800 text-white text-[11px] p-4 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none shadow-2xl leading-relaxed border border-slate-700">
              <p class="font-bold mb-2 border-b border-slate-600 pb-1 text-blue-300">分類規則說明</p>
              <ul class="space-y-2">
                <li>● <b>廢棄物處理</b>：大型廢棄物、鄰里無主垃圾清運</li>
                <li>● <b>環境公害</b>：噪音舉發、污染舉發</li>
                <li>● <b>道路與路燈</b>：路燈不亮、道路坑洞、積淹水、側溝修繕</li>
                <li>● <b>交通設施</b>：號誌異常、標誌損壞、孔蓋損壞</li>
                <li>● <b>動物相關</b>：動物救援、動物虐待傷害</li>
                <li>● <b>水利設施</b>：漏水報修、下水道側溝清淤</li>
                <li>● <b>公共維護</b>：路樹處理、隧道與地下道維修</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="h-[300px]"><canvas id="coreCategoryChart"></canvas></div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div
        class="lg:col-span-2 bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden flex flex-col h-[700px]">
        <div class="p-6 border-b bg-slate-50/50 flex flex-col gap-6 flex-none">
          <div class="flex flex-col md:flex-row gap-4 justify-between items-center">
            <div class="relative flex-1 w-full max-w-2xl">
              <input v-model="searchKeyword" type="text" placeholder="搜尋內容、地址或編號..."
                class="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 shadow-sm transition-all">
              <i data-lucide="search" class="absolute left-3 top-3 w-4 h-4 text-slate-400"></i>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-sm text-slate-600 font-medium whitespace-nowrap">排序：
                <select v-model="currentSort"
                  class="border rounded-lg px-2 py-1.5 bg-white outline-none cursor-pointer">
                  <option value="time_desc">時間 (新→舊)</option>
                  <option value="time_asc">時間 (舊→新)</option>
                  <option value="district">按行政區</option>
                </select>
              </div>
              <div class="text-sm text-slate-600 font-medium whitespace-nowrap">每頁：
                <select v-model="pageSize" class="border rounded-lg px-2 py-1.5 bg-white">
                  <option :value="10">10 筆</option>
                  <option :value="20">20 筆</option>
                  <option :value="50">50 筆</option>
                </select>
              </div>
            </div>
          </div>
          <div class="flex flex-col md:flex-row items-start md:items-center gap-4 border-t pt-4 border-slate-100">
            <div class="flex items-center gap-2 text-slate-600 text-sm font-bold"><i data-lucide="calendar"
                class="w-4 h-4 text-blue-500"></i> 日期篩選：</div>
            <div class="flex items-center gap-2">
              <input v-model="startDate" type="date" :min="dateRangeLimit.min" :max="dateRangeLimit.max"
                class="border rounded-lg px-3 py-1.5 bg-white text-sm outline-none focus:ring-2 focus:ring-blue-500">
              <span class="text-slate-400">—</span>
              <input v-model="endDate" type="date" :min="dateRangeLimit.min" :max="dateRangeLimit.max"
                class="border rounded-lg px-3 py-1.5 bg-white text-sm outline-none focus:ring-2 focus:ring-blue-500">
            </div>
          </div>
        </div>

        <div class="overflow-y-auto flex-1 relative bg-white">
          <table class="w-full text-left border-separate border-spacing-0">
            <thead>
              <tr>
                <th
                  class="sticky top-0 z-20 bg-slate-100 px-8 py-4 text-slate-500 text-[11px] font-bold uppercase tracking-widest border-b border-slate-200">
                  案件資訊</th>
                <th
                  class="sticky top-0 z-20 bg-slate-100 px-8 py-4 text-slate-500 text-[11px] font-bold uppercase tracking-widest border-b border-slate-200">
                  案件地址 / 地標</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in pagedData" :key="item['案件編號']" @click="focusLocation(item['案件地址'])"
                class="hover:bg-blue-50/50 cursor-pointer transition-all group"
                :class="{ 'bg-blue-50': selectedAddress === cleanAddress(item['案件地址']) }">
                <td class="px-8 py-4">
                  <div class="text-[10px] text-indigo-500 font-bold mb-1">{{ categorizeItem(item['派工項目']) }}</div>
                  <div class="font-bold text-slate-800 text-sm group-hover:text-blue-600 transition-colors">{{
                    item['派工項目'] }}</div>
                  <div class="text-[10px] text-slate-400 mt-1 font-mono">編號: {{ item['案件編號'] }} | {{
                    formatDate(item['立案日期']) }}</div>
                </td>
                <td class="px-8 py-4 text-sm text-slate-600">
                  <div class="flex items-center gap-2">
                    <span class="bg-slate-100 px-2 py-0.5 rounded text-[10px] font-bold">{{ getDistrict(item['案件地址'])
                      }}</span>
                    <span class="break-all">{{ item['案件地址'] }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="p-6 bg-slate-50/30 border-t flex items-center justify-center gap-8 flex-none">
          <div class="flex items-center gap-2">
            <button @click="currentPage--" :disabled="currentPage === 1"
              class="p-2 border rounded-full bg-white hover:bg-slate-50 disabled:opacity-30 transition-all shadow-sm">
              <i data-lucide="chevron-left" class="w-5 h-5"></i>
            </button>
            <div class="flex items-center gap-2 px-4 text-sm font-bold">
              第 <span class="text-xl font-black text-blue-600">{{ currentPage }}</span> / {{ totalPages }} 頁
            </div>
            <button @click="currentPage++" :disabled="currentPage === totalPages"
              class="p-2 border rounded-full bg-white hover:bg-slate-50 disabled:opacity-30 transition-all shadow-sm">
              <i data-lucide="chevron-right" class="w-5 h-5"></i>
            </button>
          </div>
        </div>
      </div>

      <div id="map-section"
        class="lg:col-span-1 bg-white p-6 rounded-3xl shadow-xl border border-slate-200 scroll-mt-6 flex flex-col h-[700px] sticky top-8">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-bold text-slate-800 flex items-center gap-2">
            <i data-lucide="map-pin" class="text-red-500"></i> 地理定位導航
          </h3>
          <button v-if="selectedAddress" @click="isFullScreenMap = true"
            class="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-3 py-1.5 rounded-lg font-bold shadow-sm transition-all active:scale-95">全螢幕</button>
        </div>
        <div class="flex-1 bg-slate-50 rounded-2xl overflow-hidden relative border border-slate-100 shadow-inner">
          <iframe v-if="selectedAddress" width="100%" height="100%" frameborder="0" style="border:0"
            :src="`https://maps.google.com/maps?q=${encodeURIComponent(selectedAddress)}&output=embed&hl=zh-TW&z=17`"
            allowfullscreen>
          </iframe>
          <div v-else class="flex flex-col items-center justify-center h-full text-slate-400 p-8 text-center space-y-4">
            <div
              class="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm border border-slate-100">
              <i data-lucide="mouse-pointer-2" class="opacity-40 text-blue-500"></i>
            </div>
            <div class="space-y-1">
              <p class="text-sm font-bold text-slate-600">等待選取案件</p>
              <p class="text-xs">點擊左側列表，地圖將自動定位與對焦。</p>
            </div>
          </div>
        </div>
        <div v-if="selectedAddress" class="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-100">
          <p class="text-[10px] text-slate-400 font-bold uppercase mb-1">清洗後傳送至地圖：</p>
          <p class="text-xs font-medium text-slate-700 break-all">{{ selectedAddress }}</p>
        </div>
      </div>
    </div>
  </div>

  <div v-if="initializing"
    class="fixed inset-0 flex flex-col items-center justify-center bg-slate-50/90 backdrop-blur-md z-[200]">
    <div class="w-14 h-14 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
    <p class="text-slate-800 font-bold mt-6 tracking-widest animate-pulse">正在載入全域大數據樣本...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';

// --- 全域變數定義 ---
const CATEGORY_MAP = {
  "廢棄物處理": ["大型廢棄物", "鄰里無主垃圾"],
  "環境公害": ["噪音", "污染"],
  "道路與路燈維護": ["路燈", "坑洞", "路面積水", "道路邊坡", "側溝", "散落物", "掏空"],
  "交通設施": ["號誌", "標誌", "孔蓋"],
  "動物相關": ["動物救援", "動物虐待"],
  "水利設施與供水": ["用戶無水", "漏水", "下水道"],
  "公共設施綜合維護": ["路樹", "橋樑", "隧道", "地下道", "涵洞"]
};

const DISTRICTS = ["松山區", "大安區", "中正區", "萬華區", "大同區", "中山區", "文山區", "南港區", "內湖區", "士林區", "北投區", "信義區"];
const API_URL = 'https://data.taipei/api/v1/dataset/df579d7f-5d29-4d00-9964-1a99b26a1a1e?scope=resourceAquire';

// --- 狀態定義 ---
const initializing = ref(true);
const loadingMore = ref(false);
const allData = ref([]);
const dbTotalCount = ref(0);
const searchKeyword = ref('');
const selectedAddress = ref('');
const isFullScreenMap = ref(false);
const startDate = ref('');
const endDate = ref('');
const selectedDistrictFilter = ref('');
const selectedCategoryFilter = ref('');
const currentSort = ref('time_desc');
const currentPage = ref(1);
const pageSize = ref(10);

let charts = { dist: null, cat: null };

// --- 網路連線 ---
const delay = (ms) => new Promise(res => setTimeout(res, ms));

const robustFetch = async (targetUrl, timeout = 15000) => {
  const proxyEndpoints = [`https://corsproxy.io/?${encodeURIComponent(targetUrl)}`, `https://api.allorigins.win/get?url=${encodeURIComponent(targetUrl)}`];
  for (const endpoint of proxyEndpoints) {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), timeout);
      const res = await fetch(endpoint, { signal: controller.signal });
      clearTimeout(id);
      if (!res.ok) continue;
      const data = await res.json();
      const finalData = typeof data.contents === 'string' ? JSON.parse(data.contents) : data;
      if (finalData && finalData.result) return finalData;
    } catch (e) { console.warn("Proxy 嘗試中..."); }
  }
  throw new Error("API失敗");
};

const fetchRandomSampling = async (append = false) => {
  if (!append) { initializing.value = true; allData.value = []; }
  loadingMore.value = true;
  try {
    if (dbTotalCount.value === 0) {
      const initData = await robustFetch(`${API_URL}&limit=1`);
      dbTotalCount.value = initData.result.count;
    }
    const numJumps = 5;
    const perJump = 100;
    const collectedData = [];
    for (let i = 0; i < numJumps; i++) {
      const randomOffset = Math.floor(Math.random() * (dbTotalCount.value - perJump));
      const jumpData = await robustFetch(`${API_URL}&limit=${perJump}&offset=${randomOffset}`);
      if (jumpData.result.results) collectedData.push(...jumpData.result.results);
      await delay(300);
    }
    allData.value = append ? [...allData.value, ...collectedData] : collectedData;
  } catch (e) { console.error("加載錯誤"); } finally {
    initializing.value = false;
    loadingMore.value = false;
    nextTick(() => { if (typeof lucide !== 'undefined') lucide.createIcons(); updateCharts(); });
  }
};

const loadMoreData = () => fetchRandomSampling(true);

// --- [核心修正] 地址清洗函數 ---
const cleanAddress = (addr) => {
  if (!addr) return '';

  // 1. 全形符號規範化 (數字與標點)
  let clean = addr.replace(/[０-９]/g, (s) => String.fromCharCode(s.charCodeAt(0) - 0xfee0));
  clean = clean.replace(/–/g, '-');

  // 2. 移除最開頭的中文行政區與郵遞區號 (防止 2025110210370 案例中的 "大安區16" 現象)
  // 匹配開頭的區名 (可能黏著數字)
  clean = clean.replace(/^[\u4e00-\u9fa5]{2,3}區(?=\d|[a-zA-Z])/, '');
  clean = clean.replace(/^[\u4e00-\u9fa5]{2,3}區/, '');
  // 移除開頭郵遞區號
  clean = clean.replace(/^\d{3,5}/, '');

  // 3. 移除參考地址備註與逗號
  clean = clean.replace(/[,，\s]*(參考地址|近|靠近|對面|位於)[:：].*/g, '');
  clean = clean.replace(/[\(（].*?(參考地址|近|靠近|對面|位於).*?[\)）]/g, '');

  const isEnglish = /[a-zA-Z]/.test(clean);

  if (isEnglish) {
    // 修正：不要隨便刪除 3 位數數字 (因為那是巷弄號碼)，只刪除「末端」的 5 位數郵遞區號
    clean = clean.replace(/\b\d{5}$/, '');
    // 移除 No. ...號 中的 "號"
    clean = clean.replace(/(No\.\s*\d+.*?)號/gi, '$1');
    // 移除 Taiwan
    clean = clean.replace(/Taiwan/gi, '');

    // 智慧拆分並過濾里名 (不含數字且不含地標關鍵字的片段通常是里名)
    const parts = clean.split(/[,，]/).map(p => p.trim()).filter(Boolean);
    const seen = new Set();
    const resultParts = [];

    parts.forEach(part => {
      const lower = part.toLowerCase();
      if (lower === 'taipei city' || lower === 'taipei') {
        if (seen.has('taipei')) return;
        seen.add('taipei');
      }
      const isAddressKey = /(Rd|Ln|Aly|Sec|No|Dist|City|Street|Road|Lane|Alley|District)/i.test(part);
      const hasNumber = /\d/.test(part);
      if (isAddressKey || hasNumber) {
        resultParts.push(part);
      }
    });
    clean = resultParts.join(', ');
  } else {
    // 中文清洗邏輯
    clean = clean.replace(/(台灣|臺北市|台北市)/g, '');
    clean = clean.replace(/(\d+鄰)|(第\d+鄰)|[\u4e00-\u9fa5]+里/g, '');
    const floorPattern = /([0-9一二三四五六七八九十]+[樓層Ff])|(地下[0-9一二三四五六七八九十]+[樓層Ff])/g;
    clean = clean.replace(floorPattern, '');
  }

  return clean.trim();
};

const focusLocation = (addr) => {
  selectedAddress.value = cleanAddress(addr);
  nextTick(() => {
    const mapEl = document.getElementById('map-section');
    if (mapEl) mapEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
};

// --- 計算屬性 ---
const statCards = computed(() => [
  { id: 1, label: 'Analysis Hits', desc: '篩選命中筆數', value: filteredData.value.length.toLocaleString(), icon: 'target' },
  { id: 2, label: 'Data Hotspot', desc: '最高頻行政區', value: getTopDistrict(), icon: 'map-pin' },
  { id: 3, label: 'Main Category', desc: '主導案件類型', value: getTopCategory(), icon: 'pie-chart' }
]);

const dataTimeRange = computed(() => {
  if (allData.value.length === 0) return '---';
  const dates = allData.value.map(i => String(i['立案日期'])).filter(d => d.length === 8).sort();
  if (dates.length === 0) return '分析中';
  return `${dates[0].substring(0, 4)}/${dates[0].substring(4, 6)} ~ ${dates[dates.length - 1].substring(0, 4)}/${dates[dates.length - 1].substring(4, 6)}`;
});

const filteredData = computed(() => {
  let data = [...allData.value];
  const kw = searchKeyword.value.trim().toLowerCase();
  if (kw) data = data.filter(i => (i['案件地址'] + i['派工項目'] + i['案件編號']).toLowerCase().includes(kw));
  if (selectedDistrictFilter.value) data = data.filter(i => (i['案件地址'] || '').includes(selectedDistrictFilter.value));
  if (selectedCategoryFilter.value) data = data.filter(i => categorizeItem(i['派工項目']) === selectedCategoryFilter.value);
  if (startDate.value || endDate.value) {
    const s = startDate.value ? startDate.value.replace(/-/g, '') : '00000000';
    const e = endDate.value ? endDate.value.replace(/-/g, '') : '99999999';
    data = data.filter(i => String(i['立案日期']) >= s && String(i['立案日期']) <= e);
  }
  data.sort((a, b) => {
    const tA = (a['立案日期'] || '') + (a['立案時間'] || '');
    const tB = (b['立案日期'] || '') + (b['立案時間'] || '');
    if (currentSort.value === 'time_desc') return tB.localeCompare(tA);
    if (currentSort.value === 'time_asc') return tA.localeCompare(tB);
    if (currentSort.value === 'district') return (a['案件地址'] || '').localeCompare(b['案件地址'] || '', 'zh-TW');
    return 0;
  });
  return data;
});

const dateRangeLimit = computed(() => {
  if (allData.value.length === 0) return { min: '', max: '' };
  const ds = allData.value.map(i => String(i['立案日期'])).filter(d => d.length === 8).sort();
  const toI = (s) => `${s.substring(0, 4)}-${s.substring(4, 6)}-${s.substring(6, 8)}`;
  return { min: toI(ds[0]), max: toI(ds[ds.length - 1]) };
});

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value) || 1);
const pagedData = computed(() => filteredData.value.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value));

const categorizeItem = (item) => {
  for (const [cat, ks] of Object.entries(CATEGORY_MAP)) { if (ks.some(k => item.includes(k))) return cat; }
  return "其他";
};

const getDistrict = (addr) => (addr.match(/(.{2,3}區)/) || ['', '其他'])[1];
const getTopDistrict = () => {
  if (filteredData.value.length === 0) return '--';
  const c = {}; filteredData.value.forEach(i => { const d = getDistrict(i['案件地址']); c[d] = (c[d] || 0) + 1; });
  const sorted = Object.entries(c).sort((a, b) => b[1] - a[1]);
  return sorted.length ? sorted[0][0] : '--';
};
const getTopCategory = () => {
  if (filteredData.value.length === 0) return '--';
  const c = {}; filteredData.value.forEach(i => { const t = categorizeItem(i['派工項目']); c[t] = (c[t] || 0) + 1; });
  const sorted = Object.entries(c).sort((a, b) => b[1] - a[1]);
  return sorted.length ? sorted[0][0] : '--';
};

const formatDate = (d) => String(d).replace(/(\d{4})(\d{2})(\d{2})/, '$1/$2/$3');

const updateCharts = () => {
  const dC = {}; const cC = {}; Object.keys(CATEGORY_MAP).forEach(k => cC[k] = 0); cC["其他"] = 0;
  filteredData.value.forEach(i => { const d = getDistrict(i['案件地址']); dC[d] = (dC[d] || 0) + 1; const c = categorizeItem(i['派工項目']); cC[c] = (cC[c] || 0) + 1; });

  if (document.getElementById('districtChart')) {
    if (charts.dist) charts.dist.destroy();
    charts.dist = new Chart(document.getElementById('districtChart'), { type: 'bar', data: { labels: DISTRICTS, datasets: [{ label: '案件量', data: DISTRICTS.map(d => dC[d] || 0), backgroundColor: '#3b82f6', borderRadius: 4 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, onClick: (e, el) => { if (el.length > 0) selectedDistrictFilter.value = DISTRICTS[el[0].index]; } } });
  }
  if (document.getElementById('coreCategoryChart')) {
    if (charts.cat) charts.cat.destroy();
    const l = Object.keys(cC);
    charts.cat = new Chart(document.getElementById('coreCategoryChart'), { type: 'doughnut', data: { labels: l, datasets: [{ data: l.map(x => cC[x]), backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#94a3b8'], borderWidth: 0 }] }, options: { responsive: true, maintainAspectRatio: false, cutout: '70%', onClick: (e, el) => { if (el.length > 0) selectedCategoryFilter.value = l[el[0].index]; } } });
  }
};

const resetFilters = () => { searchKeyword.value = ''; selectedDistrictFilter.value = ''; selectedCategoryFilter.value = ''; selectedAddress.value = ''; startDate.value = ''; endDate.value = ''; currentPage.value = 1; };

watch([filteredData, pageSize, currentSort, selectedDistrictFilter, selectedCategoryFilter, startDate, endDate], () => { currentPage.value = 1; nextTick(() => updateCharts()); });

onMounted(() => fetchRandomSampling(false));
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important;
}

input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.scroll-mt-6 {
  scroll-margin-top: 1.5rem;
}

th.sticky {
  background-color: #f1f5f9;
  box-shadow: 0 1px 0 #e2e8f0;
}

@media (min-width: 1024px) {
  .sticky.top-8 {
    position: sticky;
    top: 2rem;
  }
}
</style>
