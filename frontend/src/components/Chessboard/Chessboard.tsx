import { useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, LayoutGroup, MotionConfig, motion } from 'motion/react'
import { usePieceDrag } from './usePieceDrag'
import type { Color, PieceType, Square } from './types'
import './Chessboard.css'

type Piece = { color: Color; type: PieceType }
type Board = Partial<Record<Square, Piece>>
type PieceIds = Partial<Record<Square, string>>

const pieceNames: Record<PieceType, string> = {
  p: 'Peão', n: 'Cavalo', b: 'Bispo', r: 'Torre', q: 'Dama', k: 'Rei',
}

// Minúsculas são as pretas, maiúsculas as brancas.
const initialRows = [
  'rnbqkbnr',
  'pppppppp',
  '........',
  '........',
  '........',
  '........',
  'PPPPPPPP',
  'RNBQKBNR',
]

const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] as const
const squares = [8, 7, 6, 5, 4, 3, 2, 1].flatMap((rank) =>
  files.map((file) => `${file}${rank}` as Square),
)

function initialBoard(): Board {
  const board: Board = {}
  initialRows.forEach((row, rowIndex) => {
    [...row].forEach((code, fileIndex) => {
      if (code === '.') return
      board[`${files[fileIndex]}${8 - rowIndex}` as Square] = {
        color: code === code.toUpperCase() ? 'w' : 'b',
        type: code.toLowerCase() as PieceType,
      }
    })
  })
  return board
}

function initialPieceIds(): PieceIds {
  return Object.fromEntries(squares.map((square) => [square, square]))
}

function pieceImage(color: Color, type: PieceType) {
  return `https://lichess1.org/assets/piece/cburnett/${color}${type.toUpperCase()}.svg`
}

export default function Chessboard() {
  const boardId = useId()
  const boardRef = useRef<HTMLDivElement>(null)
  const [board, setBoard] = useState(initialBoard)
  const [pieceIds, setPieceIds] = useState(initialPieceIds)
  const [gameNumber, setGameNumber] = useState(0)
  const [turn, setTurn] = useState<Color>('w')
  const [selected, setSelected] = useState<Square | null>(null)
  const [lastMove, setLastMove] = useState<{ from: Square; to: Square } | null>(null)
  const drag = usePieceDrag({ boardRef, onSelect: setSelected, onDrop: dropPiece })

  // Qualquer peça pode ir para qualquer casa, sem validação de regras.
  function moveTo(to: Square, from = selected) {
    if (!from || from === to || !board[from]) return
    const nextBoard = { ...board, [to]: board[from] }
    delete nextBoard[from]
    const nextIds = { ...pieceIds, [to]: pieceIds[from] }
    delete nextIds[from]
    setBoard(nextBoard)
    setPieceIds(nextIds)
    setLastMove({ from, to })
    setSelected(null)
    setTurn(turn === 'w' ? 'b' : 'w')
  }

  function dropPiece(from: Square, to: Square): Square {
    if (from === to || !board[from]) return from
    moveTo(to, from)
    return to
  }

  function selectSquare(square: Square) {
    if (square === selected) {
      setSelected(null)
      return
    }
    const piece = board[square]
    if (selected && (!piece || piece.color !== turn)) {
      moveTo(square)
      return
    }
    setSelected(piece?.color === turn ? square : null)
  }

  function resetGame() {
    drag.reset()
    setBoard(initialBoard())
    setPieceIds(initialPieceIds())
    setTurn('w')
    setGameNumber((number) => number + 1)
    setSelected(null)
    setLastMove(null)
  }

  return (
    <MotionConfig reducedMotion="user" transition={{ type: 'spring', duration: 0.28, bounce: 0 }}>
      <section className="chess-game" aria-label="Partida de xadrez">
        <div className="game-toolbar">
          <p className="game-status" role="status">Vez das {turn === 'w' ? 'brancas' : 'pretas'}.</p>
          <button type="button" className="reset-button" onClick={resetGame}>Nova partida</button>
        </div>
        <LayoutGroup id={`${boardId}-${gameNumber}`}>
          <div ref={boardRef} key={gameNumber} className={`board${drag.isDragging ? ' is-dragging' : ''}`} role="group" aria-label="Tabuleiro de xadrez"
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                drag.cancel()
                setSelected(null)
              }
            }}>
            {squares.map((square, index) => {
              const piece = board[square]
              const isDark = (Math.floor(index / 8) + index % 8) % 2 === 1
              const isSelected = selected === square
              const isLastMove = lastMove?.from === square || lastMove?.to === square
              const canDrag = piece?.color === turn
              const description = piece ? `${pieceNames[piece.type]} (${piece.color === 'w' ? 'brancas' : 'pretas'})` : 'vazia'

              return (
                <button key={square} type="button" data-square={square}
                  className={['square', isDark ? 'dark' : 'light', isSelected && 'selected',
                    isLastMove && 'last-move', canDrag && 'draggable-square',
                    drag.isDragging && drag.hovered === square && 'drop-target',
                  ].filter(Boolean).join(' ')}
                  aria-label={`${square}: ${description}`}
                  aria-pressed={isSelected}
                  onPointerDown={(event) => {
                    drag.preparePointer()
                    if (canDrag && piece) {
                      drag.start(event, { id: pieceIds[square]!, square, color: piece.color, type: piece.type }, selected)
                    }
                  }}
                  onPointerMove={drag.move}
                  onPointerUp={drag.end}
                  onPointerCancel={drag.cancel}
                  onLostPointerCapture={drag.cancel}
                  onClick={(event) => {
                    if (event.detail === 0 || !drag.consumeClick()) selectSquare(square)
                  }}>
                  <AnimatePresence initial={false}>
                    {piece && <motion.img key={pieceIds[square]}
                      layoutId={drag.floating?.id === pieceIds[square] ? undefined : pieceIds[square]}
                      src={pieceImage(piece.color, piece.type)} alt="" className="piece-img" draggable={false}
                      style={{ visibility: drag.floating?.id === pieceIds[square] ? 'hidden' : 'visible' }}
                      initial={false} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      transition={{ layout: { type: 'spring', duration: 0.28, bounce: 0 }, opacity: { duration: 0.12 } }} />}
                  </AnimatePresence>
                </button>
              )
            })}
          </div>
        </LayoutGroup>
        <p className="game-help">Arraste uma peça para qualquer casa ou clique para mover.</p>
      </section>
      {drag.floating && createPortal(
        <motion.div className="dragged-piece" aria-hidden="true"
          style={{ x: drag.x, y: drag.y, width: drag.floating.size, height: drag.floating.size }}>
          <motion.img src={pieceImage(drag.floating.color, drag.floating.type)} alt="" draggable={false}
            style={{ rotate: drag.rotate }} />
        </motion.div>, document.body,
      )}
    </MotionConfig>
  )
}
