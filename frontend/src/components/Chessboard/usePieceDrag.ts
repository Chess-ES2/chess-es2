import { useEffect, useRef, useState } from 'react'
import type { PointerEvent, RefObject } from 'react'
import { animate, useAnimationFrame, useMotionValue, useReducedMotion } from 'motion/react'
import type { Color, PieceType, Square } from './types'

type DragPiece = { id: string; square: Square; color: Color; type: PieceType }
type FloatingPiece = DragPiece & { size: number; originX: number; originY: number }
type Grab = DragPiece & {
  pointerId: number
  element: HTMLButtonElement
  startX: number
  startY: number
  offsetX: number
  offsetY: number
  originX: number
  originY: number
  moved: boolean
  deselectOnClick: boolean
  lastX: number
  lastTime: number
  velocityX: number
}

type DragOptions = {
  boardRef: RefObject<HTMLDivElement | null>
  onSelect: (square: Square | null) => void
  onDrop: (from: Square, to: Square) => Square
}

// Abaixo desse limiar (px/s) a peça não gira: só movimentos rápidos giram.
const SPIN_THRESHOLD = 1500
const SPIN_FACTOR = 0.5
const MAX_SPIN = 2400

export function usePieceDrag({ boardRef, onSelect, onDrop }: DragOptions) {
  const [floating, setFloating] = useState<FloatingPiece | null>(null)
  const [hovered, setHovered] = useState<Square | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const grab = useRef<Grab | null>(null)
  const suppressClick = useRef(false)
  const animations = useRef<Array<{ stop: () => void }>>([])
  const generation = useRef(0)
  const reducedMotion = useReducedMotion()
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const spin = useMotionValue(0)
  const spinVelocity = useRef(0)

  // Inércia do giro: atrito vai freando e uma mola traz de volta pra posição ereta.
  useAnimationFrame((_, delta) => {
    if (reducedMotion || !grab.current) return
    const step = Math.min(delta, 32) / 1000
    let speed = spinVelocity.current
    if (speed === 0 && spin.get() === 0) return
    speed *= Math.exp(-5.5 * step)
    const upright = Math.round(spin.get() / 360) * 360
    speed += (upright - spin.get()) * 18 * step
    if (Math.abs(speed) < 4 && Math.abs(spin.get() - upright) < 0.5) {
      spinVelocity.current = 0
      spin.jump(upright)
      return
    }
    spinVelocity.current = speed
    spin.set(spin.get() + speed * step)
  })

  useEffect(() => () => {
    generation.current += 1
    animations.current.forEach((animation) => animation.stop())
  }, [])

  function squareAt(clientX: number, clientY: number) {
    const element = document.elementFromPoint(clientX, clientY)?.closest<HTMLButtonElement>('[data-square]')
    return element && boardRef.current?.contains(element) ? element.dataset.square as Square : null
  }

  function clearAnimation() {
    generation.current += 1
    animations.current.forEach((animation) => animation.stop())
    animations.current = []
  }

  function releasePointer(current: Grab) {
    grab.current = null
    if (current.element.hasPointerCapture(current.pointerId)) {
      current.element.releasePointerCapture(current.pointerId)
    }
  }

  function start(event: PointerEvent<HTMLButtonElement>, piece: DragPiece, selected: Square | null) {
    if (!event.isPrimary || event.button !== 0 || grab.current) return
    clearAnimation()
    setFloating(null)
    spin.jump(0)
    spinVelocity.current = 0
    suppressClick.current = true
    // Guarda onde a peça foi pega pra ela ficar presa nesse ponto do cursor.
    const rect = event.currentTarget.getBoundingClientRect()
    const size = rect.width * 0.9
    const left = rect.left + (rect.width - size) / 2
    const top = rect.top + (rect.height - size) / 2
    grab.current = {
      ...piece, pointerId: event.pointerId, element: event.currentTarget,
      startX: event.clientX, startY: event.clientY,
      offsetX: left - event.clientX, offsetY: top - event.clientY,
      originX: Math.min(95, Math.max(5, ((event.clientX - left) / size) * 100)),
      originY: Math.min(95, Math.max(5, ((event.clientY - top) / size) * 100)),
      moved: false, deselectOnClick: selected === piece.square,
      lastX: event.clientX, lastTime: event.timeStamp, velocityX: 0,
    }
    event.currentTarget.setPointerCapture(event.pointerId)
    onSelect(piece.square)
  }

  function move(event: PointerEvent<HTMLButtonElement>) {
    const current = grab.current
    if (!current || current.pointerId !== event.pointerId) return
    if (!current.moved && Math.hypot(event.clientX - current.startX, event.clientY - current.startY) < 4) return
    // Velocidade do ponteiro (suavizada) — é o que decide se a peça gira.
    const elapsed = event.timeStamp - current.lastTime
    if (elapsed > 0) {
      const instant = (event.clientX - current.lastX) / (elapsed / 1000)
      current.velocityX += (instant - current.velocityX) * 0.5
      current.lastX = event.clientX
      current.lastTime = event.timeStamp
    }
    if (!current.moved) {
      current.moved = true
      x.jump(event.clientX + current.offsetX)
      y.jump(event.clientY + current.offsetY)
      setFloating({
        id: current.id, square: current.square, color: current.color, type: current.type,
        size: current.element.getBoundingClientRect().width * 0.9,
        originX: current.originX, originY: current.originY,
      })
      setIsDragging(true)
    } else {
      x.set(event.clientX + current.offsetX)
      y.set(event.clientY + current.offsetY)
    }
    if (Math.abs(current.velocityX) > SPIN_THRESHOLD) {
      const target = Math.max(-MAX_SPIN, Math.min(MAX_SPIN, current.velocityX * SPIN_FACTOR))
      spinVelocity.current += (target - spinVelocity.current) * 0.4
    }
    setHovered(squareAt(event.clientX, event.clientY))
  }

  function settle(current: Grab, square: Square) {
    setIsDragging(false)
    setHovered(null)
    spinVelocity.current = 0
    const target = boardRef.current?.querySelector<HTMLButtonElement>(`[data-square="${square}"]`)
    const upright = Math.round(spin.get() / 360) * 360
    if (!target || reducedMotion) {
      spin.jump(0)
      setFloating(null)
      return
    }
    const rect = target.getBoundingClientRect()
    const size = current.element.getBoundingClientRect().width * 0.9
    const version = generation.current
    animations.current = [
      animate(x, rect.left + (rect.width - size) / 2, { duration: 0.2, ease: [0.2, 0, 0, 1] }),
      animate(y, rect.top + (rect.height - size) / 2, {
        duration: 0.2, ease: [0.2, 0, 0, 1],
        onComplete: () => {
          if (version === generation.current) setFloating(null)
        },
      }),
      animate(spin, upright, { duration: 0.2, ease: [0.2, 0, 0, 1] }),
    ]
  }

  function end(event: PointerEvent<HTMLButtonElement>) {
    const current = grab.current
    if (!current || current.pointerId !== event.pointerId) return
    releasePointer(current)
    if (!current.moved) {
      if (current.deselectOnClick) onSelect(null)
      return
    }
    const target = squareAt(event.clientX, event.clientY)
    const destination = target ? onDrop(current.square, target) : current.square
    settle(current, destination)
  }

  function cancel() {
    const current = grab.current
    if (!current) return
    releasePointer(current)
    if (current.moved) settle(current, current.square)
  }

  function reset() {
    const current = grab.current
    if (current) releasePointer(current)
    clearAnimation()
    spinVelocity.current = 0
    spin.jump(0)
    setFloating(null)
    setHovered(null)
    setIsDragging(false)
  }

  function consumeClick() {
    const suppressed = suppressClick.current
    suppressClick.current = false
    return suppressed
  }

  function preparePointer() {
    if (!grab.current) suppressClick.current = false
  }

  return { floating, hovered, isDragging, x, y, rotate: reducedMotion ? 0 : spin,
    start, move, end, cancel, reset, consumeClick, preparePointer }
}
