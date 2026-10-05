from motor.tabuleiro import Tabuleiro
from ia.avaliacao import avaliar, avaliar_material

# Posição inicial sem a dama preta / sem a dama branca
FEN_SEM_DAMA_PRETA  = "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"
FEN_SEM_DAMA_BRANCA = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w"


class TestMaterial:
    def test_posicao_inicial_equilibrada(self):
        assert avaliar_material(Tabuleiro.inicial()) == 0

    def test_brancas_com_dama_a_mais(self):
        tab = Tabuleiro.de_fen(FEN_SEM_DAMA_PRETA)
        assert avaliar_material(tab) == 900

    def test_pretas_com_dama_a_mais(self):
        tab = Tabuleiro.de_fen(FEN_SEM_DAMA_BRANCA)
        assert avaliar_material(tab) == -900

    def test_tabuleiro_vazio(self):
        assert avaliar_material(Tabuleiro()) == 0


class TestAvaliar:
    def test_posicao_inicial(self):
        assert avaliar(Tabuleiro.inicial()) == 0

    def test_nao_altera_o_tabuleiro(self):
        tab = Tabuleiro.inicial()
        fen_antes = tab.para_fen()
        avaliar(tab)
        assert tab.para_fen() == fen_antes

    def test_resultado_estavel(self):
        tab = Tabuleiro.de_fen(FEN_SEM_DAMA_PRETA)
        assert avaliar(tab) == avaliar(tab)
