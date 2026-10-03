import pytest
from motor.peca import Cor, Peca, TipoPeca

class TestCor:
    def test_oposta_branca(self):
        assert Cor.BRANCA.oposta() == Cor.PRETA

    def test_oposta_preta(self):
        assert Cor.PRETA.oposta() == Cor.BRANCA

class TestPeca:
    def test_de_char_fen_maiusculo_branca(self):
        peca = Peca.de_char_fen("R")
        assert peca.tipo == TipoPeca.TORRE
        assert peca.cor == Cor.BRANCA

    def test_de_char_fen_minusculo_preta(self):
        peca = Peca.de_char_fen("k")
        assert peca.tipo == TipoPeca.REI
        assert peca.cor == Cor.PRETA

    def test_de_char_fen_invalido(self):
        with pytest.raises(ValueError):
            Peca.de_char_fen("x")

    def test_para_char_fen_branca(self):
        peca = Peca(tipo=TipoPeca.DAMA, cor=Cor.BRANCA)
        assert peca.para_char_fen() == "Q"

    def test_para_char_fen_preta(self):
        peca = Peca(tipo=TipoPeca.PEAO, cor=Cor.PRETA)
        assert peca.para_char_fen() == "p"

    def test_round_trip_fen(self):
        for char in "RNBQKPrnbqkp":
            assert Peca.de_char_fen(char).para_char_fen() == char

    def test_imutabilidade(self):
        #Peca é frozen dataclass, a atribuição deve falhar.
        peca = Peca(tipo=TipoPeca.REI, cor=Cor.BRANCA)
        with pytest.raises(Exception):
            peca.cor = Cor.PRETA  # type: ignore
    def test_igualdade(self):
        p1 = Peca(TipoPeca.PEAO, Cor.BRANCA)
        p2 = Peca(TipoPeca.PEAO, Cor.BRANCA)
        p3 = Peca(TipoPeca.PEAO, Cor.PRETA)
        assert p1 == p2
        assert p1 != p3


