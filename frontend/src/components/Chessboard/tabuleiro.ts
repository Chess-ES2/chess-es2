import type { Color, PieceType, Square } from './types'

export function centroDaCasa(casa: Square, virado: boolean) {
  const coluna = casa.charCodeAt(0) - 97
  const linha = 8 - parseInt(casa[1], 10)
  const x = coluna * 12.5 + 6.25
  const y = linha * 12.5 + 6.25
  return virado ? { x: 100 - x, y: 100 - y } : { x, y }
}

export function pieceImage(color: Color, type: PieceType) {
  return `https://lichess1.org/assets/piece/cburnett/${color}${type.toUpperCase()}.svg`
}
