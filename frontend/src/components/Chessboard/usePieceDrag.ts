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
  onDrop: (from: Square, to: Square) => Square | Promise<Square>
  canSnapOptimistically?: (from: Square, to: Square) => boolean
}

const MAX_TILT = 13
const TILT_FACTOR = 0.011

export function usePieceDrag({ boardRef, onSelect, onDrop, canSnapOptimistically }: DragOptions) {
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
  const scale = useMotionValue(1)
  const tilt = useMotionValue(0)
  const tiltVelocity = useRef(0)

  useAnimationFrame((_, delta) => {
    if (reducedMotion || !grab.current?.moved) return
    const step = Math.min(delta, 32) / 1000
    const current = grab.current
    // Decai a velocidade horizontal quando o ponteiro para de se mover
    current.velocityX *= Math.exp(-12 * step)
    const targetTilt = Math.max(-MAX_TILT, Math.min(MAX_TILT, current.velocityX * TILT_FACTOR))
    const diff = targetTilt - tilt.get()
    tiltVelocity.current += diff * 180 * step
    tiltVelocity.current *= Math.exp(-16 * step)
    const next = tilt.get() + tiltVelocity.current * step
    if (Math.abs(diff) < 0.05 && Math.abs(tiltVelocity.current) < 0.1) {
      tilt.set(targetTilt)
      tiltVelocity.current = 0
    } else {
      tilt.set(next)
    }
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
    tilt.jump(0)
    tiltVelocity.current = 0
    scale.jump(1)
    suppressClick.current = true
    const rect = event.currentTarget.getBoundingClientRect()
    const size = rect.width * 0.9
    const left = rect.left + (rect.width - size) / 2
    const top = rect.top + (rect.height - size) / 2
    grab.current = {
      ...piece, pointerId: event.pointerId, element: event.currentTarget,
      startX: event.clientX, startY: event.clientY,
      offsetX: left - event.clientX, offsetY: top - event.clientY,
      originX: Math.min(85, Math.max(15, ((event.clientX - left) / size) * 100)),
      originY: Math.min(85, Math.max(15, ((event.clientY - top) / size) * 100)),
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
    const elapsed = event.timeStamp - current.lastTime
    if (elapsed > 0) {
      const instant = (event.clientX - current.lastX) / (elapsed / 1000)
      current.velocityX += (instant - current.velocityX) * 0.45
      current.lastX = event.clientX
      current.lastTime = event.timeStamp
    }
    if (!current.moved) {
      current.moved = true
      x.jump(event.clientX + current.offsetX)
      y.jump(event.clientY + current.offsetY)
      if (!reducedMotion) {
        animate(scale, 1.09, { type: 'spring', stiffness: 520, damping: 26, mass: 0.6 })
      }
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
    setHovered(squareAt(event.clientX, event.clientY))
  }

  function settle(current: Grab, square: Square, bounceBack = false) {
    setIsDragging(false)
    setHovered(null)
    tiltVelocity.current = 0
    clearAnimation()
    const target = boardRef.current?.querySelector<HTMLButtonElement>(`[data-square="${square}"]`)
    if (!target || reducedMotion) {
      tilt.jump(0)
      scale.jump(1)
      setFloating(null)
      return
    }
    const rect = target.getBoundingClientRect()
    const size = current.element.getBoundingClientRect().width * 0.9
    const version = generation.current
    const moveSpring = bounceBack
      ? { type: 'spring' as const, stiffness: 460, damping: 24, mass: 0.75 }
      : { type: 'spring' as const, stiffness: 580, damping: 30, mass: 0.65 }

    animations.current = [
      animate(x, rect.left + (rect.width - size) / 2, moveSpring),
      animate(y, rect.top + (rect.height - size) / 2, {
        ...moveSpring,
        onComplete: () => {
          if (version === generation.current) setFloating(null)
        },
      }),
      animate(scale, bounceBack ? 1 : [scale.get(), 0.96, 1], bounceBack
        ? { type: 'spring', stiffness: 480, damping: 24 }
        : { duration: 0.24, times: [0, 0.55, 1], ease: 'easeOut' }),
      animate(tilt, 0, { type: 'spring', stiffness: 420, damping: 22 }),
    ]
  }

  async function end(event: PointerEvent<HTMLButtonElement>) {
    const current = grab.current
    if (!current || current.pointerId !== event.pointerId) return
    releasePointer(current)
    if (!current.moved) {
      if (current.deselectOnClick) onSelect(null)
      return
    }
    const target = squareAt(event.clientX, event.clientY)
    if (!target || target === current.square) {
      settle(current, current.square, true)
      return
    }

    const otimista = canSnapOptimistically?.(current.square, target) ?? false
    if (otimista) {
      settle(current, target, false)
    }

    const destination = await onDrop(current.square, target)
    if (!otimista || destination !== target) {
      settle(current, destination, destination === current.square)
    }
  }

  function cancel() {
    const current = grab.current
    if (!current) return
    releasePointer(current)
    if (current.moved) settle(current, current.square, true)
  }

  function reset() {
    const current = grab.current
    if (current) releasePointer(current)
    clearAnimation()
    tiltVelocity.current = 0
    tilt.jump(0)
    scale.jump(1)
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

  return {
    floating, hovered, isDragging, x, y,
    scale: reducedMotion ? 1 : scale,
    rotate: reducedMotion ? 0 : tilt,
    start, move, end, cancel, reset, consumeClick, preparePointer,
  }
}
