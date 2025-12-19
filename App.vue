<template>
  <div class="max-w-7xl mx-auto p-4 md:p-8" v-if="!initializing">
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-2">
          <span class="text-blue-600">📊</span> 臺北市 1999 數據分析
        </h1>
        <p class="text-slate-500 mt-1 italic">
          即時數據連動 (總體資料量：<b class="text-blue-600">{{ dbTotalCount.toLocaleString() }}</b> 筆)
        </p>
      </div>
      <button @click="resetFilters" class="bg-white border px-6 py-2 rounded-xl shadow-sm hover:bg-slate-50 transition-all">
        重設分析條件
      </button>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div v-for="card in statCards" :key="card.id" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">{{ card.label }}</div>
        <div class="text-slate-500 text-sm font-medium">{{ card.desc }}</div>
        <div class="text-3xl font-black text-slate-800 mt-1">{{ card.value }}</div>
      </div>
    </div>

    <div class="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden">
        <div class="p-8 border-b bg-slate-50/50">
            <input 
                v-model="searchKeyword" 
                type="text" 
                placeholder="搜尋案件編號、地址..." 
                class="w-full px-6 py-4 rounded-2xl border focus:ring-2 focus:ring-blue-500 outline-none text-lg"
            >
        </div>
        <table class="w-full text-left">
            <thead class="bg-slate-100/50 text-[11px] font-bold uppercase text-slate-500">
                <tr>
                    <th class="px-8 py-5">案件編號</th>
                    <th class="px-8 py-5">派工項目</th>
                    <th class="px-8 py-5">地址</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="item in filteredData" :key="item['案件編號']" class="border-b hover:bg-blue-50/40 transition-all cursor-pointer">
                    <td class="px-8 py-4 font-mono text-slate-400 text-xs">{{ item['案件編號'] }}</td>
                    <td class="px-8 py-4 font-bold text-slate-800 text-sm">{{ item['派工項目'] }}</td>
                    <td class="px-8 py-4 text-slate-500 text-sm">{{ item['案件地址'] }}</td>
                </tr>
            </tbody>
        </table>
    </div>
  </div>

  <div v-else class="fixed inset-0 flex flex-col items-center justify-center bg-white">
    <div class="w-12 h-12 border-4 border-slate-100 border-t-blue-600 rounded-full animate-spin"></div>
    <p class="mt-4 font-bold text-slate-800 animate-pulse">系統初始化中...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';

// 狀態管理
const dbTotalCount = ref(0);
const allSampleData = ref([]);
const searchKeyword = ref('');
const initializing = ref(true);

const API_URL = 'https://data.taipei/api/v1/dataset/95e364a7-4fc6-4f02-b248-876a7a76333a?scope=resourceAquire';

// 動態計算篩選結果
const filteredData = computed(() => {
    if (!searchKeyword.value) return allSampleData.value;
    const kw = searchKeyword.value.toLowerCase();
    return allSampleData.value.filter(i => 
        (i['案件地址'] || '').toLowerCase().includes(kw) || 
        (i['案件編號'] || '').toLowerCase().includes(kw) ||
        (i['派工項目'] || '').toLowerCase().includes(kw)
    );
});

// 統計數值
const statCards = computed(() => [
    { id: 1, label: 'Filter Stats', desc: '篩選命中數', value: filteredData.value.length },
    { id: 2, label: 'Sample Size', desc: '快取樣本筆數', value: allSampleData.value.length },
    { id: 3, label: 'System Status', desc: '連線狀態', value: '加密連線' }
]);

// 抓取資料
const initSystem = async () => {
    try {
        const response = await fetch(`${API_URL}&limit=1000`);
        const data = await response.json();
        if (data && data.result) {
            allSampleData.value = data.result.results;
            // 關鍵修改：從 API 抓取動態 count
            dbTotalCount.value = data.result.count || 0;
        }
    } catch (e) {
        console.error("Connection failed.");
    } finally {
        initializing.value = false;
    }
};

const resetFilters = () => {
    searchKeyword.value = '';
};

onMounted(initSystem);
</script>

<style scoped>
/* 這裡可以放置 App.vue 專用的 CSS */
body {
    background-color: #f8fafc;
}
</style>
