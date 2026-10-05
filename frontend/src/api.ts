export type EstadoPartida = {
  id: string
  fen: string
  turno: 'brancas' | 'pretas'
  xeque_mate: boolean
}

export type JogadaServidor = {
  origem: string
  destino: string
  peca: string
  captura: string | null
  e_roque: boolean
  e_en_passant: boolean
  promocao: string | null
}

type RespostaJogada = { jogada: JogadaServidor; estado: EstadoPartida }

async function requisitar<T>(caminho: string, init?: RequestInit): Promise<T> {
  const resposta = await fetch(`/api${caminho}`, init)
  const corpo = await resposta.json().catch(() => null)
  if (!resposta.ok) throw new Error(corpo?.erro ?? `Erro ${resposta.status}`)
  return corpo as T
}

function enviar(corpo: unknown): RequestInit {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  }
}

export function novaPartida() {
  return requisitar<EstadoPartida>('/partida/nova', enviar({}))
}

export function jogar(id: string, origem: string, destino: string, promocao?: string) {
  return requisitar<RespostaJogada>(`/partida/${id}/jogada`, enviar({ origem, destino, promocao }))
}

export function desfazer(id: string) {
  return requisitar<RespostaJogada>(`/partida/${id}/desfazer`, enviar({}))
}

export function movimentos(id: string, casa: string) {
  return requisitar<{ casa: string; movimentos: JogadaServidor[] }>(
    `/partida/${id}/jogadas/${casa}`,
  )
}
