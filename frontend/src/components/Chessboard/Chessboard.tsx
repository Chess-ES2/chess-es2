import { useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, LayoutGroup, MotionConfig, motion } from 'motion/react'
import { usePieceDrag } from './usePieceDrag'
import Promotion from './Promotion'
import Checkmate from './Checkmate'
import { centroDaCasa, pieceImage } from './tabuleiro'
import {
  desfazer,
  jogar,
  movimentos,
  novaPartida,
  type EstadoPartida,
  type JogadaServidor,
} from '../../api'
import type { Color, PieceType, Square } from './types'
import type { GameMode, BotDifficulty } from '../../types'
import './Chessboard.css'

interface ChessboardProps {
  mode: GameMode;
  difficulty: BotDifficulty;
  corJogador: Color;
  onVoltarMenu: () => void;
  onTrocarLados: () => void;
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

const FEN_INICIAL = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w'

const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] as const
const squares = [8, 7, 6, 5, 4, 3, 2, 1].flatMap((rank) =>
  files.map((file) => `${file}${rank}` as Square),
)

function corDoChar(caractere: string): Color {
  return caractere === caractere.toUpperCase() ? 'w' : 'b'
}

function boardFromFen(fen: string): Board {
  const board: Board = {}
  fen.split(' ')[0].split('/').forEach((linha, indice) => {
    let coluna = 0
    for (const caractere of linha) {
      if (caractere >= '1' && caractere <= '8') {
        coluna += Number(caractere)
        continue
      }
      board[`${files[coluna]}${8 - indice}` as Square] = {
        color: corDoChar(caractere),
        type: caractere.toLowerCase() as PieceType,
      }
      coluna += 1
    }
  })
  return board
}

function idsDaPosicao(board: Board): PieceIds {
  return Object.fromEntries(Object.keys(board).map((casa) => [casa, casa])) as PieceIds
}

const IDS_INICIAIS = idsDaPosicao(boardFromFen(FEN_INICIAL))

function moverIds(
  ids: PieceIds,
  jogada: Pick<JogadaServidor, 'origem' | 'destino' | 'e_roque' | 'e_en_passant'>,
): PieceIds {
  const proximos = { ...ids }
  if (jogada.e_en_passant) {
    delete proximos[`${jogada.destino[0]}${jogada.origem[1]}` as Square]
  }
  if (jogada.e_roque) {
    const [torreDe, torrePara] = jogada.destino === 'g1' ? ['h1', 'f1']
      : jogada.destino === 'c1' ? ['a1', 'd1']
      : jogada.destino === 'g8' ? ['h8', 'f8']
      : ['a8', 'd8']
    proximos[torrePara as Square] = ids[torreDe as Square]
    delete proximos[torreDe as Square]
  }
  proximos[jogada.destino as Square] = ids[jogada.origem as Square]
  delete proximos[jogada.origem as Square]
  return proximos
}

function capturas(jogadas: JogadaServidor[]): Captured {
  const resultado: Captured = { w: [], b: [] }
  for (const jogada of jogadas) {
    if (!jogada.captura) continue
    resultado[corDoChar(jogada.peca)].push({
      color: corDoChar(jogada.captura),
      type: jogada.captura.toLowerCase() as PieceType,
    })
  }
  return resultado
}

function capturedValue(pieces: Piece[]) {
  return pieces.reduce((total, piece) => total + pieceValues[piece.type], 0)
}

