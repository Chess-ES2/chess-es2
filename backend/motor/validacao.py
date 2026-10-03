from __future__ import annotations

from motor.peca import Cor
from motor.tabuleiro import Tabuleiro
from motor.movimentacao import (
    Jogada,
    gerar_movimentos_peca,
    gerar_todos_movimentos,
)

def obter_movimentos_validos(tabuleiro: Tabuleiro, casa: str) -> list[Jogada]:
    return gerar_movimentos_peca(tabuleiro, casa)

def obter_todos_movimentos_validos(tabuleiro: Tabuleiro, cor: Cor | None = None) -> list[Jogada]:
    cor_alvo = cor if cor is not None else tabuleiro.turno
    return gerar_todos_movimentos(tabuleiro, cor_alvo)

def validar_movimento(tabuleiro: Tabuleiro, origem: str, destino: str) -> Jogada | None:

    """Realiza as verificações:
    1. A casa de origem contém uma peça?
    2. A peça na origem pertence ao jogador da vez (tabuleiro.turno)?
    3. O destino corresponde a um movimento ou captura válido para a peça?
    Retorna o objeto Jogada se o movimento for válido; caso contrário, retorna None."""

    peca = tabuleiro.obter(origem)
    if peca is None:
        return None

    # A peça precisa ser da cor do turno atual
    if peca.cor != tabuleiro.turno:
        return None

    # Verifica se o destino está entre os movimentos/capturas possíveis da peça
    for jogada in gerar_movimentos_peca(tabuleiro, origem):
        if jogada.destino == destino:
            return jogada

    return None
