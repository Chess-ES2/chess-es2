import { useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, LayoutGroup, MotionConfig, motion } from 'motion/react'
import { Chess, SQUARES } from 'chess.js'
import type { Color, PieceSymbol, Square } from 'chess.js'
import { usePieceDrag } from './usePieceDrag'
import './Chessboard.css'

const pieceNames: Record<PieceSymbol, string> = {
  p: 'Peão', n: 'Cavalo', b: 'Bispo', r: 'Torre', q: 'Dama', k: 'Rei',
}
type PieceIds = Partial<Record<Square, string>>

// Posição inicial sem direitos de roque para ambos os lados.
const initialPosition = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1'

function initialPieceIds(): PieceIds {
  const board = new Chess(initialPosition)
  return Object.fromEntries(SQUARES.filter((square) => board.get(square)).map((square) => [square, square]))
}

function pieceImage(color: Color, type: PieceSymbol) {
  return `https://lichess1.org/assets/piece/cburnett/${color}${type.toUpperCase()}.svg`
}

function availableMoves(game: Chess, square?: Square) {
  return game.moves({ square, verbose: true }).filter((move) => !move.isPromotion())
}

function gameStatus(game: Chess, hasMoves: boolean) {
  if (!hasMoves && game.isCheck()) {
    return `Xeque-mate! Vitória das ${game.turn() === 'w' ? 'pretas' : 'brancas'}.`
  }
  if (!hasMoves) return 'Empate por afogamento.'
  if (game.isThreefoldRepetition()) return 'Empate por repetição de posição.'
  if (game.isInsufficientMaterial()) return 'Empate por material insuficiente.'
  if (game.isDraw()) return 'Empate pela regra dos 50 lances.'
  return `Vez das ${game.turn() === 'w' ? 'brancas' : 'pretas'}${game.isCheck() ? ' — xeque!' : '.'}`
}

export default function Chessboard() {
  const boardId = useId()
  const boardRef = useRef<HTMLDivElement>(null)
  const [game, setGame] = useState(() => new Chess(initialPosition))
  const [pieceIds, setPieceIds] = useState(initialPieceIds)
  const [gameNumber, setGameNumber] = useState(0)
  const [selected, setSelected] = useState<Square | null>(null)
  const [lastMove, setLastMove] = useState<{ from: Square; to: Square } | null>(null)
  const moves = availableMoves(game)
  const gameOver = moves.length === 0 || game.isDraw()
  const legalMoves = selected && !gameOver ? moves.filter((move) => move.from === selected) : []
  const drag = usePieceDrag({ boardRef, onSelect: setSelected, onDrop: dropPiece })

  function moveTo(to: Square, from = selected) {
    if (!from || !moves.some((move) => move.from === from && move.to === to)) return
    // Preserve history for repetition detection without mutating React state.
    const nextGame = new Chess(initialPosition)
    nextGame.loadPgn(game.pgn())
    const move = nextGame.move({ from, to })
    const nextIds = { ...pieceIds, [to]: pieceIds[from] }
    delete nextIds[from]
    if (move.isEnPassant()) {
      const capturedSquare = `${to[0]}${from[1]}` as Square
      delete nextIds[capturedSquare]
    }
    setPieceIds(nextIds)
    setGame(nextGame)
    setLastMove({ from, to })
    setSelected(null)
  }

  function dropPiece(from: Square, to: Square): Square {
    if (gameOver) return from
    const move = moves.find((candidate) => candidate.from === from && candidate.to === to)
    if (!move) return from
    moveTo(to, from)
    return to
  }

  function selectSquare(square: Square) {
    if (gameOver) return
    if (square === selected) {
      setSelected(null)
      return
    }
    const move = legalMoves.find((candidate) => candidate.to === square)
    if (move) {
      moveTo(square)
      return
    }
    setSelected(game.get(square)?.color === game.turn() ? square : null)
  }

  function resetGame() {
    drag.reset()
    setGame(new Chess(initialPosition))
    setPieceIds(initialPieceIds())
    setGameNumber((number) => number + 1)
    setSelected(null)
    setLastMove(null)
  }

  return (
    <MotionConfig reducedMotion="user" transition={{ type: 'spring', duration: 0.28, bounce: 0 }}>
      <section className="chess-game" aria-label="Partida de xadrez">
        <div className="game-toolbar">
          <p className="game-status" role="status">{gameStatus(game, moves.length > 0)}</p>
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
            {SQUARES.map((square, index) => {
              const piece = game.get(square)
              const isDark = (Math.floor(index / 8) + index % 8) % 2 === 1
              const move = legalMoves.find((candidate) => candidate.to === square)
              const isSelected = selected === square
              const isLastMove = lastMove?.from === square || lastMove?.to === square
              const canDrag = piece?.color === game.turn() && !gameOver
              const description = piece ? `${pieceNames[piece.type]} (${piece.color === 'w' ? 'brancas' : 'pretas'})` : 'vazia'

              return (
                <button key={square} type="button" data-square={square}
                  className={['square', isDark ? 'dark' : 'light', isSelected && 'selected',
                    isLastMove && 'last-move', move && 'legal-destination',
                    canDrag && 'draggable-square', move && drag.hovered === square && 'drop-target',
                  ].filter(Boolean).join(' ')}
                  aria-label={`${square}: ${description}${move ? (move.captured ? ', captura disponível' : ', movimento disponível') : ''}`}
                  aria-pressed={isSelected}
                  disabled={gameOver}
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
                  <AnimatePresence initial={false}>
                    {move && <motion.span key="hint" className={`move-hint${move.captured ? ' capture-hint' : ''}`}
                      initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.5 }} transition={{ duration: 0.15, type: 'tween' }}
                      aria-hidden="true" />}
                  </AnimatePresence>
                </button>
              )
            })}
          </div>
        </LayoutGroup>
        <p className="game-help">Arraste uma peça até um destino vermelho ou clique para mover.</p>
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
