/// <reference types="vitest/config" />
import { existsSync, readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// HTTPS local: usa o certificado self-signed montado em /certs (ver `make certs`).
// Cai para HTTP automaticamente quando os certificados não existem (build/testes).
function httpsConfig() {
  const certFile = process.env.SSL_CERT_FILE ?? '/certs/cert.pem'
  const keyFile = process.env.SSL_KEY_FILE ?? '/certs/key.pem'
  if (existsSync(certFile) && existsSync(keyFile)) {
    return { cert: readFileSync(certFile), key: readFileSync(keyFile) }
  }
  return undefined
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    https: httpsConfig(),
    // Evita reloads desnecessários ao observar artefatos gerados.
    watch: { ignored: ['**/coverage/**', '**/htmlcov/**', '**/.venv/**'] },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/main.tsx',
        'src/App.tsx',
        'src/theme/**',
        'src/types/**',
        'src/lib/api.ts',
        'src/**/*.d.ts',
        'src/**/*.test.{ts,tsx}',
        'src/test/**',
        // UI apresentacional do WhatsApp (cobertura focada na lógica de auth).
        'src/features/**',
        'src/pages/HomePage.tsx',
      ],
      thresholds: {
        statements: 95,
        branches: 85,
        functions: 95,
        lines: 95,
      },
    },
  },
})
