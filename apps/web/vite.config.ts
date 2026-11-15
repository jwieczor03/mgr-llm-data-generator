import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  appType: 'mpa',
  server: {
    host: '127.0.0.1', port: 5173, strictPort: true,
    proxy: {
      '/api/v1': 'http://127.0.0.1:8000',
      '/health/live': 'http://127.0.0.1:8000',
    },
  },
});
