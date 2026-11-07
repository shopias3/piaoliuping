import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    // H5 开发模式代理后端；App 打包时在 api/request.js 配置完整服务器地址
    // 说明：本机 8000 端口被其他应用占用，后端使用 8010
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8010',
        changeOrigin: true
      }
    }
  }
})
