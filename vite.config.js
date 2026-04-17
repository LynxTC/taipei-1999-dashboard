import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    // 自動判斷是否在 GitHub Pages 環境，若是則補上儲存庫名稱為子路徑
    base: process.env.NODE_ENV === 'production' ? '/taipei-1999-dashboard/' : '/',
})