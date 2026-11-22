from __future__ import annotations

from motor.peca import Cor, TipoPeca
from motor.tabuleiro import Tabuleiro
from ia.tabelas import (
    BONUS_POSICAO,
    PST_BRANCAS,
    PST_PRETAS,
    PST_REI_FINAL_BRANCAS,
    PST_REI_FINAL_PRETAS,
    VALOR_PECA,
)

# Convenção: a nota é sempre do ponto de vista das brancas.
# Brancas = max
# Pretas = min

BONUS_PAR_BISPOS = 30
_PESO_FASE_TOTAL = 24  # 4*1 (N) + 4*1 (B) + 4*2 (R) + 2*4 (Q)
_PESO_FASE: dict[TipoPeca, int] = {
    TipoPeca.CAVALO: 1,
    TipoPeca.BISPO: 1,
    TipoPeca.TORRE: 2,
    TipoPeca.DAMA: 4,
}


def avaliar_material(tabuleiro: Tabuleiro) -> int:
    # Soma o valor das peças brancas e subtrai o das pretas.
    nota = 0
    for peca in tabuleiro.pecas.values():
        valor = VALOR_PECA[peca.tipo]
        nota += valor if peca.cor == Cor.BRANCA else -valor
    return nota


def avaliar_posicional(tabuleiro: Tabuleiro) -> int:
    # Soma o bônus de posição das peças brancas e subtrai o das pretas.
    nota = 0
    for casa, peca in tabuleiro.pecas.items():
        if BONUS_POSICAO.get(peca.tipo) is None:
            continue
        if peca.cor == Cor.BRANCA:
            nota += PST_BRANCAS[peca.tipo][casa]
        else:
            nota -= PST_PRETAS[peca.tipo][casa]
    return nota


def avaliar(tabuleiro: Tabuleiro) -> int:
    # Nota da posição: material + bônus de posição das peças.
    return avaliar_material(tabuleiro) + avaliar_posicional(tabuleiro)


def avaliar_motor(tabuleiro: Tabuleiro) -> int:
    """Avaliação estendida usada pela busca: material + PST em passada única,
    interpolação meio-jogo/final para o Rei (tapered eval) e bônus de par de bispos."""
    nota = 0
    fase = 0
    bispos_b = 0
    bispos_p = 0
    rei_b: str | None = None
    rei_p: str | None = None

    for casa, peca in tabuleiro.pecas.items():
        tipo = peca.tipo
        fase += _PESO_FASE.get(tipo, 0)

        if peca.cor == Cor.BRANCA:
            if tipo == TipoPeca.REI:
                rei_b = casa
            else:
                nota += VALOR_PECA[tipo] + PST_BRANCAS[tipo][casa]
                if tipo == TipoPeca.BISPO:
                    bispos_b += 1
        else:
            if tipo == TipoPeca.REI:
                rei_p = casa
            else:
                nota -= VALOR_PECA[tipo] + PST_PRETAS[tipo][casa]
                if tipo == TipoPeca.BISPO:
                    bispos_p += 1

    # Interpolação da fase do jogo para o Rei (1.0 = meio-jogo, 0.0 = final)
    peso_mg = min(fase, _PESO_FASE_TOTAL)
    peso_eg = _PESO_FASE_TOTAL - peso_mg
    if rei_b is not None:
        mg = PST_BRANCAS[TipoPeca.REI][rei_b]
        eg = PST_REI_FINAL_BRANCAS[rei_b]
        nota += (mg * peso_mg + eg * peso_eg) // _PESO_FASE_TOTAL
    if rei_p is not None:
        mg = PST_PRETAS[TipoPeca.REI][rei_p]
        eg = PST_REI_FINAL_PRETAS[rei_p]
        nota -= (mg * peso_mg + eg * peso_eg) // _PESO_FASE_TOTAL

    if bispos_b >= 2:
        nota += BONUS_PAR_BISPOS
    if bispos_p >= 2:
        nota -= BONUS_PAR_BISPOS

    return nota
