// Caminhos do projeto e instalação automática das dependências
// (backend em Python/venv e frontend em npm).
// Sem dependências externas: funciona em Linux, macOS e Windows com Node 18+.

import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export const isWindows = process.platform === 'win32'
export const rootDir = resolve(dirname(fileURLToPath(import.meta.url)), '..')
export const backendDir = join(rootDir, 'backend')
export const frontendDir = join(rootDir, 'frontend')
export const venvDir = join(rootDir, '.venv')
export const venvPython = isWindows
  ? join(venvDir, 'Scripts', 'python.exe')
  : join(venvDir, 'bin', 'python')
export const npmCommand = isWindows ? 'npm.cmd' : 'npm'

function findSystemPython() {
  const candidates = isWindows
    ? [['py', ['-3']], ['python', []], ['python3', []]]
    : [['python3', []], ['python', []]]

  for (const [command, prefix] of candidates) {
    const result = spawnSync(command, [...prefix, '--version'], {
      stdio: 'ignore',
      shell: isWindows,
    })
    if (result.status === 0) return { command, prefix }
  }
  return null
}

export function ensureBackendDeps() {
  if (!existsSync(venvPython)) {
    const python = findSystemPython()
    if (!python) {
      console.error('[setup] Python 3 não encontrado. Instale o Python 3.10+ e tente de novo.')
      return false
    }

    console.log('[setup] Criando ambiente virtual Python em .venv ...')
    const criado = spawnSync(python.command, [...python.prefix, '-m', 'venv', venvDir], {
      stdio: 'inherit',
      shell: isWindows,
    })
    if (criado.status !== 0 || !existsSync(venvPython)) {
      console.error('[setup] Não foi possível criar o ambiente virtual.')
      console.error('        No Linux (Debian/Ubuntu) talvez seja preciso: sudo apt install python3-venv')
      return false
    }
  }

  // Reinstala apenas quando o requirements.txt muda (cache pelo hash do arquivo).
  const requirements = readFileSync(join(backendDir, 'requirements.txt'))
  const hash = createHash('sha256').update(requirements).digest('hex')
  const stamp = join(venvDir, '.requirements.sha256')
  if (existsSync(stamp) && readFileSync(stamp, 'utf8').trim() === hash) return true

  console.log('[setup] Instalando dependências do backend (pip install -r backend/requirements.txt) ...')
  const instalado = spawnSync(
    venvPython,
    ['-m', 'pip', 'install', '--disable-pip-version-check', '-r', 'requirements.txt'],
    { cwd: backendDir, stdio: 'inherit' },
  )
  if (instalado.status !== 0) {
    console.error('[setup] Falha ao instalar as dependências do backend.')
    return false
  }
  writeFileSync(stamp, hash)
  return true
}

export function ensureFrontendDeps() {
  const viteBin = join(frontendDir, 'node_modules', '.bin', isWindows ? 'vite.cmd' : 'vite')
  if (existsSync(viteBin)) return true

  console.log('[setup] Instalando dependências do frontend (npm install em frontend/) ...')
  const instalado = spawnSync(npmCommand, ['install'], {
    cwd: frontendDir,
    stdio: 'inherit',
    shell: isWindows,
  })
  if (instalado.status !== 0 || !existsSync(viteBin)) {
    console.error('[setup] Falha ao instalar as dependências do frontend.')
    return false
  }
  return true
}
