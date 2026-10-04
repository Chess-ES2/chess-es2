from __future__ import annotations
from dataclasses import dataclass, field

from motor.peca import Cor
from motor.tabuleiro import Tabuleiro
from motor.movimentacao import Jogada
from motor.validacao import (
    obter_movimentos_validos,
    obter_todos_movimentos_validos,
    validar_movimento,
    esta_em_xeque,
    esta_em_xeque_mate,
    esta_em_afogamento,
    empate_por_material_insuficiente,
    ocorre_repeticao_tripla,
)

class JogadaInvalida(Exception):
    """Lançada quando uma jogada inválida ou fora de turno é tentada."""

@dataclass
class Jogo:
    tabuleiro: Tabuleiro = field(default_factory=Tabuleiro.inicial)
    historico: list[Jogada] = field(default_factory=list)
    historico_posicoes: list[str] = field(default_factory=list)

    #Construtores
    @staticmethod
    def novo() -> Jogo:
        #Inicia uma nova partida com o tabuleiro na posição inicial e vez das Brancas.
        return Jogo(tabuleiro=Tabuleiro.inicial())

    @staticmethod
    def de_fen(fen: str) -> Jogo:
        #Inicia uma partida a partir de uma posição FEN.
        return Jogo(tabuleiro=Tabuleiro.de_fen(fen))

    def __post_init__(self):
        self.historico_posicoes.append(self.tabuleiro.para_fen())

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


        self.tabuleiro.definir(origem, None)
        self.tabuleiro.definir(destino, jogada.peca)
        self.tabuleiro.turno = self.tabuleiro.turno.oposta()

        self.historico.append(jogada)
        self.historico_posicoes.append(self.tabuleiro.para_fen())

        return jogada

    def obter_historico_posicoes(self) -> list[str]:
        """Retorna as posições do tabuleiro registradas durante a partida."""
        return list(self.historico_posicoes)

    def obter_historico(self) -> list[Jogada]:
        """Retorna o histórico das jogadas realizadas."""
        return list(self.historico)

    def esta_em_xeque(self) -> bool:
        """Verifica se o jogador do turno atual está em xeque."""
        return esta_em_xeque(self.tabuleiro, self.tabuleiro.turno)

    def esta_em_xeque_mate(self) -> bool:
        """Verifica se o jogador do turno atual está em xeque-mate."""
        return esta_em_xeque_mate(self.tabuleiro, self.tabuleiro.turno)

    def esta_em_afogamento(self) -> bool:
        """Verifica se o jogador do turno atual está em afogamento."""
        return esta_em_afogamento(self.tabuleiro, self.tabuleiro.turno)

    def empate_por_material_insuficiente(self) -> bool:
        """Verifica se a partida terminou por material insuficiente."""
        return empate_por_material_insuficiente(self.tabuleiro)

    def ocorre_repeticao_tripla(self) -> bool:
        """Verifica se alguma posição ocorreu pelo menos três vezes."""
        return ocorre_repeticao_tripla(self.historico_posicoes)

    def __repr__(self) -> str:
        turno_str = "Brancas" if self.turno_atual() == Cor.BRANCA else "Pretas"
        return f"Jogo(turno={turno_str}, fen={self.tabuleiro.para_fen()})"
