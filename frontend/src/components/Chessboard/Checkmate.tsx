import { motion } from 'motion/react'
import type { Color } from './types'
import './Checkmate.css'

type CheckmateProps = {
  vencedor: Color
  onVerTabuleiro: () => void
  onVoltarMenu: () => void
  onTrocarLados: () => void
}

export default function Checkmate({
  vencedor,
  onVerTabuleiro,
  onVoltarMenu,
  onTrocarLados,
}: CheckmateProps) {
  return (
    <motion.div
      className="checkmate-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.18 }}
    >
      <motion.div
        className="checkmate-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="checkmate-titulo"
        initial={{ scale: 0.9, y: 14 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, opacity: 0 }}
        transition={{ type: 'spring', duration: 0.4, bounce: 0.25 }}
      >
        <h1 id="checkmate-titulo">Xeque-mate</h1>
        <p className="checkmate-vencedor">
          {vencedor === 'w' ? 'As brancas venceram' : 'As pretas venceram'}
        </p>

        <div className="checkmate-acoes">
          <div className="checkmate-linha">
            <button type="button" className="checkmate-secundario" onClick={onVerTabuleiro}>
              Ver Tabuleiro
            </button>
            <button type="button" className="checkmate-secundario" onClick={onVoltarMenu}>
              Menu Principal
            </button>
          </div>

          <div className="checkmate-linha">
            <button type="button" className="checkmate-revanche" onClick={onTrocarLados}>
              Revanche
            </button>
            <span className="checkmate-dica">
              <button
                type="button"
                className="checkmate-ajuda"
                aria-label="A revanche troca os lados da partida"
              >
                ?
              </button>
              <span className="checkmate-dica-texto" role="tooltip">
                A revanche troca os lados da partida
              </span>
            </span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
