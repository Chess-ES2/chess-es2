// Instala tudo que o projeto precisa para rodar (backend + frontend).
// Uso: npm run setup

import { ensureBackendDeps, ensureFrontendDeps } from './deps.mjs'

if (!ensureBackendDeps() || !ensureFrontendDeps()) process.exit(1)

console.log('[setup] Tudo pronto. Rode "npm run dev" para subir frontend + backend.')
