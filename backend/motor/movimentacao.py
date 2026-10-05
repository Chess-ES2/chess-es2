from __future__ import annotations
from dataclasses import dataclass

from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro, coordenadas, de_coordenadas

@dataclass
class Jogada:
   #Representa um movimento de uma peça no tabuleiro.

    origem:  str
    destino: str
    peca:    Peca
    captura: Peca | None = None
    e_roque: bool = False
    e_en_passant: bool = False
    promocao: TipoPeca | None = None

    def e_captura(self) -> bool:
        #Retorna true se o movimento resulta em captura de peça adversaria.
        return self.captura is not None

    def para_dict(self) -> dict:
        return {
            "origem":       self.origem,
            "destino":      self.destino,
            "peca":         self.peca.para_char_fen(),
            "captura":      self.captura.para_char_fen() if self.captura else None,
            "e_roque":      self.e_roque,
            "e_en_passant": self.e_en_passant,
            "promocao":     self.promocao.value if self.promocao else None,
        }

    def __repr__(self) -> str:
        captura_str = f" x {self.captura.para_char_fen()}" if self.captura else ""
        return f"Jogada({self.peca.para_char_fen()}: {self.origem} -> {self.destino}{captura_str})"



#Geração de movimentos e capturas:

def gerar_movimentos_peca(tabuleiro: Tabuleiro, casa: str) -> list[Jogada]:
    #Gera todos os movimentos e capturas válidos da peça na casa indicada,
    
    peca = tabuleiro.obter(casa)
    if peca is None:
        return []

    geradores = {
        TipoPeca.PEAO:   _movimentos_peao,
        TipoPeca.CAVALO: _movimentos_cavalo,
        TipoPeca.BISPO:  _movimentos_bispo,
        TipoPeca.TORRE:  _movimentos_torre,
        TipoPeca.DAMA:   _movimentos_dama,
        TipoPeca.REI:    _movimentos_rei,
    }
    return geradores[peca.tipo](tabuleiro, casa, peca)


def gerar_todos_movimentos(tabuleiro: Tabuleiro, cor: Cor) -> list[Jogada]:
    #Gera todos os movimentos e capturas válidos de todas as peças da cor indicada.
    movimentos: list[Jogada] = []
    for casa in tabuleiro.casas_ocupadas_por(cor):
        movimentos.extend(gerar_movimentos_peca(tabuleiro, casa))
    return movimentos


# funcs auxiliares
def _avaliar_destino(
    tabuleiro: Tabuleiro,
    peca:      Peca,
    origem:    str,
    destino:   str,
) -> Jogada | None:
    #Avalia se uma casa de destino é válida:
    
    alvo = tabuleiro.obter(destino)
    if alvo is None:
        return Jogada(origem=origem, destino=destino, peca=peca, captura=None)
    if alvo.cor != peca.cor:
        return Jogada(origem=origem, destino=destino, peca=peca, captura=alvo)
    return None

def _deslizar(
    tabuleiro: Tabuleiro,
    peca:      Peca,
    origem:    str,
    direcoes:  list[tuple[int, int]],
) -> list[Jogada]:
    # Gera movimentos e capturas para peças que deslizam em linhas retas ou diagonais.
   
    jogadas: list[Jogada] = []
    col_orig, lin_orig = coordenadas(origem)

    for delta_col, delta_lin in direcoes:
        col, lin = col_orig + delta_col, lin_orig + delta_lin
        while 0 <= col <= 7 and 0 <= lin <= 7:
            destino = de_coordenadas(col, lin)
            if destino is None:
                break
            alvo = tabuleiro.obter(destino)
            if alvo is None:
                jogadas.append(Jogada(origem=origem, destino=destino, peca=peca))
            elif alvo.cor != peca.cor:
                #Captura de peça adversaria e encerra o raio de visao
                jogadas.append(Jogada(origem=origem, destino=destino, peca=peca, captura=alvo))
                break
            else:
                #Bloqueado por peca da mesma cor
                break
            col += delta_col
            lin += delta_lin

    return jogadas


# Regras por tipo de peça:

