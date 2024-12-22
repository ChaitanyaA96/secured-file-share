import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    https: {
      key: fs.readFileSync('./certificates/fileshare.key'),
      cert: fs.readFileSync('./certificates/devserver.crt'),
    },
    proxy: {
      '/api': {
        target: 'https://127.0.0.1:8000',
        changeOrigin: true,
        secure: false, // Ignore self-signed certificate errors
      },
    },
  },
})
