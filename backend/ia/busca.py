from __future__ import annotations

import random
import time
from dataclasses import dataclass

from ia.aberturas import consultar_livro
from ia.avaliacao import avaliar_motor
from ia.tabelas import VALOR_PECA
from motor.jogo import aplicar_jogada
from motor.movimentacao import Jogada
from motor.peca import Cor, TipoPeca
from motor.tabuleiro import COLUNAS, LINHAS, Tabuleiro
from motor.validacao import esta_em_xeque, obter_todos_movimentos_validos

VALOR_XEQUE_MATE = 1_000_000
_INFINITO = VALOR_XEQUE_MATE * 2

# Mantido por compatibilidade com código/testes existentes
PROFUNDIDADES: dict[str, int] = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "expert": 5,
}


@dataclass(frozen=True)
class ConfigDificuldade:
    profundidade_max: int
    tempo_limite_ms: int
    quiescencia: bool = True
    usar_livro: bool = True


CONFIG_DIFICULDADES: dict[str, ConfigDificuldade] = {
    "easy":   ConfigDificuldade(profundidade_max=1, tempo_limite_ms=150,  quiescencia=False, usar_livro=True),
    "medium": ConfigDificuldade(profundidade_max=2, tempo_limite_ms=300,  quiescencia=True,  usar_livro=True),
    "hard":   ConfigDificuldade(profundidade_max=3, tempo_limite_ms=650,  quiescencia=True,  usar_livro=True),
    "expert": ConfigDificuldade(profundidade_max=5, tempo_limite_ms=1400, quiescencia=True,  usar_livro=True),
}

# Flags da Tabela de Transposição
_TT_EXACT = 0
_TT_LOWER = 1
_TT_UPPER = 2
_TT_MAX_ENTRADAS = 65_536

# Zobrist Hashing (semente fixa para determinismo)
_rng = random.Random(20260401)
_CASAS = [f"{c}{l}" for l in LINHAS for c in COLUNAS]
_ZOBRIST_PECA: dict[tuple[str, TipoPeca, Cor], int] = {
    (casa, tipo, cor): _rng.getrandbits(64)
    for casa in _CASAS
    for tipo in TipoPeca
    for cor in Cor
}
_ZOBRIST_TURNO_PRETO: int = _rng.getrandbits(64)
_ZOBRIST_ROQUE: dict[str, int] = {k: _rng.getrandbits(64) for k in ("K", "Q", "k", "q")}
_ZOBRIST_EP: dict[str, int] = {casa: _rng.getrandbits(64) for casa in _CASAS}

_TT: dict[int, tuple[int, int, int, tuple[str, str, TipoPeca | None] | None]] = {}


def hash_zobrist(tabuleiro: Tabuleiro) -> int:
    h = 0
    for casa, peca in tabuleiro.pecas.items():
        h ^= _ZOBRIST_PECA[(casa, peca.tipo, peca.cor)]
    if tabuleiro.turno == Cor.PRETA:
        h ^= _ZOBRIST_TURNO_PRETO
    for k, ativo in tabuleiro.direitos_roque.items():
        if ativo:
            h ^= _ZOBRIST_ROQUE[k]
    if tabuleiro.casa_en_passant is not None:
        h ^= _ZOBRIST_EP[tabuleiro.casa_en_passant]
    return h


def _chave_jogada(jogada: Jogada) -> tuple[str, str, TipoPeca | None]:
    return (jogada.origem, jogada.destino, jogada.promocao)


def _nota(tabuleiro: Tabuleiro) -> int:
    # Negamax: a nota é sempre do ponto de vista de quem tem o turno.
    nota = avaliar_motor(tabuleiro)
    return nota if tabuleiro.turno == Cor.BRANCA else -nota


