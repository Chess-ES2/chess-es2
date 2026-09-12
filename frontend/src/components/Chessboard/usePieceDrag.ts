import { useEffect, useRef, useState } from 'react'
import type { PointerEvent, RefObject } from 'react'
import { animate, useMotionValue, useMotionValueEvent, useReducedMotion, useSpring, useTransform, useVelocity } from 'motion/react'
import type { Color, PieceSymbol, Square } from 'chess.js'

type DragPiece = { id: string; square: Square; color: Color; type: PieceSymbol }
type Grab = DragPiece & {
  pointerId: number
  element: HTMLButtonElement
  startX: number
  startY: number
  moved: boolean
  deselectOnClick: boolean
}

type DragOptions = {
  boardRef: RefObject<HTMLDivElement | null>
  onSelect: (square: Square | null) => void
  onDrop: (from: Square, to: Square) => Square
}

export function usePieceDrag({ boardRef, onSelect, onDrop }: DragOptions) {
  const [floating, setFloating] = useState<(DragPiece & { size: number }) | null>(null)
  const [hovered, setHovered] = useState<Square | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const grab = useRef<Grab | null>(null)
  const suppressClick = useRef(false)
  const animations = useRef<Array<{ stop: () => void }>>([])
  const generation = useRef(0)
  const reducedMotion = useReducedMotion()
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const velocity = useVelocity(x)
  const swing = useSpring(0, { stiffness: 160, damping: 12, mass: 0.7 })
  const rotate = useTransform(swing, (angle) => Math.max(-20, Math.min(20, angle)))

  useMotionValueEvent(velocity, 'change', (speed) => {
    swing.set(grab.current?.moved && !reducedMotion ? Math.max(-20, Math.min(20, -speed * 0.02)) : 0)
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
    swing.jump(0)
    suppressClick.current = true
    grab.current = {
      ...piece, pointerId: event.pointerId, element: event.currentTarget,
      startX: event.clientX, startY: event.clientY, moved: false,
      deselectOnClick: selected === piece.square,
    }
    event.currentTarget.setPointerCapture(event.pointerId)
    onSelect(piece.square)
  }

  function move(event: PointerEvent<HTMLButtonElement>) {
    const current = grab.current
    if (!current || current.pointerId !== event.pointerId) return
    if (!current.moved && Math.hypot(event.clientX - current.startX, event.clientY - current.startY) < 4) return
    const size = current.element.getBoundingClientRect().width * 0.9
    if (!current.moved) {
      current.moved = true
      x.jump(event.clientX - size / 2)
      y.jump(event.clientY + 2)
      setFloating({ id: current.id, square: current.square, color: current.color, type: current.type, size })
      setIsDragging(true)
    } else {
      x.set(event.clientX - size / 2)
      y.set(event.clientY + 2)
    }
    setHovered(squareAt(event.clientX, event.clientY))
  }

  function settle(current: Grab, square: Square) {
    setIsDragging(false)
    setHovered(null)
    swing.set(0)
    const target = boardRef.current?.querySelector<HTMLButtonElement>(`[data-square="${square}"]`)
    if (!target || reducedMotion) {
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
    swing.jump(0)
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

  return { floating, hovered, isDragging, x, y, rotate: reducedMotion ? 0 : rotate,
    start, move, end, cancel, reset, consumeClick, preparePointer }
}
