from __future__ import annotations

from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro, _COORD_PARA_CASA, coordenadas, de_coordenadas
from motor.movimentacao import (
    Jogada,
    gerar_movimentos_peca,
    gerar_todos_movimentos,
)

_SALTOS_CAVALO = (
    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
    ( 1, -2), ( 1, 2), ( 2, -1), ( 2, 1),
)
_PASSOS_REI = (
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
)
_RAIOS_ORTOGONAIS = ((-1, 0), (1, 0), (0, -1), (0, 1))
_RAIOS_DIAGONAIS = ((-1, -1), (-1, 1), (1, -1), (1, 1))

_ROQUE_TORRES: dict[str, tuple[str, str, Cor]] = {
    "g1": ("h1", "f1", Cor.BRANCA),
    "c1": ("a1", "d1", Cor.BRANCA),
    "g8": ("h8", "f8", Cor.PRETA),
    "c8": ("a8", "d8", Cor.PRETA),
}


def obter_movimentos_validos(tabuleiro: Tabuleiro, casa: str) -> list[Jogada]:
    """Retorna apenas os movimentos que não deixam o próprio rei em xeque."""

    peca = tabuleiro.obter(casa)

    if peca is None:
        return []

    movimentos = gerar_movimentos_peca(tabuleiro, casa)
    movimentos_validos: list[Jogada] = []
    pecas = tabuleiro.pecas
    cor = peca.cor
    cor_adv = cor.oposta()

    for jogada in movimentos:
        # Roque não pode ser feito se o rei estiver em xeque ou passar por casas atacadas
        if jogada.e_roque:
            if esta_em_xeque(tabuleiro, cor):
                continue
            if jogada.destino == "g1":
                if casa_sob_ataque(tabuleiro, "f1", cor_adv) or casa_sob_ataque(tabuleiro, "g1", cor_adv):
                    continue
            elif jogada.destino == "c1":
                if casa_sob_ataque(tabuleiro, "d1", cor_adv) or casa_sob_ataque(tabuleiro, "c1", cor_adv):
                    continue
            elif jogada.destino == "g8":
                if casa_sob_ataque(tabuleiro, "f8", cor_adv) or casa_sob_ataque(tabuleiro, "g8", cor_adv):
                    continue
            elif jogada.destino == "c8":
                if casa_sob_ataque(tabuleiro, "d8", cor_adv) or casa_sob_ataque(tabuleiro, "c8", cor_adv):
                    continue

        # Simulação in-place (make/unmake) sem alocar cópia do Tabuleiro
        origem = jogada.origem
        destino = jogada.destino
        peca_origem = pecas.pop(origem, None)
        peca_destino = pecas.get(destino)
        pecas[destino] = jogada.peca

        casa_ep: str | None = None
        peca_ep: Peca | None = None
        if jogada.e_en_passant:
            col_dest, _ = coordenadas(destino)
            _, lin_orig = coordenadas(origem)
            casa_ep = _COORD_PARA_CASA[lin_orig][col_dest]
            peca_ep = pecas.pop(casa_ep, None)

        torre_orig: str | None = None
        torre_dest: str | None = None
        peca_torre: Peca | None = None
        if jogada.e_roque:
            torre_orig, torre_dest, cor_torre = _ROQUE_TORRES[destino]
            peca_torre = pecas.pop(torre_orig, None)
            pecas[torre_dest] = peca_torre or Peca(TipoPeca.TORRE, cor_torre)

        try:
            if not esta_em_xeque(tabuleiro, cor):
                movimentos_validos.append(jogada)
        finally:
            # Desfaz a simulação in-place
            if torre_orig is not None and torre_dest is not None:
                pecas.pop(torre_dest, None)
                if peca_torre is not None:
                    pecas[torre_orig] = peca_torre
            if casa_ep is not None and peca_ep is not None:
                pecas[casa_ep] = peca_ep
            if peca_destino is None:
                pecas.pop(destino, None)
            else:
                pecas[destino] = peca_destino
            if peca_origem is not None:
                pecas[origem] = peca_origem

    return movimentos_validos


