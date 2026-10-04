import { useState } from 'react'
import { AnimatePresence, MotionConfig, motion, useReducedMotion } from 'motion/react'
import './App.css'
import Chessboard from './components/Chessboard/Chessboard'
import DifficultySlider from './components/DifficultySlider'
import { type Color } from './components/Chessboard/types'
import { type GamePhase, type GameMode, type BotDifficulty } from './types'

function App() {
  const [phase, setPhase] = useState<GamePhase>('menu')
  const [mode, setMode] = useState<GameMode>('local')
  const [difficulty, setDifficulty] = useState<BotDifficulty>('medium')
  const [corJogador, setCorJogador] = useState<Color>('w')

  const reduzirMovimento = useReducedMotion()

  const startGame = () => setPhase('playing')
  const voltarParaMenu = () => setPhase('menu')

  return (
    <MotionConfig reducedMotion="user">
      <div className="app-container">
        {phase === 'menu' ? (
          <div className="menu-wrapper">
            <div className="menu-container">
              <h1>Xadrez - ES2</h1>

              <div className="menu-group">
                <label>Modo de Jogo</label>
                <div className="button-group">
                  <button
                    className={mode === 'local' ? 'active' : ''}
                    onClick={() => setMode('local')}
                  >
                    Multijogador Local
                  </button>
                  <button
                    className={mode === 'bot' ? 'active' : ''}
                    onClick={() => setMode('bot')}
                  >
                    Contra o Bot
                  </button>
                </div>
              </div>

              <div className="menu-group">
                <label>Suas Peças</label>
                <div className="button-group">
                  <button
                    className={corJogador === 'w' ? 'active' : ''}
                    onClick={() => setCorJogador('w')}
                  >
                    <span className="peca-opcao-icone clara" aria-hidden="true">♚</span>
                    Brancas
                  </button>
                  <button
                    className={corJogador === 'b' ? 'active' : ''}
                    onClick={() => setCorJogador('b')}
                  >
                    <span className="peca-opcao-icone escura" aria-hidden="true">♚</span>
                    Pretas
                  </button>
                </div>
              </div>

              <AnimatePresence initial={false}>
                {mode === 'bot' && (
                  <motion.div
                    key="dificuldade"
                    className="menu-group menu-dificuldade"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{
                      height: reduzirMovimento
                        ? { duration: 0 }
                        : { type: 'spring', duration: 0.45, bounce: 0 },
                      opacity: { duration: reduzirMovimento ? 0 : 0.18, ease: 'easeOut' },
                    }}
                  >
                    <div className="menu-dificuldade-conteudo">
                      <motion.span
                        className="menu-dificuldade-titulo"
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ type: 'spring', duration: 0.4, bounce: 0, delay: 0.05 }}
                      >
                        Dificuldade do Bot
                      </motion.span>

                      <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ type: 'spring', duration: 0.4, bounce: 0, delay: 0.1 }}
                      >
                        <DifficultySlider valor={difficulty} aoTrocar={setDifficulty} />
                      </motion.div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <button className="start-button" onClick={startGame}>
                Iniciar Partida
              </button>
            </div>
          </div>
        ) : (
          <div className="game-view">
            <header className="top-bar">
              <h2>Xadrez - ES2</h2>
              <button className="voltar-btn" onClick={voltarParaMenu}>
                Menu Principal
              </button>
            </header>

            <main className="game-content">
              <Chessboard mode={mode} difficulty={difficulty} corJogador={corJogador} />
            </main>
          </div>
        )}
      </div>
    </MotionConfig>
  )
}

export default App
