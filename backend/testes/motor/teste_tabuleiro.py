import pytest
from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import (
    Tabuleiro,
    FEN_INICIAL,
    casa_valida,
    coordenadas,
    de_coordenadas,
)

class TestGeometria:
    def test_casa_valida(self):
        assert casa_valida("a1") is True
        assert casa_valida("h8") is True
        assert casa_valida("e4") is True

    def test_casa_invalida(self):
        assert casa_valida("i1") is False
        assert casa_valida("a9") is False
        assert casa_valida("z")  is False
        assert casa_valida("e44") is False

    def test_coordenadas_a1(self):
        assert coordenadas("a1") == (0, 0)

    def test_coordenadas_h8(self):
        assert coordenadas("h8") == (7, 7)

    def test_de_coordenadas(self):
        assert de_coordenadas(0, 0) == "a1"
        assert de_coordenadas(7, 7) == "h8"
        assert de_coordenadas(-1, 0) is None
        assert de_coordenadas(0, 8)  is None

class TestTabuleiro:
    def test_inicial_parse_fen(self):
        tab = Tabuleiro.inicial()
        assert tab.turno == Cor.BRANCA

    def test_posicao_inicial_pecas(self):
        tab = Tabuleiro.inicial()
        assert tab.obter("e1") == Peca(TipoPeca.REI,   Cor.BRANCA)
        assert tab.obter("e8") == Peca(TipoPeca.REI,   Cor.PRETA)
        assert tab.obter("d1") == Peca(TipoPeca.DAMA,  Cor.BRANCA)
        assert tab.obter("a1") == Peca(TipoPeca.TORRE, Cor.BRANCA)

    def test_casas_vazias_no_meio(self):
        tab = Tabuleiro.inicial()
        for casa in ["e4", "d4", "e5", "d5"]:
            assert tab.obter(casa) is None
            assert tab.esta_vazia(casa) is True

    def test_round_trip_fen(self):
        #Parsear e serializar deve produzir a mesma FEN.
        tab = Tabuleiro.de_fen(FEN_INICIAL)
        assert tab.para_fen() == FEN_INICIAL

    def test_encontrar_rei(self):
        tab = Tabuleiro.inicial()
        assert tab.encontrar_rei(Cor.BRANCA) == "e1"
        assert tab.encontrar_rei(Cor.PRETA)  == "e8"

    def test_copiar_independencia(self):
        #Modificar a cópia não deve afetar o original.
        tab   = Tabuleiro.inicial()
        copia = tab.copiar()
        copia.definir("e4", Peca(TipoPeca.PEAO, Cor.BRANCA))
        assert tab.obter("e4") is None
        assert copia.obter("e4") == Peca(TipoPeca.PEAO, Cor.BRANCA)

    def test_casas_ocupadas_por(self):
        tab = Tabuleiro.inicial()
        brancas = tab.casas_ocupadas_por(Cor.BRANCA)
        pretas = tab.casas_ocupadas_por(Cor.PRETA)
        assert len(brancas) == 16
        assert len(pretas) == 16

    def test_definir_e_remover_peca(self):
        tab = Tabuleiro.inicial()
        assert tab.obter("e4") is None
        tab.definir("e4", Peca(TipoPeca.DAMA, Cor.BRANCA))
        assert tab.obter("e4") == Peca(TipoPeca.DAMA, Cor.BRANCA)
        tab.definir("e4", None)
        assert tab.obter("e4") is None
        assert tab.esta_vazia("e4") is True

    def test_encontrar_rei_inexistente(self):
        tab = Tabuleiro()
        with pytest.raises(ValueError):
            tab.encontrar_rei(Cor.BRANCA)

    def test_fen_invalida_menos_campos(self):
        with pytest.raises(ValueError):
            Tabuleiro.de_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
