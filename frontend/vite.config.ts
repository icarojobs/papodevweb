/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
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
