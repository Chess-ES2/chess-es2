import './Chessboard.css'

const initialBoard: string[][] = [
  ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
  ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
  ['', '', '', '', '', '', '', ''],
  ['', '', '', '', '', '', '', ''],
  ['', '', '', '', '', '', '', ''],
  ['', '', '', '', '', '', '', ''],
  ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
  ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr'],
]

const pieceImages: Record<string, string> = {
  br: 'https://lichess1.org/assets/piece/cburnett/bR.svg',
  bn: 'https://lichess1.org/assets/piece/cburnett/bN.svg',
  bb: 'https://lichess1.org/assets/piece/cburnett/bB.svg',
  bq: 'https://lichess1.org/assets/piece/cburnett/bQ.svg',
  bk: 'https://lichess1.org/assets/piece/cburnett/bK.svg',
  bp: 'https://lichess1.org/assets/piece/cburnett/bP.svg',
  wr: 'https://lichess1.org/assets/piece/cburnett/wR.svg',
  wn: 'https://lichess1.org/assets/piece/cburnett/wN.svg',
  wb: 'https://lichess1.org/assets/piece/cburnett/wB.svg',
  wq: 'https://lichess1.org/assets/piece/cburnett/wQ.svg',
  wk: 'https://lichess1.org/assets/piece/cburnett/wK.svg',
  wp: 'https://lichess1.org/assets/piece/cburnett/wP.svg',
}

export default function Chessboard() {
  return (
    <div className="board">
      {initialBoard.map((row, rowIndex) =>
        row.map((piece, colIndex) => {
          const isDark = (rowIndex + colIndex) % 2 === 1;
          return (
            <div key={`${rowIndex}-${colIndex}`} className={`square ${isDark ? 'dark' : 'light'}`}>
              {piece && <img src={pieceImages[piece]} alt={piece} className="piece-img" />}
            </div>
          );
        })
      )}
    </div>
  )
}