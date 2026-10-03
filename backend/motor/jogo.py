from __future__ import annotations
from dataclasses import dataclass, field

from motor.peca import Cor
from motor.tabuleiro import Tabuleiro
from motor.movimentacao import Jogada
from motor.validacao import (
    obter_movimentos_validos,
    obter_todos_movimentos_validos,
    validar_movimento,
)

class JogadaInvalida(Exception):
    """Lançada quando uma jogada inválida ou fora de turno é tentada."""

@dataclass
class Jogo:
    tabuleiro: Tabuleiro = field(default_factory=Tabuleiro.inicial)

    #Construtores
    @staticmethod
    def novo() -> Jogo:
        #Inicia uma nova partida com o tabuleiro na posição inicial e vez das Brancas.
        return Jogo(tabuleiro=Tabuleiro.inicial())

    @staticmethod
    def de_fen(fen: str) -> Jogo:
        #Inicia uma partida a partir de uma posição FEN.
        return Jogo(tabuleiro=Tabuleiro.de_fen(fen))


    # Controle de turnos e consulta:

    def turno_atual(self) -> Cor:
        #Retorna a cor do jogador que deve jogar no momento
        return self.tabuleiro.turno

    def movimentos_validos(self, casa: str | None = None) -> list[Jogada]:
        #Retorna os movimentos válidos para o turno atual. Se uma casa for especificada, retorna apenas os movimentos da peça nessa casa.
    
        if casa is not None:
            peca = self.tabuleiro.obter(casa)
            if peca is None or peca.cor != self.tabuleiro.turno:
                return []
            return obter_movimentos_validos(self.tabuleiro, casa)
        return obter_todos_movimentos_validos(self.tabuleiro)

    # Execucao de jogada e alternancia de turno

    def fazer_jogada(self, origem: str, destino: str) -> Jogada:
        #Executa um movimento no tabuleiro e alterna o turno (EAP 3.6).
        jogada = validar_movimento(self.tabuleiro, origem, destino)
        if jogada is None:
            peca = self.tabuleiro.obter(origem)
            if peca is None:
                raise JogadaInvalida(f"Não há nenhuma peça na casa {origem}.")
            if peca.cor != self.tabuleiro.turno:
                cor_atual = "Brancas" if self.tabuleiro.turno == Cor.BRANCA else "Pretas"
                raise JogadaInvalida(f"É a vez das {cor_atual}. A peça em {origem} pertence ao adversário.")
            raise JogadaInvalida(f"O movimento de {origem} para {destino} não é válido para esta peça.")


        # Aplica o movimento e captura no tabuleiro (EAP 3.1, 3.3, 3.5)
        self.tabuleiro.definir(origem, None)
        self.tabuleiro.definir(destino, jogada.peca)

        # Alterna o turno entre os jogadores (EAP 3.6)
        self.tabuleiro.turno = self.tabuleiro.turno.oposta()

        return jogada

    def __repr__(self) -> str:
        turno_str = "Brancas" if self.turno_atual() == Cor.BRANCA else "Pretas"
        return f"Jogo(turno={turno_str}, fen={self.tabuleiro.para_fen()})"
