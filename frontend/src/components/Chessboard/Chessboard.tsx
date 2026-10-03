import { useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, LayoutGroup, MotionConfig, motion } from 'motion/react'
import { usePieceDrag } from './usePieceDrag'
import type { Color, PieceType, Square } from './types'
import type { GameMode, BotDifficulty } from '../../types'
import './Chessboard.css'

interface ChessboardProps {
  onNovaPartida: () => void;
  mode: GameMode;
  difficulty: BotDifficulty;
}

type Piece = { color: Color; type: PieceType }
type Board = Partial<Record<Square, Piece>>
type PieceIds = Partial<Record<Square, string>>
type Move = { from: Square; to: Square }
type Captured = Record<Color, Piece[]>

const pieceNames: Record<PieceType, string> = {
  p: 'Peão', n: 'Cavalo', b: 'Bispo', r: 'Torre', q: 'Dama', k: 'Rei',
}

const pieceValues: Record<PieceType, number> = {
  p: 1, n: 3, b: 3, r: 5, q: 9, k: 0,
}

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

function replay(moves: Move[]) {
  const board = initialBoard()
  const pieceIds = initialPieceIds()
  const captured: Captured = { w: [], b: [] }
  moves.forEach(({ from, to }) => {
    const piece = board[from]
    if (!piece) return
    const target = board[to]
    if (target && target.color !== piece.color) captured[piece.color].push(target)
    board[to] = piece
    delete board[from]
    pieceIds[to] = pieceIds[from]
    delete pieceIds[from]
  })
  return { board, pieceIds, captured }
}

function capturedValue(pieces: Piece[]) {
  return pieces.reduce((total, piece) => total + pieceValues[piece.type], 0)
}

function PlayerBar({ color, name, pieces, advantage, active }: {
  color: Color; name: string; pieces: Piece[]; advantage: number; active: boolean
}) {
  return (
    <div className={['player-bar', color === 'b' ? 'top' : 'bottom', active && 'active'].filter(Boolean).join(' ')}>
      <span className="player-avatar">
        <img src={pieceImage(color, 'k')} alt="" />
      </span>
      <span className="player-name">{name}</span>
      <span className="player-captured">
        {pieces.map((piece, index) => (
          <img key={index} src={pieceImage(piece.color, piece.type)} alt="" className="captured-piece" />
        ))}
        {advantage > 0 && <span className="material-advantage">+{advantage}</span>}
      </span>
    </div>
  )
}

function getArrowCoords(sq: string) {
  const file = sq.charCodeAt(0) - 97;
  const rank = 8 - parseInt(sq[1], 10);
  return { x: file * 12.5 + 6.25, y: rank * 12.5 + 6.25 };
}

