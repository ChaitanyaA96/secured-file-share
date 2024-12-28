import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load environment variables
  const environment = process.env.ENVIRONMENT || 'dev'

  // Determine if it's in development mode
  const isDev = environment === 'dev'

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: 'https://backend:8000', // Use HTTP for the backend
          changeOrigin: true,
          secure: false, // Do not enforce SSL validation
        },
      },
    },
  }
})
