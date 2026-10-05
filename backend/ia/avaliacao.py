from __future__ import annotations

from motor.peca import Cor
from motor.tabuleiro import Tabuleiro, coordenadas
from ia.tabelas import VALOR_PECA, BONUS_POSICAO

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


def avaliar_posicional(tabuleiro: Tabuleiro) -> int:
    #Soma o bônus de posição das peças brancas e subtrai o das pretas.
    nota = 0
    for casa, peca in tabuleiro.pecas.items():
        tabela = BONUS_POSICAO.get(peca.tipo)
        if tabela is None:
            continue
        coluna, linha = coordenadas(casa)
        # "linha" 0 é a fileira 1, mas a tabela começa na fileira 8:
        # por isso as brancas usam 7 - linha e as pretas usam linha (tabela espelhada).
        if peca.cor == Cor.BRANCA:
            nota += tabela[7 - linha][coluna]
        else:
            nota -= tabela[linha][coluna]
    return nota


def avaliar(tabuleiro: Tabuleiro) -> int:
    #Nota da posição: material + bônus de posição das peças.
    return avaliar_material(tabuleiro) + avaliar_posicional(tabuleiro)
