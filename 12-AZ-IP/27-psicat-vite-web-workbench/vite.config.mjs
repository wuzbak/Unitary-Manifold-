import { defineConfig } from 'vite';

export default defineConfig({
  root: 'ui',
  base: './',
  server: {
    host: '127.0.0.1',
    port: 5179,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:8327',
    },
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
});
