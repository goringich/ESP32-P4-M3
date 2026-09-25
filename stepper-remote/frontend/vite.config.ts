import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.dirname(fileURLToPath(import.meta.url));
const host = process.env.STEPPER_REMOTE_HOST?.trim() || '127.0.0.1';
const loopbackHosts = new Set(['localhost', '127.0.0.1', '::1', '[::1]']);

if (!loopbackHosts.has(host) && process.env.STEPPER_REMOTE_ALLOW_REMOTE !== '1') {
  throw new Error(
    'remote Vite bind refused: set STEPPER_REMOTE_ALLOW_REMOTE=1 explicitly'
  );
}

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(rootDir, 'index.html'),
        pad: path.resolve(rootDir, 'pad.html'),
      },
    },
  },
  server: {
    host,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3001',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    host,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3001',
        changeOrigin: true,
      },
    },
  },
});