export default function Chessboard({ onNovaPartida, mode, difficulty }: ChessboardProps) {
  const boardId = useId()
  const boardRef = useRef<HTMLDivElement>(null)
  const [board, setBoard] = useState(initialBoard)
  const [pieceIds, setPieceIds] = useState(initialPieceIds)
  const [turn, setTurn] = useState<Color>('w')
  const [selected, setSelected] = useState<Square | null>(null)
  const [lastMove, setLastMove] = useState<Move | null>(null)
  const [captured, setCaptured] = useState<Captured>({ w: [], b: [] })
  const [history, setHistory] = useState<Move[]>([])
  const [arrows, setArrows] = useState<Move[]>([])
  const [drawingArrow, setDrawingArrow] = useState<Move | null>(null)
  const drag = usePieceDrag({ boardRef, onSelect: setSelected, onDrop: dropPiece })

  const advantage = capturedValue(captured.w) - capturedValue(captured.b)
  const moveRows: Array<{ white: Move; black?: Move }> = []
  for (let index = 0; index < history.length; index += 2) {
    moveRows.push({ white: history[index], black: history[index + 1] })
  }

  function moveTo(to: Square, from = selected) {
    if (!from || from === to || !board[from]) return
    const piece = board[from]
    const target = board[to]
    const nextBoard = { ...board, [to]: piece }
    delete nextBoard[from]
    const nextIds = { ...pieceIds, [to]: pieceIds[from] }
    delete nextIds[from]
    if (target && target.color !== piece.color) {
      setCaptured((previous) => ({ ...previous, [piece.color]: [...previous[piece.color], target] }))
    }
    setBoard(nextBoard)
    setPieceIds(nextIds)
    setHistory((previous) => [...previous, { from, to }])
    setLastMove({ from, to })
    setSelected(null)
    setTurn(turn === 'w' ? 'b' : 'w')
  }

  function dropPiece(from: Square, to: Square): Square {
    const piece = board[from]
    if (!piece || from === to || board[to]?.color === piece.color) return from
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

  function undoMove() {
    if (history.length === 0) return
    drag.reset()
    const previous = history.slice(0, -1)
    const state = replay(previous)
    setBoard(state.board)
    setPieceIds(state.pieceIds)
    setCaptured(state.captured)
    setHistory(previous)
    setTurn(previous.length % 2 === 0 ? 'w' : 'b')
    setLastMove(previous.at(-1) ?? null)
    setSelected(null)
  }

  const dificuldadeLabel = {
    easy: 'Fácil',
    medium: 'Médio',
    hard: 'Difícil'
  };

  const allArrows = [...arrows, drawingArrow].filter(Boolean) as Move[];

  return (
    <MotionConfig reducedMotion="user" transition={{ type: 'spring', duration: 0.28, bounce: 0 }}>
      <section className="chess-game" aria-label="Partida de xadrez">
        <div className="game-layout">
          <div className="game-main">
            <PlayerBar color="b" name="Pretas" pieces={captured.b} advantage={advantage < 0 ? -advantage : 0} active={turn === 'b'} />
            <LayoutGroup id={`${boardId}`}>
              <div ref={boardRef} className={`board${drag.isDragging ? ' is-dragging' : ''}`} role="group" aria-label="Tabuleiro de xadrez"
              onContextMenu={(event) => event.preventDefault()}
                onPointerLeave={() => setDrawingArrow(null)}
                onKeyDown={(event) => {
                  if (event.key === 'Escape') {
                    drag.cancel()
                    setSelected(null)
                  }
                }}>
                  <svg style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  pointerEvents: 'none',
                  zIndex: 10
                }}>
                  {allArrows.map((arrow, i) => {
                    const start = getArrowCoords(arrow.from);
                    const end = getArrowCoords(arrow.to);
                    return (
                      <g key={`${arrow.from}-${arrow.to}-${i}`} opacity={0.8}>
                        <defs>
                          <marker id={`arrowhead-${i}`} markerWidth="4" markerHeight="4" refX="2.5" refY="2" orient="auto">
                            <polygon points="0 0, 4 2, 0 4" fill="#ffaa00" />
                          </marker>
                        </defs>
                        <line
                          x1={`${start.x}%`}
                          y1={`${start.y}%`}
                          x2={`${end.x}%`}
                          y2={`${end.y}%`}
                          stroke="#ffaa00"
                          strokeWidth="2.5%"
                          markerEnd={`url(#arrowhead-${i})`}
                        />
                      </g>
                    );
                  })}
                </svg>
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
                        if (event.button === 2) {
                          setDrawingArrow({ from: square, to: square })
                          return
                        }
                        drag.preparePointer()
                        if (canDrag && piece) {
                          drag.start(event, { id: pieceIds[square]!, square, color: piece.color, type: piece.type }, selected)
                        }
                      }}
                      onPointerEnter={() => {
                        if (drawingArrow) {
                          setDrawingArrow({ from: drawingArrow.from, to: square })
                        }
                      }}
                      onPointerMove={drag.move}
                      onPointerUp={(event) => {
                        if (event.button === 2) {
                          if (drawingArrow && drawingArrow.from !== square) {
                            setArrows((prev) => {
                              const jaExiste = prev.some((a) => a.from === drawingArrow.from && a.to === square)
                              return jaExiste
                                ? prev.filter((a) => !(a.from === drawingArrow.from && a.to === square))
                                : [...prev, { from: drawingArrow.from, to: square }]
                            })
                          }
                          setDrawingArrow(null)
                          return
                        }
                        drag.end(event)
                      }}
                      onPointerCancel={drag.cancel}
                      onLostPointerCapture={drag.cancel}
                      onClick={(event) => {
                        setArrows([])
                        if (event.detail === 0 || !drag.consumeClick()) selectSquare(square)
                      }}>
                      {index % 8 === 0 && <span className="coord coord-rank" aria-hidden="true">{square[1]}</span>}
                      {index >= 56 && <span className="coord coord-file" aria-hidden="true">{square[0]}</span>}
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
            <PlayerBar color="w" name="Brancas" pieces={captured.w} advantage={advantage > 0 ? advantage : 0} active={turn === 'w'} />
          </div>
          <aside className="game-panel" aria-label="Informações da partida">
            <header className="panel-header">
              Partida {mode === 'bot' ? `vs Computador (${dificuldadeLabel[difficulty]})` : '(Multijogador Local)'}
            </header>
            <div className="turn-card" role="status">
              <span className={`turn-dot ${turn}`} aria-hidden="true" />
              Vez das {turn === 'w' ? 'brancas' : 'pretas'}
            </div>
            <div className="move-list">
              {moveRows.length === 0
                ? <p className="move-empty">Arraste uma peça para começar.</p>
                : moveRows.map((row, rowIndex) => (
                    <div className="move-row" key={rowIndex}>
                      <span className="move-number">{rowIndex + 1}.</span>
                      <span className={`move-cell${rowIndex * 2 === history.length - 1 ? ' current' : ''}`}>
                        {row.white.from}-{row.white.to}
                      </span>
                      {row.black
                        ? <span className={`move-cell${rowIndex * 2 + 1 === history.length - 1 ? ' current' : ''}`}>
                            {row.black.from}-{row.black.to}
                          </span>
                        : <span className="move-cell" />}
                    </div>
                  ))}
            </div>
            <div className="panel-actions">
              <button type="button" className="action-button" onClick={undoMove} disabled={history.length === 0}>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                </svg>
                Desfazer
              </button>
              <button type="button" className="action-button primary" onClick={onNovaPartida}>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 8v8M8 12h8" />
                </svg>
                Nova partida
              </button>
            </div>
          </aside>
        </div>
      </section>
      {drag.floating && createPortal(
        <motion.div className="dragged-piece" aria-hidden="true"
          style={{ x: drag.x, y: drag.y, width: drag.floating.size, height: drag.floating.size }}>
          <motion.img src={pieceImage(drag.floating.color, drag.floating.type)} alt="" draggable={false}
            style={{ rotate: drag.rotate, transformOrigin: `${drag.floating.originX}% ${drag.floating.originY}%` }} />
        </motion.div>, document.body,
      )}
    </MotionConfig>
  )
}
