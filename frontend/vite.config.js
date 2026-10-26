import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins:[react()], server:{proxy:{'/api':process.env.REVENUEOPS_API_URL || 'http://127.0.0.1:5050','/health':process.env.REVENUEOPS_API_URL || 'http://127.0.0.1:5050'}}, test:{environment:'jsdom',setupFiles:['./tests/setup.js'], exclude:['tests/e2e/**','node_modules/**']} })
