import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent } from 'react'
import {
  animate,
  motion,
  useMotionValue,
  useMotionValueEvent,
  useReducedMotion,
  useTransform,
  type Transition,
} from 'motion/react'
import { type BotDifficulty } from '../types'
import './DifficultySlider.css'

const DIFICULDADES: { valor: BotDifficulty; rotulo: string; cor: string }[] = [
  { valor: 'easy', rotulo: 'Fácil', cor: '#4ade80' },
  { valor: 'medium', rotulo: 'Médio', cor: '#facc15' },
  { valor: 'hard', rotulo: 'Difícil', cor: '#ef4444' },
]

const PASSOS: Record<string, number> = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1 }
const TAMANHO_ESFERA = 24
const MOLA_SUAVE: Transition = { type: 'spring', duration: 0.35, bounce: 0 }

type Props = {
  valor: BotDifficulty
  aoTrocar: (valor: BotDifficulty) => void
}

// Slider com arraste contínuo entre os três estados: a esfera acompanha o ponteiro,
// a cor interpola de verde -> amarelo -> vermelho e, ao soltar, ela desliza
// suavemente (mola) até o estado mais próximo.
export default function DifficultySlider({ valor, aoTrocar }: Props) {
  const indiceAtual = DIFICULDADES.findIndex((item) => item.valor === valor)
  const reduzirMovimento = useReducedMotion()
  const [controle, setControle] = useState<HTMLDivElement | null>(null)
  const [largura, setLargura] = useState(0)
  const [arrastando, setArrastando] = useState(false)
  const arrastandoRef = useRef(false)
  const deslocamentoPressionado = useRef(0)

  const posicao = useMotionValue(indiceAtual)
  const deslocamentoMaximo = Math.max(0, largura - TAMANHO_ESFERA)
  const esferaX = useTransform(posicao, (p) => (p / (DIFICULDADES.length - 1)) * deslocamentoMaximo)
  const preenchimento = useTransform(esferaX, (x) => x + TAMANHO_ESFERA / 2)
  const corAtual = useTransform(
    posicao,
    DIFICULDADES.map((_, indice) => indice),
    DIFICULDADES.map((item) => item.cor),
  )

  const mola = reduzirMovimento ? { duration: 0 } : MOLA_SUAVE

  // Atualiza a dificuldade escolhida conforme a esfera cruza cada estado.
  useMotionValueEvent(posicao, 'change', (p) => {
    aoTrocar(DIFICULDADES[Math.round(p)].valor)
  })

  useEffect(() => {
    if (!controle) return
    const medir = () => setLargura(controle.getBoundingClientRect().width)
    medir()
    const observador = new ResizeObserver(medir)
    observador.observe(controle)
    return () => observador.disconnect()
  }, [controle])

  function posicaoDoPonteiro(clientX: number) {
    if (!controle || deslocamentoMaximo <= 0) return posicao.get()
    const retangulo = controle.getBoundingClientRect()
    const x = clientX - retangulo.left - TAMANHO_ESFERA / 2 - deslocamentoPressionado.current
    const proporcao = x / deslocamentoMaximo
    return Math.min(1, Math.max(0, proporcao)) * (DIFICULDADES.length - 1)
  }

  function aoPressionar(evento: PointerEvent<HTMLDivElement>) {
    if (!controle) return
    evento.currentTarget.setPointerCapture(evento.pointerId)
    const naEsfera = (evento.target as HTMLElement).closest('.slider-esfera') !== null

    if (naEsfera) {
      // Mantém o ponto de pega: a esfera não pula para debaixo do cursor.
      const retangulo = controle.getBoundingClientRect()
      const centroEsfera = retangulo.left + TAMANHO_ESFERA / 2 + esferaX.get()
      deslocamentoPressionado.current = evento.clientX - centroEsfera
    } else {
      deslocamentoPressionado.current = 0
      posicao.set(posicaoDoPonteiro(evento.clientX))
    }

    arrastandoRef.current = true
    setArrastando(true)
  }

  function aoMoverPonteiro(evento: PointerEvent<HTMLDivElement>) {
    if (!arrastandoRef.current) return
    posicao.set(posicaoDoPonteiro(evento.clientX))
  }

  function aoSoltarPonteiro(evento: PointerEvent<HTMLDivElement>) {
    if (!arrastandoRef.current) return
    arrastandoRef.current = false
    setArrastando(false)
    if (evento.currentTarget.hasPointerCapture(evento.pointerId)) {
      evento.currentTarget.releasePointerCapture(evento.pointerId)
    }
    animate(posicao, Math.round(posicao.get()), mola)
  }

  function aoTeclar(evento: KeyboardEvent<HTMLDivElement>) {
    const passo = PASSOS[evento.key]
    let destino: number | null = null

    if (passo) destino = Math.min(DIFICULDADES.length - 1, Math.max(0, Math.round(posicao.get()) + passo))
    if (evento.key === 'Home') destino = 0
    if (evento.key === 'End') destino = DIFICULDADES.length - 1
    if (destino === null) return

    evento.preventDefault()
    animate(posicao, destino, mola)
  }

  function selecionar(item: (typeof DIFICULDADES)[number], indice: number) {
    aoTrocar(item.valor)
    animate(posicao, indice, mola)
  }

  return (
    <div
      className="dificuldade-slider"
      style={{ '--nivel-cor': DIFICULDADES[indiceAtual].cor } as CSSProperties}
    >
      <div
        ref={setControle}
        className={`slider-controle${arrastando ? ' arrastando' : ''}`}
        onPointerDown={aoPressionar}
        onPointerMove={aoMoverPonteiro}
        onPointerUp={aoSoltarPonteiro}
        onPointerCancel={aoSoltarPonteiro}
      >
        <div className="slider-trilha" aria-hidden="true">
          <motion.span
            className="slider-preenchimento"
            style={{ width: preenchimento, backgroundColor: corAtual }}
          />
        </div>

        <motion.div
          className="slider-esfera"
          role="slider"
          tabIndex={0}
          aria-label="Dificuldade do Bot"
          aria-valuemin={0}
          aria-valuemax={DIFICULDADES.length - 1}
          aria-valuenow={indiceAtual}
          aria-valuetext={DIFICULDADES[indiceAtual].rotulo}
          style={{ x: esferaX, backgroundColor: corAtual }}
          animate={{ scale: arrastando ? 1.12 : 1 }}
          transition={mola}
          onKeyDown={aoTeclar}
        />
      </div>

      <div className="slider-rotulos">
        {DIFICULDADES.map((item, indice) => {
          const ativo = indice === indiceAtual
          return (
            <button
              key={item.valor}
              type="button"
              className={ativo ? 'ativo' : ''}
              style={ativo ? { color: item.cor } : undefined}
              aria-pressed={ativo}
              onClick={() => selecionar(item, indice)}
            >
              {item.rotulo}
            </button>
          )
        })}
      </div>
    </div>
  )
}
