// Roda o backend Flask usando o Python do ambiente virtual (.venv).
//   node scripts/backend.mjs        -> servidor de desenvolvimento em http://localhost:5000
//   node scripts/backend.mjs test   -> testes do backend (pytest)
//
// Uso via npm: npm run dev:backend | npm test

import { spawn } from 'node:child_process'
import { backendDir, ensureBackendDeps, venvPython } from './deps.mjs'

const modo = process.argv[2] ?? 'run'

if (!ensureBackendDeps()) process.exit(1)

const args = modo === 'test' ? ['-m', 'pytest', 'testes/', '-v'] : ['principal.py']
const child = spawn(venvPython, args, { cwd: backendDir, stdio: 'inherit' })

for (const sinal of ['SIGINT', 'SIGTERM']) {
  process.on(sinal, () => child.kill(sinal))
}

child.on('exit', (code) => process.exit(code ?? 0))