def _pontuar_jogada(
    jogada: Jogada,
    chave_tt: tuple[str, str, TipoPeca | None] | None,
    killers: list[tuple[str, str, TipoPeca | None]],
) -> int:
    chave = _chave_jogada(jogada)
    if chave_tt is not None and chave == chave_tt:
        return 100_000
    score = 0
    if jogada.captura is not None:
        # MVV-LVA: prioriza capturar peças valiosas com peças baratas
        score += 10_000 + 10 * VALOR_PECA[jogada.captura.tipo] - VALOR_PECA[jogada.peca.tipo]
    if jogada.promocao is not None:
        score += 9_000 + VALOR_PECA[jogada.promocao]
    if score == 0 and killers:
        if chave == killers[0]:
            return 8_000
        if len(killers) > 1 and chave == killers[1]:
            return 7_500
    return score


def _ordenar(
    movimentos: list[Jogada],
    chave_tt: tuple[str, str, TipoPeca | None] | None = None,
    killers: list[tuple[str, str, TipoPeca | None]] | None = None,
) -> list[Jogada]:
    if len(movimentos) <= 1:
        return movimentos
    ks = killers or []
    return sorted(
        movimentos,
        key=lambda j: _pontuar_jogada(j, chave_tt, ks),
        reverse=True,
    )


class _TempoEsgotado(Exception):
    pass


class _ContextoBusca:
    __slots__ = ("prazo", "quiescencia", "nos", "killers")

    def __init__(self, tempo_limite_ms: float | None, quiescencia: bool) -> None:
        self.prazo: float | None = (
            time.perf_counter() + tempo_limite_ms / 1000.0
            if tempo_limite_ms is not None
            else None
        )
        self.quiescencia = quiescencia
        self.nos = 0
        self.killers: dict[int, list[tuple[str, str, TipoPeca | None]]] = {}

    def checar_tempo(self) -> None:
        self.nos += 1
        if self.prazo is not None and (self.nos & 127) == 0:
            if time.perf_counter() >= self.prazo:
                raise _TempoEsgotado()

    def registrar_killer(self, ply: int, jogada: Jogada) -> None:
        if jogada.captura is not None or jogada.promocao is not None:
            return
        chave = _chave_jogada(jogada)
        lista = self.killers.get(ply)
        if lista is None:
            self.killers[ply] = [chave]
        elif lista[0] != chave:
            self.killers[ply] = [chave, lista[0]]


def _quiescencia(
    tabuleiro: Tabuleiro,
    alpha: int,
    beta: int,
    ctx: _ContextoBusca,
    qply: int = 0,
) -> int:
    ctx.checar_tempo()

    stand_pat = _nota(tabuleiro)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    if qply >= 6:
        return alpha

    # Busca apenas capturas e promoções para eliminar efeito horizonte
    movimentos = [
        j for j in obter_todos_movimentos_validos(tabuleiro)
        if j.captura is not None or j.promocao == TipoPeca.DAMA
    ]
    if not movimentos:
        return alpha

    for jogada in _ordenar(movimentos):
        copia = tabuleiro.copiar()
        aplicar_jogada(copia, jogada)
        valor = -_quiescencia(copia, -beta, -alpha, ctx, qply + 1)
        if valor >= beta:
            return beta
        if valor > alpha:
            alpha = valor

    return alpha


def _negamax(
    tabuleiro: Tabuleiro,
    profundidade: int,
    alpha: int,
    beta: int,
    ctx: _ContextoBusca,
    ply: int = 0,
) -> int:
    ctx.checar_tempo()

    alpha_orig = alpha
    h = hash_zobrist(tabuleiro)
    entrada = _TT.get(h)
    chave_tt: tuple[str, str, TipoPeca | None] | None = None

    if entrada is not None:
        tt_prof, tt_val, tt_flag, chave_tt = entrada
        if tt_prof >= profundidade:
            if tt_flag == _TT_EXACT:
                return tt_val
            if tt_flag == _TT_LOWER:
                alpha = max(alpha, tt_val)
            elif tt_flag == _TT_UPPER:
                beta = min(beta, tt_val)
            if alpha >= beta:
                return tt_val

    if profundidade == 0:
        if ctx.quiescencia:
            return _quiescencia(tabuleiro, alpha, beta, ctx)
        return _nota(tabuleiro)

    movimentos = obter_todos_movimentos_validos(tabuleiro)
    if not movimentos:
        if esta_em_xeque(tabuleiro, tabuleiro.turno):
            return -VALOR_XEQUE_MATE - profundidade
        return 0

    melhor_valor = -_INFINITO
    melhor_chave: tuple[str, str, TipoPeca | None] | None = None
    killers_ply = ctx.killers.get(ply)

    for jogada in _ordenar(movimentos, chave_tt, killers_ply):
        copia = tabuleiro.copiar()
        aplicar_jogada(copia, jogada)
        valor = -_negamax(copia, profundidade - 1, -beta, -alpha, ctx, ply + 1)
        if valor > melhor_valor:
            melhor_valor = valor
            melhor_chave = _chave_jogada(jogada)
        if valor > alpha:
            alpha = valor
        if alpha >= beta:
            ctx.registrar_killer(ply, jogada)
            break

    if len(_TT) >= _TT_MAX_ENTRADAS:
        _TT.clear()

    if melhor_valor <= alpha_orig:
        flag = _TT_UPPER
    elif melhor_valor >= beta:
        flag = _TT_LOWER
    else:
        flag = _TT_EXACT
    _TT[h] = (profundidade, melhor_valor, flag, melhor_chave)

    return melhor_valor