def _movimentos_peao(tabuleiro: Tabuleiro, casa: str, peca: Peca) -> list[Jogada]:
    jogadas: list[Jogada] = []
    col, lin = coordenadas(casa)

    # Brancas avançam subindo no tabuleiro (+1), Pretas descendo (-1)
    passo = 1 if peca.cor == Cor.BRANCA else -1
    linha_inicial = 1 if peca.cor == Cor.BRANCA else 6
    linha_promocao = 7 if peca.cor == Cor.BRANCA else 0

    # 1. Avanço simples
    casa_frente = de_coordenadas(col, lin + passo)
    if casa_frente and tabuleiro.esta_vazia(casa_frente):
        if lin + passo == linha_promocao:
            for tipo_prom in (TipoPeca.DAMA, TipoPeca.TORRE, TipoPeca.BISPO, TipoPeca.CAVALO):
                jogadas.append(Jogada(origem=casa, destino=casa_frente, peca=peca, promocao=tipo_prom))
        else:
            jogadas.append(Jogada(origem=casa, destino=casa_frente, peca=peca))

        # 2. Avanço duplo a partir da linha inicial
        if lin == linha_inicial:
            casa_dois_frente = de_coordenadas(col, lin + 2 * passo)
            if casa_dois_frente and tabuleiro.esta_vazia(casa_dois_frente):
                jogadas.append(Jogada(origem=casa, destino=casa_dois_frente, peca=peca))

    # 3. Capturas diagonais frontais
    for delta_col in (-1, 1):
        diagonal = de_coordenadas(col + delta_col, lin + passo)
        if diagonal is None:
            continue
        alvo = tabuleiro.obter(diagonal)
        if alvo is not None and alvo.cor != peca.cor:
            if lin + passo == linha_promocao:
                for tipo_prom in (TipoPeca.DAMA, TipoPeca.TORRE, TipoPeca.BISPO, TipoPeca.CAVALO):
                    jogadas.append(Jogada(origem=casa, destino=diagonal, peca=peca, captura=alvo, promocao=tipo_prom))
            else:
                jogadas.append(Jogada(origem=casa, destino=diagonal, peca=peca, captura=alvo))
        elif diagonal == tabuleiro.casa_en_passant:
            # Captura en passant
            casa_lateral = de_coordenadas(col + delta_col, lin)
            if casa_lateral:
                peao_alvo = tabuleiro.obter(casa_lateral)
                if peao_alvo and peao_alvo.cor != peca.cor and peao_alvo.tipo == TipoPeca.PEAO:
                    jogadas.append(Jogada(origem=casa, destino=diagonal, peca=peca, captura=peao_alvo, e_en_passant=True))

    return jogadas


def _movimentos_cavalo(tabuleiro: Tabuleiro, casa: str, peca: Peca) -> list[Jogada]:
   
    col, lin = coordenadas(casa)
    saltos = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        ( 1, -2), ( 1, 2), ( 2, -1), ( 2, 1)
    ]
    jogadas: list[Jogada] = []
    for delta_col, delta_lin in saltos:
        destino = de_coordenadas(col + delta_col, lin + delta_lin)
        if destino:
            jogada = _avaliar_destino(tabuleiro, peca, casa, destino)
            if jogada:
                jogadas.append(jogada)
    return jogadas


def _movimentos_bispo(tabuleiro: Tabuleiro, casa: str, peca: Peca) -> list[Jogada]:
    return _deslizar(tabuleiro, peca, casa, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


def _movimentos_torre(tabuleiro: Tabuleiro, casa: str, peca: Peca) -> list[Jogada]:
    return _deslizar(tabuleiro, peca, casa, [(-1, 0), (1, 0), (0, -1), (0, 1)])


def _movimentos_dama(tabuleiro: Tabuleiro, casa: str, peca: Peca) -> list[Jogada]:
    return _movimentos_bispo(tabuleiro, casa, peca) + _movimentos_torre(tabuleiro, casa, peca)

def _movimentos_rei(tabuleiro: Tabuleiro, casa: str, peca: Peca) -> list[Jogada]:
    col, lin = coordenadas(casa)
    passos = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1)
    ]
    jogadas: list[Jogada] = []
    for delta_col, delta_lin in passos:
        destino = de_coordenadas(col + delta_col, lin + delta_lin)
        if destino:
            jogada = _avaliar_destino(tabuleiro, peca, casa, destino)
            if jogada:
                jogadas.append(jogada)

    # Roque
    if peca.cor == Cor.BRANCA and casa == "e1":
        if tabuleiro.direitos_roque.get("K") and tabuleiro.esta_vazia("f1") and tabuleiro.esta_vazia("g1"):
            torre = tabuleiro.obter("h1")
            if torre and torre.tipo == TipoPeca.TORRE and torre.cor == Cor.BRANCA:
                jogadas.append(Jogada(origem="e1", destino="g1", peca=peca, e_roque=True))
        if tabuleiro.direitos_roque.get("Q") and tabuleiro.esta_vazia("d1") and tabuleiro.esta_vazia("c1") and tabuleiro.esta_vazia("b1"):
            torre = tabuleiro.obter("a1")
            if torre and torre.tipo == TipoPeca.TORRE and torre.cor == Cor.BRANCA:
                jogadas.append(Jogada(origem="e1", destino="c1", peca=peca, e_roque=True))
    elif peca.cor == Cor.PRETA and casa == "e8":
        if tabuleiro.direitos_roque.get("k") and tabuleiro.esta_vazia("f8") and tabuleiro.esta_vazia("g8"):
            torre = tabuleiro.obter("h8")
            if torre and torre.tipo == TipoPeca.TORRE and torre.cor == Cor.PRETA:
                jogadas.append(Jogada(origem="e8", destino="g8", peca=peca, e_roque=True))
        if tabuleiro.direitos_roque.get("q") and tabuleiro.esta_vazia("d8") and tabuleiro.esta_vazia("c8") and tabuleiro.esta_vazia("b8"):
            torre = tabuleiro.obter("a8")
            if torre and torre.tipo == TipoPeca.TORRE and torre.cor == Cor.PRETA:
                jogadas.append(Jogada(origem="e8", destino="c8", peca=peca, e_roque=True))

    return jogadas

