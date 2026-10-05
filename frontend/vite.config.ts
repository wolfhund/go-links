import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = process.env.GOLINKS_API_URL ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Same-origin /api calls in dev: no CORS configuration needed on the API.
    proxy: { '/api': API_TARGET },
  },
})
