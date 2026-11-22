import type { JogadaServidor } from '../../api'
import type { Color, PieceType, Square } from './types'

type Piece = { color: Color; type: PieceType }
type Board = Partial<Record<Square, Piece>>

const FILES = 'abcdefgh'
const LETRA_PECA: Record<PieceType, string> = {
  p: '',
  n: 'N',
  b: 'B',
  r: 'R',
  q: 'Q',
  k: 'K',
}

function coords(sq: Square): [number, number] {
  return [FILES.indexOf(sq[0]), Number(sq[1]) - 1]
}

function sqAt(col: number, rank: number): Square | null {
  if (col < 0 || col > 7 || rank < 0 || rank > 7) return null
  return `${FILES[col]}${rank + 1}` as Square
}

function caminhoLivre(board: Board, c1: number, r1: number, c2: number, r2: number): boolean {
  const dc = Math.sign(c2 - c1)
  const dr = Math.sign(r2 - r1)
  let c = c1 + dc
  let r = r1 + dr
  while (c !== c2 || r !== r2) {
    const casa = sqAt(c, r)
    if (!casa || board[casa]) return false
    c += dc
    r += dr
  }
  return true
}

function pecaAlcança(board: Board, origem: Square, destino: Square, piece: Piece): boolean {
  const [c1, r1] = coords(origem)
  const [c2, r2] = coords(destino)
  const dc = Math.abs(c2 - c1)
  const dr = Math.abs(r2 - r1)

  switch (piece.type) {
    case 'n':
      return (dc === 1 && dr === 2) || (dc === 2 && dr === 1)
    case 'b':
      return dc === dr && dc > 0 && caminhoLivre(board, c1, r1, c2, r2)
    case 'r':
      return (dc === 0 || dr === 0) && (dc + dr > 0) && caminhoLivre(board, c1, r1, c2, r2)
    case 'q':
      return (dc === dr || dc === 0 || dr === 0) && (dc + dr > 0) && caminhoLivre(board, c1, r1, c2, r2)
    case 'k':
      return dc <= 1 && dr <= 1 && (dc + dr > 0)
    case 'p': {
      const dir = piece.color === 'w' ? 1 : -1
      return r2 - r1 === dir && dc === 1
    }
  }
}

function reiEmXeque(board: Board, corRei: Color): boolean {
  let casaRei: Square | null = null
  for (const [casa, peca] of Object.entries(board) as Array<[Square, Piece]>) {
    if (peca.color === corRei && peca.type === 'k') {
      casaRei = casa
      break
    }
  }
  if (!casaRei) return false

  for (const [casa, peca] of Object.entries(board) as Array<[Square, Piece]>) {
    if (peca.color !== corRei && pecaAlcança(board, casa, casaRei, peca)) {
      return true
    }
  }
  return false
}

export function formatarSAN(
  jogada: JogadaServidor,
  boardAntes: Board,
  boardDepois: Board,
  xequeMate: boolean,
): string {
  const origem = jogada.origem as Square
  const destino = jogada.destino as Square
  const corMovida: Color = jogada.peca === jogada.peca.toUpperCase() ? 'w' : 'b'
  const tipo = jogada.peca.toLowerCase() as PieceType
  const corAdv: Color = corMovida === 'w' ? 'b' : 'w'

  let base: string
  if (jogada.e_roque) {
    base = destino[0] === 'g' ? 'O-O' : 'O-O-O'
  } else {
    const captura = jogada.captura !== null || jogada.e_en_passant
    let desambiguacao = ''

    if (tipo === 'p') {
      if (captura) desambiguacao = origem[0]
    } else if (tipo !== 'k') {
      const outras = (Object.entries(boardAntes) as Array<[Square, Piece]>).filter(
        ([casa, p]) =>
          casa !== origem &&
          p.color === corMovida &&
          p.type === tipo &&
          pecaAlcança(boardAntes, casa, destino, p),
      )
      if (outras.length > 0) {
        const mesmaColuna = outras.some(([casa]) => casa[0] === origem[0])
        const mesmaLinha = outras.some(([casa]) => casa[1] === origem[1])
        if (!mesmaColuna) desambiguacao = origem[0]
        else if (!mesmaLinha) desambiguacao = origem[1]
        else desambiguacao = origem
      }
    }

    const promo = jogada.promocao ? `=${jogada.promocao.toUpperCase()}` : ''
    base = `${LETRA_PECA[tipo]}${desambiguacao}${captura ? 'x' : ''}${destino}${promo}`
  }

  const sufixo = xequeMate ? '#' : reiEmXeque(boardDepois, corAdv) ? '+' : ''
  return `${base}${sufixo}`
}
