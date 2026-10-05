import { useState } from 'react'
import { motion } from 'motion/react'
import { centroDaCasa, pieceImage } from './tabuleiro'
import type { Color, PieceType, Square } from './types'
import './Promotion.css'

type PromotionProps = {
  cor: Color
  destino: Square
  virado: boolean
  onEscolher: (tipo: PieceType) => void
  onCancelar: () => void
}

const TIPOS: PieceType[] = ['q', 'r', 'b', 'n']

const nomes: Partial<Record<PieceType, string>> = {
  q: 'Dama',
  r: 'Torre',
  b: 'Bispo',
  n: 'Cavalo',
}

const RAIO = 27
const ABERTURA = 45

export default function Promotion({ cor, destino, virado, onEscolher, onCancelar }: PromotionProps) {
  const [destacado, setDestacado] = useState<PieceType | null>(null)
  const ancora = centroDaCasa(destino, virado)
  const direcao = Math.atan2(50 - ancora.y, 50 - ancora.x)
  const passo = (2 * ABERTURA) / (TIPOS.length - 1)

  const opcoes = TIPOS.map((tipo, indice) => {
    const angulo = direcao + (((indice - (TIPOS.length - 1) / 2) * passo * Math.PI) / 180)
    return {
      tipo,
      x: ancora.x + Math.cos(angulo) * RAIO,
      y: ancora.y + Math.sin(angulo) * RAIO,
    }
  })

  return (
    <div className="promotion" role="dialog" aria-label="Escolha a peça da promoção">
      <div className="promotion-fundo" onClick={onCancelar} />
      <svg className="promotion-linhas">
        {opcoes.map(({ tipo, x, y }, indice) => (
          <motion.line
            key={tipo}
            className={`promotion-linha${destacado === tipo ? ' ativa' : ''}`}
            x1={`${ancora.x}%`}
            y1={`${ancora.y}%`}
            x2={`${x}%`}
            y2={`${y}%`}
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 0.3, ease: 'easeOut', delay: 0.04 * indice }}
          />
        ))}
      </svg>
      {opcoes.map(({ tipo, x, y }, indice) => (
        <motion.button
          key={tipo}
          type="button"
          data-tipo={tipo}
          className={`promotion-opcao ${cor === 'w' ? 'branca' : 'preta'}`}
          style={{ left: `${x}%`, top: `${y}%` }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          whileHover={{ scale: 1.4, transition: { type: 'spring', duration: 0.22, bounce: 0.35 } }}
          whileTap={{ scale: 1.2 }}
          transition={{ type: 'spring', duration: 0.4, bounce: 0.4, delay: 0.05 * indice }}
          onHoverStart={() => setDestacado(tipo)}
          onHoverEnd={() => setDestacado(null)}
          onClick={() => onEscolher(tipo)}
          aria-label={`Promover para ${nomes[tipo] ?? tipo}`}
        >
          <img src={pieceImage(cor, tipo)} alt="" draggable={false} />
        </motion.button>
      ))}
    </div>
  )
}
