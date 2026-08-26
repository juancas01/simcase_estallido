import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// El servidor de desarrollo proxya /api al motor, para poder trabajar en la
// interfaz con `npm run dev` sin construir nada.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
  },
})
