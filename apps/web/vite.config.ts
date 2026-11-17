import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

export default defineConfig({
  plugins: [react()],
  appType: 'mpa',
  build: { rollupOptions: { input: { main: resolve(__dirname, 'index.html'), monitor: resolve(__dirname, 'monitor.html') } } },
  server: {
    host: '127.0.0.1', port: 5173, strictPort: true,
    proxy: {
      '/api/v1': 'http://127.0.0.1:8000',
      '/health/live': 'http://127.0.0.1:8000',
    },
  },
});
