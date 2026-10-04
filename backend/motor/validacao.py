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
        tabuleiro_copia = tabuleiro.copiar()

        # Simula a jogada
        tabuleiro_copia.definir(jogada.origem, None)
        tabuleiro_copia.definir(jogada.destino, jogada.peca)

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
    tabuleiro: Tabuleiro, origem: str, destino: str
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

    # Verifica apenas os movimentos que não deixam o próprio rei em xeque
    for jogada in obter_movimentos_validos(tabuleiro, origem):
        if jogada.destino == destino:
            return jogada

    return None


def esta_em_xeque(tabuleiro: Tabuleiro, cor: Cor) -> bool:
    """Verifica se o rei da cor indicada está sendo atacado."""

    casa_rei = tabuleiro.encontrar_rei(cor)
    cor_adversaria = cor.oposta()

    for casa in tabuleiro.casas_ocupadas_por(cor_adversaria):
        movimentos = gerar_movimentos_peca(tabuleiro, casa)

        for movimento in movimentos:
            if movimento.destino == casa_rei:
                return True

    return False

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