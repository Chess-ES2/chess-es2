from __future__ import annotations

from motor.peca import TipoPeca

# Valores em centipeões (100 = um peão). Inteiros evitam erros de arredondamento.
VALOR_PECA: dict[TipoPeca, int] = {
    TipoPeca.PEAO:   100,
    TipoPeca.CAVALO: 320,
    TipoPeca.BISPO:  330,
    TipoPeca.TORRE:  500,
    TipoPeca.DAMA:   900,
    TipoPeca.REI:    0,   # o rei nunca é capturado, então não entra na contagem de material
}

# Bônus por casa. Cada tabela é escrita como se vê o tabuleiro,
# do ponto de vista das brancas: a primeira linha é a fileira 8 e a última é a fileira 1.
# Para as pretas a tabela é lida de cabeça para baixo (ta la em avaliar_posicional).
BONUS_POSICAO: dict[TipoPeca, list[list[int]]] = {
    TipoPeca.PEAO: [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [ 50,  50,  50,  50,  50,  50,  50,  50],
        [ 10,  10,  20,  30,  30,  20,  10,  10],
        [  5,   5,  10,  25,  25,  10,   5,   5],
        [  0,   0,   0,  20,  20,   0,   0,   0],
        [  5,  -5, -10,   0,   0, -10,  -5,   5],
        [  5,  10,  10, -20, -20,  10,  10,   5],
        [  0,   0,   0,   0,   0,   0,   0,   0],
    ],
    TipoPeca.CAVALO: [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-30,   5,  15,  20,  20,  15,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],
    ],
    TipoPeca.BISPO: [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ],
    TipoPeca.TORRE: [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [  5,  10,  10,  10,  10,  10,  10,   5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [  0,   0,   0,   5,   5,   0,   0,   0],
    ],
    TipoPeca.DAMA: [
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-10,   0,   5,   5,   5,   5,   0, -10],
        [ -5,   0,   5,   5,   5,   5,   0,  -5],
        [ -5,   0,   5,   5,   5,   5,   0,  -5],
        [-10,   0,   5,   5,   5,   5,   0, -10],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
    ],
    # Rei: tabela de meio-jogo (prefere ficar protegido). Falta a tabela de final de jogo.
    TipoPeca.REI: [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [ 20,  20,   0,   0,   0,   0,  20,  20],
        [ 20,  30,  10,   0,   0,  10,  30,  20],
    ],
}
