import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: './',
  root: 'src',
  publicDir: '../public',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/index.html'),
        composer: resolve(__dirname, 'src/composer.html'),
        overlay: resolve(__dirname, 'src/overlay.html'),
        dock: resolve(__dirname, 'src/dock.html')
      }
    }
  },
  server: {
    port: 5173,
    strictPort: true
  }
});
