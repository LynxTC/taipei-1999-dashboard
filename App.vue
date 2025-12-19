<template>
  <div class="max-w-7xl mx-auto p-4 md:p-8" v-show="!initializing">
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-2">
          <i data-lucide="map" class="text-blue-600"></i>
          臺北市 1999 派工數據儀表板
        </h1>
        <p class="text-slate-500 mt-1 italic">
          即時數據連動 (總體資料量：<b class="text-blue-600">{{ dbTotalCount.toLocaleString() }}</b> 筆)
        </p>
      </div>
      <button @click="resetFilters" class="flex items-center gap-2 bg-white border px-6 py-2.5 rounded-xl hover:bg-slate-50 shadow-sm transition-all active:scale-95">
        <i data-lucide="rotate-ccw"></i> 重設所有條件
      </button>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div v-for="card in statCards" :key="card.id" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div class="text-slate-400 text-[10px] font-bold uppercase mb-1">{{ card.label }}</div>
        <div class="text-slate-500 text-sm font-medium">{{ card.desc }}</div>
        <div class="text-3xl font-black text-slate-800 mt-1">{{ card.value }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
      <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <h3 class="font-bold text-slate-800 mb-6 flex items-center gap-2">
          <i data-lucide="bar-chart-3" class="text-orange-500"></i> 行政區分佈統計
        </h3>
        <div class="h-[350px]">
          <canvas id="districtChart"></canvas>
        </div>
      </div>
      <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <h3 class="font-bold text-slate-800 mb-6 flex items-center gap-2">
          <i data-lucide="pie-chart" class="text-indigo-500"></i> 案件類型分析
        </h3>
        <div class="h-[350px]">
          <canvas id="categoryChart"></canvas>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b bg-slate-50/50">
        <div class="relative max-w-2xl mx-auto">
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="搜尋編號、地址、派工內容..." 
            class="w-full pl-6 pr-4 py-4 bg-white border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 text-lg shadow-sm"
          >
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-100/50 text-slate-500 text-[11px] font-bold uppercase tracking-widest">
            <tr>
              <th class="px-8 py-5">案件編號</th>
              <th class="px-8 py-5">派工項目</th>
              <th class="px-8 py-5">案件地址</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 text-slate-700">
            <tr v-for="item in filteredData" :key="item['案件編號']" class="hover:bg-blue-50/40 transition-all cursor-pointer">
              <td class="px-8 py-4 font-mono text-slate-400 text-xs">{{ item['案件編號'] }}</td>
              <td class="px-8 py-4 font-bold text-slate-800 text-sm">{{ item['派工項目'] }}</td>
              <td class="px-8 py-4 text-slate-500 text-sm">
                <span class="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-[10px] font-bold mr-2">{{ getDistrict(item['案件地址']) }}</span>
                {{ item['案件地址'] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="filteredData.length === 0" class="p-20 text-center text-slate-400">
        查無符合條件之數據
      </div>
    </div>
  </div>

  <div v-if="initializing" class="fixed inset-0 flex flex-col items-center justify-center bg-slate-50/90 backdrop-blur-md">
    <div class="w-14 h-14 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
    <p class="text-slate-800 font-bold mt-6 tracking-widest animate-pulse">正在同步市府大數據通道...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';

// 狀態與資料
const dbTotalCount = ref(0);
const allData = ref([]);
const searchKeyword = ref('');
const initializing = ref(true);
let charts = { dist: null, cat: null };

const API_URL = 'https://data.taipei/api/v1/dataset/95e364a7-4fc6-4f02-b248-876a7a76333a?scope=resourceAquire';
const DISTRICTS = ["松山區", "大安區", "中正區", "萬華區", "大同區", "中山區", "文山區", "南港區", "內湖區", "士林區", "北投區", "信義區"];

// 計算篩選
const filteredData = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase();
  if (!kw) return allData.value;
  return allData.value.filter(i => 
    (i['案件地址'] || '').toLowerCase().includes(kw) || 
    (i['派工項目'] || '').toLowerCase().includes(kw) ||
    (i['案件編號'] || '').toLowerCase().includes(kw)
  );
});

// 統計卡片內容
const statCards = computed(() => [
  { id: 1, label: 'Analysis Hits', desc: '篩選命中筆數', value: filteredData.value.length.toLocaleString() },
  { id: 2, label: 'Data Hotspot', desc: '目前最高頻行政區', value: getTopDistrict() },
  { id: 3, label: 'System Status', desc: '系統連線狀態', value: '動態同步中' }
]);

// 獲取行政區
const getDistrict = (addr) => {
  const match = (addr || '').match(/(.{2}區)/);
  return match ? match[1] : '其他';
};

// 獲取熱點
const getTopDistrict = () => {
  if (filteredData.value.length === 0) return '--';
  const counts = {};
  filteredData.value.forEach(i => {
    const d = getDistrict(i['案件地址']);
    counts[d] = (counts[d] || 0) + 1;
  });
  return Object.entries(counts).sort((a,b) => b[1]-a[1])[0][0];
};

// 初始化圖表
const updateCharts = () => {
  const distCounts = {};
  const catCounts = {};
  
  filteredData.value.forEach(i => {
    const d = getDistrict(i['案件地址']);
    distCounts[d] = (distCounts[d] || 0) + 1;
    const p = i['派工項目'] || '其他';
    catCounts[p] = (catCounts[p] || 0) + 1;
  });

  // 行政區圖
  const dCtx = document.getElementById('districtChart');
  if (dCtx) {
    if (charts.dist) charts.dist.destroy();
    charts.dist = new Chart(dCtx, {
      type: 'bar',
      data: {
        labels: DISTRICTS,
        datasets: [{ label: '案件量', data: DISTRICTS.map(d => distCounts[d] || 0), backgroundColor: '#3b82f6', borderRadius: 6 }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
  }

  // 類別圓餅圖
  const cCtx = document.getElementById('categoryChart');
  if (cCtx) {
    if (charts.cat) charts.cat.destroy();
    const topCats = Object.entries(catCounts).sort((a,b) => b[1]-a[1]).slice(0, 5);
    charts.cat = new Chart(cCtx, {
      type: 'doughnut',
      data: {
        labels: topCats.map(x => x[0]),
        datasets: [{ data: topCats.map(x => x[1]), backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'], borderWidth: 0 }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '70%' }
    });
  }
};

// 監聽數據變化並重繪圖表
watch(filteredData, () => {
  nextTick(() => updateCharts());
});

// 初始化系統
const initSystem = async () => {
  try {
    const res = await fetch(`${API_URL}&limit=1000`);
    const json = await res.json();
    if (json.result) {
      allData.value = json.result.results;
      // 這裡動態抓取 count
      dbTotalCount.value = json.result.count || 0;
    }
  } catch (e) {
    console.error("API Error");
  } finally {
    initializing.value = false;
    // 渲染 Lucide 圖示
    setTimeout(() => {
        lucide.createIcons();
        updateCharts();
    }, 100);
  }
};

const resetFilters = () => {
  searchKeyword.value = '';
};

onMounted(initSystem);
</script>

<style scoped>
/* 將原本的 CSS 搬移至此 */
canvas { width: 100% !important; height: 100% !important; }
</style>