def _buscar_raiz(
    tabuleiro: Tabuleiro,
    movimentos: list[Jogada],
    profundidade: int,
    ctx: _ContextoBusca,
    melhor_anterior: Jogada | None = None,
) -> tuple[Jogada, int]:
    chave_tt = _chave_jogada(melhor_anterior) if melhor_anterior is not None else None
    if chave_tt is None:
        entrada = _TT.get(hash_zobrist(tabuleiro))
        if entrada is not None:
            chave_tt = entrada[3]

    ordenadas = _ordenar(movimentos, chave_tt)
    melhor = ordenadas[0]
    alpha = -_INFINITO
    beta = _INFINITO

    for jogada in ordenadas:
        copia = tabuleiro.copiar()
        aplicar_jogada(copia, jogada)
        valor = -_negamax(copia, profundidade - 1, -beta, -alpha, ctx, 1)
        if valor > alpha:
            alpha = valor
            melhor = jogada

    return melhor, alpha


def melhor_jogada(
    tabuleiro: Tabuleiro,
    profundidade: int,
    *,
    tempo_limite_ms: float | None = None,
    usar_quiescencia: bool = True,
    usar_livro: bool = True,
) -> Jogada | None:
    movimentos = obter_todos_movimentos_validos(tabuleiro)
    if not movimentos:
        return None
    if len(movimentos) == 1:
        return movimentos[0]

    if usar_livro:
        fen_atual = tabuleiro.para_fen()
        lance_livro = consultar_livro(fen_atual, movimentos)
        if lance_livro is not None:
            return lance_livro

    # Iterative Deepening: sempre completa profundidade 1; aprofunda até profundidade alvo ou limite de tempo.
    ctx_d1 = _ContextoBusca(tempo_limite_ms=None, quiescencia=usar_quiescencia)
    melhor, valor = _buscar_raiz(tabuleiro, movimentos, 1, ctx_d1)
    if profundidade <= 1 or abs(valor) >= VALOR_XEQUE_MATE - 100:
        return melhor

    ctx = _ContextoBusca(tempo_limite_ms=tempo_limite_ms, quiescencia=usar_quiescencia)
    for prof_atual in range(2, profundidade + 1):
        try:
            candidato, valor = _buscar_raiz(tabuleiro, movimentos, prof_atual, ctx, melhor)
            melhor = candidato
            if abs(valor) >= VALOR_XEQUE_MATE - 100:
                break
        except _TempoEsgotado:
            break

    return melhor


def melhor_jogada_dificuldade(tabuleiro: Tabuleiro, dificuldade: str | None) -> Jogada | None:
    cfg = CONFIG_DIFICULDADES.get(dificuldade or "medium", CONFIG_DIFICULDADES["medium"])
    return melhor_jogada(
        tabuleiro,
        cfg.profundidade_max,
        tempo_limite_ms=cfg.tempo_limite_ms,
        usar_quiescencia=cfg.quiescencia,
        usar_livro=cfg.usar_livro,
    )
