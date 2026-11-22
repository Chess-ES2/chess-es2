import { centroDaCasa } from './tabuleiro'
import type { Square } from './types'

export type BoardArrow = { from: Square; to: Square }

type BoardArrowsProps = {
  arrows: BoardArrow[]
  drawingArrow: BoardArrow | null
  highlights: Square[]
  virado: boolean
}

const BOARD_SIZE = 800
const SHAFT_HALF = 7
const HEAD_LENGTH = 29
const HEAD_HALF = 17.5
const START_PAD = 24
const END_PAD = 14

function ponto(casa: Square, virado: boolean) {
  const c = centroDaCasa(casa, virado)
  return { x: (c.x / 100) * BOARD_SIZE, y: (c.y / 100) * BOARD_SIZE }
}

function caminhoSetaReta(x1: number, y1: number, x2: number, y2: number): string {
  const dx = x2 - x1
  const dy = y2 - y1
  const dist = Math.hypot(dx, dy)
  if (dist < START_PAD + END_PAD + HEAD_LENGTH * 0.5) return ''

  const ux = dx / dist
  const uy = dy / dist
  const px = -uy
  const py = ux

  const sx = x1 + ux * START_PAD
  const sy = y1 + uy * START_PAD
  const tx = x2 - ux * END_PAD
  const ty = y2 - uy * END_PAD
  const bx = tx - ux * HEAD_LENGTH
  const by = ty - uy * HEAD_LENGTH

  const sLx = sx + px * SHAFT_HALF
  const sLy = sy + py * SHAFT_HALF
  const sRx = sx - px * SHAFT_HALF
  const sRy = sy - py * SHAFT_HALF

  const bLx = bx + px * SHAFT_HALF
  const bLy = by + py * SHAFT_HALF
  const bRx = bx - px * SHAFT_HALF
  const bRy = by - py * SHAFT_HALF

  const wLx = bx + px * HEAD_HALF
  const wLy = by + py * HEAD_HALF
  const wRx = bx - px * HEAD_HALF
  const wRy = by - py * HEAD_HALF

  return [
    `M ${sLx.toFixed(1)} ${sLy.toFixed(1)}`,
    `L ${bLx.toFixed(1)} ${bLy.toFixed(1)}`,
    `L ${wLx.toFixed(1)} ${wLy.toFixed(1)}`,
    `L ${tx.toFixed(1)} ${ty.toFixed(1)}`,
    `L ${wRx.toFixed(1)} ${wRy.toFixed(1)}`,
    `L ${bRx.toFixed(1)} ${bRy.toFixed(1)}`,
    `L ${sRx.toFixed(1)} ${sRy.toFixed(1)}`,
    `A ${SHAFT_HALF} ${SHAFT_HALF} 0 0 0 ${sLx.toFixed(1)} ${sLy.toFixed(1)}`,
    'Z',
  ].join(' ')
}

function eSaltoCavalo(dx: number, dy: number) {
  const ax = Math.round(Math.abs(dx))
  const ay = Math.round(Math.abs(dy))
  return (ax === 100 && ay === 200) || (ax === 200 && ay === 100)
}

function SetaCavalo({
  x1, y1, x2, y2, opacity,
}: { x1: number; y1: number; x2: number; y2: number; opacity: number }) {
  const dx = x2 - x1
  const dy = y2 - y1
  const horizontalPrimeiro = Math.abs(dx) > Math.abs(dy)
  const cornerX = horizontalPrimeiro ? x2 : x1
  const cornerY = horizontalPrimeiro ? y1 : y2

  // Segmento inicial recuado da casa de origem até o cotovelo
  const ux1 = Math.sign(cornerX - x1)
  const uy1 = Math.sign(cornerY - y1)
  const sx = x1 + ux1 * START_PAD
  const sy = y1 + uy1 * START_PAD

  // Segmento final do cotovelo até a ponta recuada na casa destino
  const ux2 = Math.sign(x2 - cornerX)
  const uy2 = Math.sign(y2 - cornerY)
  const tx = x2 - ux2 * END_PAD
  const ty = y2 - uy2 * END_PAD
  const bx = tx - ux2 * HEAD_LENGTH
  const by = ty - uy2 * HEAD_LENGTH
  const px2 = -uy2
  const py2 = ux2

  const headPoints = [
    `${(bx + px2 * HEAD_HALF).toFixed(1)},${(by + py2 * HEAD_HALF).toFixed(1)}`,
    `${tx.toFixed(1)},${ty.toFixed(1)}`,
    `${(bx - px2 * HEAD_HALF).toFixed(1)},${(by - py2 * HEAD_HALF).toFixed(1)}`,
  ].join(' ')

  return (
    <g opacity={opacity}>
      <path
        d={`M ${sx.toFixed(1)} ${sy.toFixed(1)} L ${cornerX.toFixed(1)} ${cornerY.toFixed(1)} L ${bx.toFixed(1)} ${by.toFixed(1)}`}
        fill="none"
        stroke="#f59e0b"
        strokeWidth={SHAFT_HALF * 2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polygon points={headPoints} fill="#f59e0b" />
    </g>
  )
}

export default function BoardArrows({
  arrows,
  drawingArrow,
  highlights,
  virado,
}: BoardArrowsProps) {
  const renderList: Array<{ arrow: BoardArrow; preview: boolean }> = [
    ...arrows.map((arrow) => ({ arrow, preview: false })),
    ...(drawingArrow && drawingArrow.from !== drawingArrow.to
      ? [{ arrow: drawingArrow, preview: true }]
      : []),
  ]

  if (renderList.length === 0 && highlights.length === 0) return null

  return (
    <svg
      className="board-arrows"
      viewBox={`0 0 ${BOARD_SIZE} ${BOARD_SIZE}`}
      aria-hidden="true"
    >
      {highlights.map((square) => {
        const { x, y } = ponto(square, virado)
        return (
          <circle
            key={`hl-${square}`}
            cx={x}
            cy={y}
            r={42}
            fill="none"
            stroke="#f59e0b"
            strokeWidth={7}
            opacity={0.78}
          />
        )
      })}

      {renderList.map(({ arrow, preview }, idx) => {
        const start = ponto(arrow.from, virado)
        const end = ponto(arrow.to, virado)
        const opacity = preview ? 0.5 : 0.82

        if (eSaltoCavalo(end.x - start.x, end.y - start.y)) {
          return (
            <SetaCavalo
              key={`${arrow.from}-${arrow.to}-${preview ? 'p' : idx}`}
              x1={start.x}
              y1={start.y}
              x2={end.x}
              y2={end.y}
              opacity={opacity}
            />
          )
        }

        const d = caminhoSetaReta(start.x, start.y, end.x, end.y)
        if (!d) return null

        return (
          <path
            key={`${arrow.from}-${arrow.to}-${preview ? 'p' : idx}`}
            d={d}
            fill="#f59e0b"
            opacity={opacity}
          />
        )
      })}
    </svg>
  )
}
