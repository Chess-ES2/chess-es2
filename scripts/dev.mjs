// Sobe backend (Flask, porta 5000) e frontend (Vite, porta 5173) juntos.
// O frontend fica conectado ao backend pelo proxy do Vite: /api/* -> http://localhost:5000/*
//
// Uso: npm run dev

import { spawn, spawnSync } from 'node:child_process'
import { networkInterfaces } from 'node:os'
import {
  backendDir,
  ensureBackendDeps,
  ensureFrontendDeps,
  frontendDir,
  isWindows,
  npmCommand,
  venvPython,
} from './deps.mjs'

if (!ensureBackendDeps() || !ensureFrontendDeps()) process.exit(1)

const children = []
let encerrando = false

function start(nome, comando, args, opcoes) {
  const child = spawn(comando, args, { stdio: 'inherit', ...opcoes })
  children.push({ nome, child })
  child.on('exit', (code, signal) => {
    if (encerrando) return
    console.error(`\n[dev] ${nome} encerrou (${code ?? signal}). Encerrando os demais processos...`)
    shutdown(code ?? 1)
  })
  return child
}

// Endereços IPv4 da rede local (ignora loopback e pontes de containers).
function enderecosDaRedeLocal() {
  const ignorar = /^(lo|br-|docker|veth|virbr)/i
  const enderecos = []
  for (const [nome, infos] of Object.entries(networkInterfaces())) {
    if (ignorar.test(nome)) continue
    for (const info of infos ?? []) {
      if (info.family === 'IPv4' && !info.internal) enderecos.push({ nome, ip: info.address })
    }
  }
  return enderecos
}

function shutdown(code = 0) {
  if (encerrando) return
  encerrando = true
  for (const { child } of children) {
    if (!child.pid || child.exitCode !== null) continue
    if (isWindows) {
      // No Windows é preciso matar a árvore de processos (npm -> node -> vite etc.).
      spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' })
    } else {
      child.kill('SIGTERM')
    }
  }
  setTimeout(() => process.exit(code), 300)
}

for (const sinal of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
  process.on(sinal, () => shutdown(0))
}

console.log('[dev] Backend  -> http://localhost:5000')
console.log('[dev] Frontend -> http://localhost:5173  (chamadas em /api vão para o backend)')
const enderecos = enderecosDaRedeLocal()
if (enderecos.length > 0) {
  console.log('[dev] Nos IPs locais da máquina:')
  for (const { nome, ip } of enderecos) {
    console.log(`[dev]   frontend http://${ip}:5173  |  backend http://${ip}:5000  (${nome})`)
  }
}
console.log('[dev] Ctrl+C encerra os dois.\n')

start('backend', venvPython, ['principal.py'], { cwd: backendDir })
start('frontend', npmCommand, ['run', 'dev'], { cwd: frontendDir, shell: isWindows })
