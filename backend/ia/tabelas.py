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
    # Rei: tabela de meio-jogo (prefere ficar protegido).
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

# Rei no final de jogo: incentiva centralização e atividade.
BONUS_REI_FINAL: list[list[int]] = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]

_COLUNAS = "abcdefgh"
_LINHAS = "12345678"

# Lookup O(1) por (tipo, casa) pré-computado para evitar cálculos de coordenadas na busca.
PST_BRANCAS: dict[TipoPeca, dict[str, int]] = {
    tipo: {
        f"{_COLUNAS[col]}{_LINHAS[lin]}": tabela[7 - lin][col]
        for lin in range(8)
        for col in range(8)
    }
    for tipo, tabela in BONUS_POSICAO.items()
}

PST_PRETAS: dict[TipoPeca, dict[str, int]] = {
    tipo: {
        f"{_COLUNAS[col]}{_LINHAS[lin]}": tabela[lin][col]
        for lin in range(8)
        for col in range(8)
    }
    for tipo, tabela in BONUS_POSICAO.items()
}

PST_REI_FINAL_BRANCAS: dict[str, int] = {
    f"{_COLUNAS[col]}{_LINHAS[lin]}": BONUS_REI_FINAL[7 - lin][col]
    for lin in range(8)
    for col in range(8)
}

PST_REI_FINAL_PRETAS: dict[str, int] = {
    f"{_COLUNAS[col]}{_LINHAS[lin]}": BONUS_REI_FINAL[lin][col]
    for lin in range(8)
    for col in range(8)
}
