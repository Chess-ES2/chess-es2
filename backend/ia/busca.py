from __future__ import annotations

from ia.avaliacao import avaliar
from motor.jogo import aplicar_jogada
from motor.movimentacao import Jogada
from motor.peca import Cor
from motor.tabuleiro import Tabuleiro
from motor.validacao import esta_em_xeque, obter_todos_movimentos_validos

VALOR_XEQUE_MATE = 1_000_000

PROFUNDIDADES = {"easy": 1, "medium": 2, "hard": 3}


def _nota(tabuleiro: Tabuleiro) -> int:
    # Negamax: a nota é sempre do ponto de vista de quem tem o turno.
    nota = avaliar(tabuleiro)
    return nota if tabuleiro.turno == Cor.BRANCA else -nota


def _ordenar(movimentos: list[Jogada]) -> list[Jogada]:
    # Capturas e promoções primeiro: rendem cortes melhores no alpha-beta.
    return sorted(
        movimentos,
        key=lambda jogada: (jogada.captura is not None, jogada.promocao is not None),
        reverse=True,
    )


def _negamax(tabuleiro: Tabuleiro, profundidade: int, alpha: int, beta: int) -> int:
    if profundidade == 0:
        return _nota(tabuleiro)

    movimentos = obter_todos_movimentos_validos(tabuleiro)
    if not movimentos:
        if esta_em_xeque(tabuleiro, tabuleiro.turno):
            return -VALOR_XEQUE_MATE - profundidade
        return 0

    valor = -VALOR_XEQUE_MATE * 2
    for jogada in _ordenar(movimentos):
        copia = tabuleiro.copiar()
        aplicar_jogada(copia, jogada)
        valor = max(valor, -_negamax(copia, profundidade - 1, -beta, -alpha))
        alpha = max(alpha, valor)
        if alpha >= beta:
            break
    return valor


def melhor_jogada(tabuleiro: Tabuleiro, profundidade: int) -> Jogada | None:
    movimentos = obter_todos_movimentos_validos(tabuleiro)
    if not movimentos:
        return None

    melhor = movimentos[0]
    alpha = -VALOR_XEQUE_MATE * 2
    for jogada in _ordenar(movimentos):
        copia = tabuleiro.copiar()
        aplicar_jogada(copia, jogada)
        valor = -_negamax(copia, profundidade - 1, -VALOR_XEQUE_MATE * 2, -alpha)
        if valor > alpha:
            alpha = valor
            melhor = jogada
    return melhor
