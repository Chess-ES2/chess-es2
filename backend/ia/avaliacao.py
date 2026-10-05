from __future__ import annotations

from motor.peca import Cor
from motor.tabuleiro import Tabuleiro
from ia.tabelas import VALOR_PECA

# Convenção: a nota é sempre do ponto de vista das brancas.
# Brancas = max
# Pretas = min

def avaliar_material(tabuleiro: Tabuleiro) -> int:
    #Soma o valor das peças brancas e subtrai o das pretas.
    nota = 0
    for peca in tabuleiro.pecas.values():
        valor = VALOR_PECA[peca.tipo]
        nota += valor if peca.cor == Cor.BRANCA else -valor
    return nota


def avaliar(tabuleiro: Tabuleiro) -> int:
    #Nota da posição. Por enquanto considera apenas o material.
    return avaliar_material(tabuleiro)
