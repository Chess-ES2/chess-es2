from __future__ import annotations

from motor.peca import Cor, TipoPeca
from motor.tabuleiro import Tabuleiro
from motor.movimentacao import (
    Jogada,
    gerar_movimentos_peca,
    gerar_todos_movimentos,
)


def obter_movimentos_validos(tabuleiro: Tabuleiro, casa: str) -> list[Jogada]:
    """Retorna apenas os movimentos que não deixam o próprio rei em xeque."""

    peca = tabuleiro.obter(casa)

    if peca is None:
        return []

    movimentos = gerar_movimentos_peca(tabuleiro, casa)
    movimentos_validos = []

    for jogada in movimentos:
        # Roque não pode ser feito se o rei estiver em xeque ou passar por casas atacadas
        if jogada.e_roque:
            if esta_em_xeque(tabuleiro, peca.cor):
                continue
            cor_adv = peca.cor.oposta()
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

        tabuleiro_copia = tabuleiro.copiar()

        # Simula a jogada
        tabuleiro_copia.definir(jogada.origem, None)
        tabuleiro_copia.definir(jogada.destino, jogada.peca)

        # Simula en passant removendo o peao adversario
        if jogada.e_en_passant:
            from motor.tabuleiro import coordenadas, de_coordenadas
            col_dest, _ = coordenadas(jogada.destino)
            _, lin_orig = coordenadas(jogada.origem)
            casa_capturada = de_coordenadas(col_dest, lin_orig)
            if casa_capturada:
                tabuleiro_copia.definir(casa_capturada, None)

        # Simula roque movendo a torre junto
        if jogada.e_roque:
            from motor.peca import Peca
            if jogada.destino == "g1":
                tabuleiro_copia.definir("h1", None)
                tabuleiro_copia.definir("f1", Peca(TipoPeca.TORRE, Cor.BRANCA))
            elif jogada.destino == "c1":
                tabuleiro_copia.definir("a1", None)
                tabuleiro_copia.definir("d1", Peca(TipoPeca.TORRE, Cor.BRANCA))
            elif jogada.destino == "g8":
                tabuleiro_copia.definir("h8", None)
                tabuleiro_copia.definir("f8", Peca(TipoPeca.TORRE, Cor.PRETA))
            elif jogada.destino == "c8":
                tabuleiro_copia.definir("a8", None)
                tabuleiro_copia.definir("d8", Peca(TipoPeca.TORRE, Cor.PRETA))

        # O movimento é válido se o próprio rei não ficar em xeque
        if not esta_em_xeque(tabuleiro_copia, peca.cor):
            movimentos_validos.append(jogada)

    return movimentos_validos


def obter_todos_movimentos_validos(
    tabuleiro: Tabuleiro, cor: Cor | None = None
) -> list[Jogada]:
    """Retorna todos os movimentos legais de uma determinada cor."""

    cor_alvo = cor if cor is not None else tabuleiro.turno

    movimentos_validos = []

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
    """Verifica se a casa indicada está sob ataque de peças da cor especificada."""
    from motor.tabuleiro import coordenadas
    col_alvo, lin_alvo = coordenadas(casa)

    for casa_adv in tabuleiro.casas_ocupadas_por(por_cor):
        peca_adv = tabuleiro.obter(casa_adv)
        if peca_adv is None:
            continue
        if peca_adv.tipo == TipoPeca.PEAO:
            passo = 1 if peca_adv.cor == Cor.BRANCA else -1
            col_peao, lin_peao = coordenadas(casa_adv)
            if lin_peao + passo == lin_alvo and abs(col_peao - col_alvo) == 1:
                return True
        else:
            for mov in gerar_movimentos_peca(tabuleiro, casa_adv):
                if mov.destino == casa:
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