def obter_todos_movimentos_validos(
    tabuleiro: Tabuleiro, cor: Cor | None = None
) -> list[Jogada]:
    """Retorna todos os movimentos legais de uma determinada cor."""

    cor_alvo = cor if cor is not None else tabuleiro.turno

    movimentos_validos: list[Jogada] = []

    for casa in tabuleiro.casas_ocupadas_por(cor_alvo):
        movimentos_validos.extend(
            obter_movimentos_validos(tabuleiro, casa)
        )

    return movimentos_validos


def validar_movimento(
    tabuleiro: Tabuleiro, origem: str, destino: str, promocao: TipoPeca | None = None
) -> Jogada | None:
    """Realiza as verificações:

    1. A casa de origem contém uma peça?
    2. A peça na origem pertence ao jogador da vez?
    3. O destino corresponde a um movimento válido para a peça?
    4. A jogada não deixa o próprio rei em xeque.

    Retorna o objeto Jogada se o movimento for válido.
    Caso contrário, retorna None.
    """

    peca = tabuleiro.obter(origem)

    if peca is None:
        return None

    # A peça precisa ser da cor do turno atual
    if peca.cor != tabuleiro.turno:
        return None

    candidatas = [j for j in obter_movimentos_validos(tabuleiro, origem) if j.destino == destino]
    if not candidatas:
        return None

    if candidatas[0].promocao is not None:
        tipo_escolhido = promocao if promocao is not None else TipoPeca.DAMA
        for c in candidatas:
            if c.promocao == tipo_escolhido:
                return c
        return candidatas[0]

    return candidatas[0]


def casa_sob_ataque(tabuleiro: Tabuleiro, casa: str, por_cor: Cor) -> bool:
    """Verifica se a casa indicada está sob ataque de peças da cor especificada.
    Usa busca reversa a partir da casa alvo sem alocar objetos Jogada."""
    col_alvo, lin_alvo = coordenadas(casa)
    pecas = tabuleiro.pecas
    coord_para_casa = _COORD_PARA_CASA

    # 1. Peões atacantes (um peão branco ataca subindo +1, logo vem de lin_alvo - 1)
    lin_peao = lin_alvo - 1 if por_cor == Cor.BRANCA else lin_alvo + 1
    if 0 <= lin_peao <= 7:
        linha_casas = coord_para_casa[lin_peao]
        if col_alvo > 0:
            p = pecas.get(linha_casas[col_alvo - 1])
            if p is not None and p.cor == por_cor and p.tipo == TipoPeca.PEAO:
                return True
        if col_alvo < 7:
            p = pecas.get(linha_casas[col_alvo + 1])
            if p is not None and p.cor == por_cor and p.tipo == TipoPeca.PEAO:
                return True

    # 2. Cavalos atacantes
    for dc, dl in _SALTOS_CAVALO:
        c = col_alvo + dc
        l = lin_alvo + dl
        if 0 <= c <= 7 and 0 <= l <= 7:
            p = pecas.get(coord_para_casa[l][c])
            if p is not None and p.cor == por_cor and p.tipo == TipoPeca.CAVALO:
                return True

    # 3. Raios ortogonais (Torre / Dama)
    for dc, dl in _RAIOS_ORTOGONAIS:
        c = col_alvo + dc
        l = lin_alvo + dl
        while 0 <= c <= 7 and 0 <= l <= 7:
            p = pecas.get(coord_para_casa[l][c])
            if p is not None:
                if p.cor == por_cor and (p.tipo == TipoPeca.TORRE or p.tipo == TipoPeca.DAMA):
                    return True
                break
            c += dc
            l += dl

    # 4. Raios diagonais (Bispo / Dama)
    for dc, dl in _RAIOS_DIAGONAIS:
        c = col_alvo + dc
        l = lin_alvo + dl
        while 0 <= c <= 7 and 0 <= l <= 7:
            p = pecas.get(coord_para_casa[l][c])
            if p is not None:
                if p.cor == por_cor and (p.tipo == TipoPeca.BISPO or p.tipo == TipoPeca.DAMA):
                    return True
                break
            c += dc
            l += dl

    # 5. Rei adjacente
    for dc, dl in _PASSOS_REI:
        c = col_alvo + dc
        l = lin_alvo + dl
        if 0 <= c <= 7 and 0 <= l <= 7:
            p = pecas.get(coord_para_casa[l][c])
            if p is not None and p.cor == por_cor and p.tipo == TipoPeca.REI:
                return True

    return False


