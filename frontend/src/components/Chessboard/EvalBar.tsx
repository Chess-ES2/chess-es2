import { useEffect, useState } from 'react'
import { motion, useMotionValueEvent, useReducedMotion, useSpring, useTransform } from 'motion/react'
import type { Color } from './types'
import './EvalBar.css'

type EvalBarProps = {
  cp: number
  turno: Color
  virado: boolean
  xequeMate: boolean
}

function formatar(cp: number) {
  const arredondado = Math.abs(cp) < 5 ? 0 : cp
  return `${arredondado > 0 ? '+' : ''}${(arredondado / 100).toFixed(2)}`
}

const SPRING_BARRA = { stiffness: 120, damping: 22, mass: 0.75 }
const SPRING_TEXTO = { stiffness: 160, damping: 26, mass: 0.6 }

export default function EvalBar({ cp, turno, virado, xequeMate }: EvalBarProps) {
  const reduzirMovimento = useReducedMotion()
  const alvoBrancas = xequeMate ? (turno === 'w' ? 0 : 100) : 50 + 50 * Math.tanh(cp / 400)

  const brancasSpring = useSpring(alvoBrancas, SPRING_BARRA)
  const cpSpring = useSpring(cp, SPRING_TEXTO)
  const [cpExibido, setCpExibido] = useState(cp)

  useEffect(() => {
    if (reduzirMovimento) {
      brancasSpring.jump(alvoBrancas)
      cpSpring.jump(cp)
    } else {
      brancasSpring.set(alvoBrancas)
      cpSpring.set(cp)
    }
  }, [alvoBrancas, cp, reduzirMovimento, brancasSpring, cpSpring])

  useMotionValueEvent(cpSpring, 'change', (v) => {
    setCpExibido(Math.round(v))
  })

  const escalaBrancas = useTransform(brancasSpring, (b) => Math.min(1, Math.max(0, b / 100)))
  const topoBadge = useTransform(brancasSpring, (b) => {
    const pos = virado ? b : 100 - b
    return `${Math.min(88, Math.max(12, pos))}%`
  })

  const valor = xequeMate ? '#' : formatar(reduzirMovimento ? cp : cpExibido)

  return (
    <div
      className="eval-bar"
      role="meter"
      aria-label="Avaliação da posição"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(alvoBrancas)}
      title={`Avaliação: ${xequeMate ? '#' : formatar(cp)}`}
    >
      <div className="eval-bar-trilha">
        <motion.div
          className="eval-bar-branca"
          style={{
            scaleY: escalaBrancas,
            transformOrigin: virado ? 'top' : 'bottom',
          }}
        />
      </div>
      <motion.span className="eval-bar-valor" style={{ top: topoBadge }}>
        {valor}
      </motion.span>
    </div>
  )
}
