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

# Bônus por casa, em centipeões. Cada tabela é escrita como se vê o tabuleiro,
# do ponto de vista das brancas: a primeira linha é a fileira 8 e a última é a fileira 1.
# Para as pretas a tabela é lida de cabeça para baixo (ver avaliar_posicional).
# Peças sem tabela ainda não recebem bônus de posição.
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
}
