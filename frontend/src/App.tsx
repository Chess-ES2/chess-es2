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
  const [difficultyWhite, setDifficultyWhite] = useState<BotDifficulty>('medium')
  const [difficultyBlack, setDifficultyBlack] = useState<BotDifficulty>('hard')
  const [corJogador, setCorJogador] = useState<Color>('w')

  const reduzirMovimento = useReducedMotion()
  const transicaoReveal = {
    height: reduzirMovimento
      ? { duration: 0 }
      : { type: 'spring' as const, duration: 0.45, bounce: 0 },
    opacity: { duration: reduzirMovimento ? 0 : 0.18, ease: 'easeOut' as const },
  }

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
                <div className="button-group button-group-3">
                  <button
                    className={mode === 'local' ? 'active' : ''}
                    onClick={() => setMode('local')}
                  >
                    Local
                  </button>
                  <button
                    className={mode === 'bot' ? 'active' : ''}
                    onClick={() => setMode('bot')}
                  >
                    vs Bot
                  </button>
                  <button
                    className={mode === 'bot-vs-bot' ? 'active' : ''}
                    onClick={() => setMode('bot-vs-bot')}
                  >
                    Bot vs Bot
                  </button>
                </div>
              </div>

              <AnimatePresence initial={false}>
                {mode !== 'bot-vs-bot' && (
                  <motion.div
                    key="suas-pecas"
                    className="menu-group menu-reveal"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={transicaoReveal}
                  >
                    <div className="menu-reveal-conteudo">
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
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence initial={false}>
                {mode === 'bot' && (
                  <motion.div
                    key="dificuldade"
                    className="menu-group menu-dificuldade"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={transicaoReveal}
                  >
                    <div className="menu-dificuldade-conteudo">
                      <span className="menu-dificuldade-titulo">
                        Dificuldade do Bot
                      </span>
                      <DifficultySlider valor={difficulty} aoTrocar={setDifficulty} />
                    </div>
                  </motion.div>
                )}

                {mode === 'bot-vs-bot' && (
                  <motion.div
                    key="dificuldade-dupla"
                    className="menu-group menu-dificuldade"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={transicaoReveal}
                  >
                    <div className="menu-dificuldade-conteudo menu-dificuldade-dupla">
                      <div className="bot-slot">
                        <span className="menu-dificuldade-titulo">
                          <span className="peca-opcao-icone clara" aria-hidden="true">♚</span>
                          Bot Brancas
                        </span>
                        <DifficultySlider valor={difficultyWhite} aoTrocar={setDifficultyWhite} />
                      </div>
                      <div className="bot-slot">
                        <span className="menu-dificuldade-titulo">
                          <span className="peca-opcao-icone escura" aria-hidden="true">♚</span>
                          Bot Pretas
                        </span>
                        <DifficultySlider valor={difficultyBlack} aoTrocar={setDifficultyBlack} />
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <button className="start-button" onClick={startGame}>
                {mode === 'bot-vs-bot' ? 'Assistir Partida' : 'Iniciar Partida'}
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
              <Chessboard
                mode={mode}
                difficulty={difficulty}
                difficultyWhite={difficultyWhite}
                difficultyBlack={difficultyBlack}
                corJogador={mode === 'bot-vs-bot' ? 'w' : corJogador}
                onVoltarMenu={voltarParaMenu}
                onTrocarLados={() => setCorJogador((cor) => (cor === 'w' ? 'b' : 'w'))}
              />
            </main>
          </div>
        )}
      </div>
    </MotionConfig>
  )
}

export default App