function PlayerBar({ color, name, pieces, advantage, active, position }: {
  color: Color; name: string; pieces: Piece[]; advantage: number; active: boolean; position: 'top' | 'bottom'
}) {
  return (
    <div className={['player-bar', position, active && 'active'].filter(Boolean).join(' ')}>
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

export default function Chessboard({ mode, difficulty, corJogador, onVoltarMenu, onTrocarLados }: ChessboardProps) {
  const boardId = useId()
  const boardRef = useRef<HTMLDivElement>(null)
  const [partidaId, setPartidaId] = useState<string | null>(null)
  const [board, setBoard] = useState(() => boardFromFen(FEN_INICIAL))
  const [turn, setTurn] = useState<Color>('w')
  const [selected, setSelected] = useState<Square | null>(null)
  const [jogadas, setJogadas] = useState<JogadaServidor[]>([])
  const [promocao, setPromocao] = useState<{ origem: Square; destino: Square } | null>(null)
  const [xequeMate, setXequeMate] = useState(false)
  const [ultimosMovimentos, setUltimosMovimentos] = useState<{
    casa: Square
    destinos: Square[]
  } | null>(null)
  const [arrows, setArrows] = useState<Move[]>([])
  const [drawingArrow, setDrawingArrow] = useState<Move | null>(null)
  const drag = usePieceDrag({ boardRef, onSelect: setSelected, onDrop: dropPiece })

  const history: Move[] = jogadas.map((jogada) => ({
    from: jogada.origem as Square,
    to: jogada.destino as Square,
  }))
  const lastMove = history.at(-1) ?? null
  const idsMovidos = jogadas.reduce(moverIds, IDS_INICIAIS)
  const pieceIds = promocao
    ? moverIds(idsMovidos, { ...promocao, e_roque: false, e_en_passant: false })
    : idsMovidos
  const captured = capturas(jogadas)
  const pecaPendente = promocao ? board[promocao.origem] : undefined

  useEffect(() => {
    let ativo = true
    novaPartida()
      .then((estado) => {
        if (!ativo) return
        setPartidaId(estado.id)
        setBoard(boardFromFen(estado.fen))
        setTurn(estado.turno === 'brancas' ? 'w' : 'b')
        setXequeMate(estado.xeque_mate)
      })
      .catch(() => setPartidaId(null))
    return () => {
      ativo = false
    }
  }, [])

  useEffect(() => {
    if (!partidaId || !selected) return
    let ativo = true
    movimentos(partidaId, selected)
      .then((dados) => {
        if (ativo) {
          setUltimosMovimentos({
            casa: selected,
            destinos: dados.movimentos.map((jogada) => jogada.destino as Square),
          })
        }
      })
      .catch(() => {
        if (ativo) setUltimosMovimentos(null)
      })
    return () => {
      ativo = false
    }
  }, [partidaId, selected])

  const destinos = ultimosMovimentos?.casa === selected ? ultimosMovimentos.destinos : []

  function aplicarEstado(estado: EstadoPartida) {
    setBoard(boardFromFen(estado.fen))
    setTurn(estado.turno === 'brancas' ? 'w' : 'b')
    setXequeMate(estado.xeque_mate)
  }

  async function resetGame() {
    drag.reset()
    setSelected(null)
    setPromocao(null)
    setXequeMate(false)
    setArrows([])
    setUltimosMovimentos(null)
    setJogadas([])
    try {
      const estado = await novaPartida()
      aplicarEstado(estado)
      setPartidaId(estado.id)
    } catch {
      setPartidaId(null)
    }
  }

  function advantageFor(cor: Color) {
    const outra: Color = cor === 'w' ? 'b' : 'w'
    return capturedValue(captured[cor]) - capturedValue(captured[outra])
  }

  const virado = corJogador === 'b'
  const corTopo: Color = virado ? 'w' : 'b'
  const squaresVisiveis = virado ? [...squares].reverse() : squares

  const moveRows: Array<{ white: Move; black?: Move }> = []
  for (let index = 0; index < history.length; index += 2) {
    moveRows.push({ white: history[index], black: history[index + 1] })
  }

  async function tentarJogada(origem: Square, destino: Square): Promise<boolean> {
    if (!partidaId || origem === destino) return false
    const peca = board[origem]
    if (!peca || board[destino]?.color === peca.color) return false
    const promove = peca.type === 'p'
      && origem[1] === (peca.color === 'w' ? '7' : '2')
      && destino[1] === (peca.color === 'w' ? '8' : '1')
    if (promove) {
      let legais = destinos
      if (!legais.includes(destino)) {
        try {
          legais = (await movimentos(partidaId, origem)).movimentos.map(
            (jogada) => jogada.destino as Square,
          )
        } catch {
          return false
        }
      }
      if (!legais.includes(destino)) return false
      setPromocao({ origem, destino })
      setSelected(null)
      return true
    }
    try {
      const { jogada, estado } = await jogar(partidaId, origem, destino)
      setJogadas((atuais) => [...atuais, jogada])
      aplicarEstado(estado)
      setSelected(null)
      return true
    } catch {
      return false
    }
  }

  async function confirmarPromocao(tipo: PieceType) {
    if (!partidaId || !promocao) return
    const { origem, destino } = promocao
    setPromocao(null)
    try {
      const { jogada, estado } = await jogar(partidaId, origem, destino, tipo)
      setJogadas((atuais) => [...atuais, jogada])
      aplicarEstado(estado)
    } catch {
      return
    }
  }

  async function dropPiece(from: Square, to: Square): Promise<Square> {
    const aceita = await tentarJogada(from, to)
    return aceita ? to : from
  }

  function selectSquare(square: Square) {
    if (square === selected) {
      setSelected(null)
      return
    }
    const peca = board[square]
    if (selected && (!peca || peca.color !== turn)) {
      void tentarJogada(selected, square)
      return
    }
    setSelected(peca?.color === turn ? square : null)
  }

  async function undoMove() {
    if (!partidaId || jogadas.length === 0) return
    drag.reset()
    setSelected(null)
    setPromocao(null)
    try {
      const { estado } = await desfazer(partidaId)
      setJogadas((atuais) => atuais.slice(0, -1))
      aplicarEstado(estado)
    } catch {
      return
    }
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
            <PlayerBar position="top" color={corTopo} name={corTopo === 'w' ? 'Brancas' : 'Pretas'} pieces={captured[corTopo]} advantage={Math.max(0, advantageFor(corTopo))} active={turn === corTopo} />
            <LayoutGroup id={`${boardId}`}>
              <div ref={boardRef} className={`board${drag.isDragging ? ' is-dragging' : ''}`} role="group" aria-label="Tabuleiro de xadrez"
              onContextMenu={(event) => event.preventDefault()}
                onPointerLeave={() => setDrawingArrow(null)}
                onKeyDown={(event) => {
                  if (event.key === 'Escape') {
                    drag.cancel()
                    setSelected(null)
                    setPromocao(null)
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
                    const start = centroDaCasa(arrow.from, virado);
                    const end = centroDaCasa(arrow.to, virado);
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
                {squaresVisiveis.map((square, index) => {
                  const piece = square === promocao?.destino
                    ? pecaPendente
                    : square === promocao?.origem
                      ? undefined
                      : board[square]
                  const isDark = (Math.floor(index / 8) + index % 8) % 2 === 1
                  const isSelected = selected === square
                  const isLastMove = lastMove?.from === square || lastMove?.to === square
                  const canDrag = piece?.color === turn
                  const isDestino = destinos.includes(square)
                  const description = piece ? `${pieceNames[piece.type]} (${piece.color === 'w' ? 'brancas' : 'pretas'})` : 'vazia'

                  return (
                    <button key={square} type="button" data-square={square}
                      className={['square', isDark ? 'dark' : 'light', isSelected && 'selected',
                        isLastMove && 'last-move', canDrag && 'draggable-square',
                        isDestino && 'valid-move',
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
                {promocao && pecaPendente && (
                  <Promotion
                    cor={pecaPendente.color}
                    destino={promocao.destino}
                    virado={virado}
                    onEscolher={confirmarPromocao}
                    onCancelar={() => setPromocao(null)}
                  />
                )}
              </div>
            </LayoutGroup>
            <PlayerBar position="bottom" color={corJogador} name={corJogador === 'w' ? 'Brancas' : 'Pretas'} pieces={captured[corJogador]} advantage={Math.max(0, advantageFor(corJogador))} active={turn === corJogador} />
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
              <button type="button" className="action-button primary" onClick={resetGame}>
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
      <AnimatePresence>
        {xequeMate && !drag.floating && (
          <Checkmate
            vencedor={turn === 'w' ? 'b' : 'w'}
            onVerTabuleiro={() => setXequeMate(false)}
            onVoltarMenu={onVoltarMenu}
            onTrocarLados={() => {
              onTrocarLados()
              void resetGame()
            }}
          />
        )}
      </AnimatePresence>
    </MotionConfig>
  )
}