def esta_em_xeque(tabuleiro: Tabuleiro, cor: Cor) -> bool:
    """Verifica se o rei da cor indicada está sendo atacado."""

    casa_rei = tabuleiro.encontrar_rei(cor)
    return casa_sob_ataque(tabuleiro, casa_rei, cor.oposta())


def esta_em_xeque_mate(tabuleiro: Tabuleiro, cor: Cor) -> bool:

    # Para existir xeque-mate, primeiro o rei precisa estar em xeque.
    if not esta_em_xeque(tabuleiro, cor):
        return False

    # Se existir pelo menos um movimento legal, ainda não é xeque-mate.
    movimentos = obter_todos_movimentos_validos(tabuleiro, cor)

    return len(movimentos) == 0

def esta_em_afogamento(tabuleiro: Tabuleiro, cor: Cor) -> bool:
    """Verifica se o jogador está em situação de afogamento (stalemate)."""

    # Se o rei está em xeque, não é afogamento.
    if esta_em_xeque(tabuleiro, cor):
        return False

    # Sem movimentos legais e sem estar em xeque = empate por afogamento.
    movimentos = obter_todos_movimentos_validos(tabuleiro, cor)

    return len(movimentos) == 0

def empate_por_material_insuficiente(tabuleiro: Tabuleiro) -> bool:
    """Verifica se o material restante é insuficiente para xeque-mate."""

    pecas = list(tabuleiro.pecas.values())

    pecas_sem_reis = [
        peca for peca in pecas
        if peca.tipo != TipoPeca.REI
    ]

    # Rei contra rei.
    if len(pecas_sem_reis) == 0:
        return True

    # Rei + bispo contra rei
    # ou rei + cavalo contra rei.
    if len(pecas_sem_reis) == 1:
        return pecas_sem_reis[0].tipo in (
            TipoPeca.BISPO,
            TipoPeca.CAVALO,
        )

    # Rei + bispo contra rei + bispo.
    # Só é material insuficiente quando os dois bispos
    # estão na mesma cor de casa.
    if len(pecas_sem_reis) == 2:
        if all(peca.tipo == TipoPeca.BISPO for peca in pecas_sem_reis):
            casas_bispos = [
                casa
                for casa, peca in tabuleiro.pecas.items()
                if peca.tipo == TipoPeca.BISPO
            ]

            return _casa_e_mesma_cor(casas_bispos[0], casas_bispos[1])

    return False

def _casa_e_mesma_cor(casa_a: str, casa_b: str) -> bool:
    """Verifica se duas casas possuem a mesma cor."""

    coluna_a = ord(casa_a[0]) - ord("a")
    linha_a = int(casa_a[1]) - 1

    coluna_b = ord(casa_b[0]) - ord("a")
    linha_b = int(casa_b[1]) - 1

    return (coluna_a + linha_a) % 2 == (coluna_b + linha_b) % 2

def ocorre_repeticao_tripla(historico_posicoes: list[str]) -> bool:
    """Verifica se alguma posição ocorreu pelo menos três vezes."""

    for posicao in set(historico_posicoes):
        if historico_posicoes.count(posicao) >= 3:
            return True

    return False
