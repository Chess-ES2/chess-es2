import { useState } from 'react'
import './App.css'
import Chessboard from './components/Chessboard/Chessboard'
import { type GamePhase, type GameMode, type BotDifficulty } from './types'

function App() {
  const [phase, setPhase] = useState<GamePhase>('menu')
  const [mode, setMode] = useState<GameMode>('local')
  const [difficulty, setDifficulty] = useState<BotDifficulty>('medium')

  const startGame = () => {
    setPhase('playing')
  }

  const voltarParaMenu = () => {
    setPhase('menu')
  }

  return (
    <div className="app-container">
      {phase === 'menu' ? (
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

          {mode === 'bot' && (
            <div className="menu-group">
              <label>Dificuldade do Bot</label>
              <select 
                value={difficulty} 
                onChange={(e) => setDifficulty(e.target.value as BotDifficulty)}
              >
                <option value="easy">Fácil</option>
                <option value="medium">Médio</option>
                <option value="hard">Difícil</option>
              </select>
            </div>
          )}

          <button className="start-button" onClick={startGame}>
            Iniciar Partida
          </button>
        </div>
      ) : (
        <Chessboard onNovaPartida={voltarParaMenu} />
      )}
    </div>
  )
}

export default App