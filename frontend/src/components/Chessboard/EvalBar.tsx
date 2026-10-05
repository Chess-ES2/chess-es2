import type { Color } from './types'
import './EvalBar.css'

type EvalBarProps = {
  cp: number
  turno: Color
  virado: boolean
  xequeMate: boolean
}

function formatar(cp: number) {
  return `${cp > 0 ? '+' : ''}${(cp / 100).toFixed(2)}`
}

export default function EvalBar({ cp, turno, virado, xequeMate }: EvalBarProps) {
  const brancas = xequeMate ? (turno === 'w' ? 0 : 100) : 50 + 50 * Math.tanh(cp / 400)
  const valor = xequeMate ? '#' : formatar(cp)
  const fronteira = Math.min(88, Math.max(12, virado ? brancas : 100 - brancas))

  return (
    <div
      className="eval-bar"
      role="meter"
      aria-label="Avaliação da posição"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(brancas)}
      title={`Avaliação: ${valor}`}
    >
      <div
        className={`eval-bar-parte ${virado ? 'branca' : 'preta'}`}
        style={{ height: `${virado ? brancas : 100 - brancas}%` }}
      />
      <div
        className={`eval-bar-parte ${virado ? 'preta' : 'branca'}`}
        style={{ height: `${virado ? 100 - brancas : brancas}%` }}
      />
      <span className="eval-bar-valor" style={{ top: `${fronteira}%` }}>
        {valor}
      </span>
    </div>
  )
}
