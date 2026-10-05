from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro
from ia.avaliacao import avaliar, avaliar_material, avaliar_posicional

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


def tabuleiro_com(*pecas: tuple[str, TipoPeca, Cor]) -> Tabuleiro:
    #Monta um tabuleiro só com as peças indicadas (casa, tipo, cor).
    tab = Tabuleiro()
    for casa, tipo, cor in pecas:
        tab.definir(casa, Peca(tipo, cor))
    return tab


class TestPosicional:
    def test_posicao_inicial_equilibrada(self):
        assert avaliar_posicional(Tabuleiro.inicial()) == 0

    def test_cavalo_no_centro_vale_mais_que_na_borda(self):
        centro = tabuleiro_com(("e4", TipoPeca.CAVALO, Cor.BRANCA))
        borda  = tabuleiro_com(("a1", TipoPeca.CAVALO, Cor.BRANCA))
        assert avaliar_posicional(centro) > avaliar_posicional(borda)

    def test_peao_avancado_vale_mais_que_na_casa_inicial(self):
        avancado = tabuleiro_com(("e5", TipoPeca.PEAO, Cor.BRANCA))
        inicial  = tabuleiro_com(("e2", TipoPeca.PEAO, Cor.BRANCA))
        assert avaliar_posicional(avancado) > avaliar_posicional(inicial)

    def test_simetria_cavalo(self):
        #e4 para as brancas é a casa espelhada de e5 para as pretas.
        brancas = tabuleiro_com(("e4", TipoPeca.CAVALO, Cor.BRANCA))
        pretas  = tabuleiro_com(("e5", TipoPeca.CAVALO, Cor.PRETA))
        assert avaliar_posicional(brancas) == -avaliar_posicional(pretas)

    def test_simetria_peao(self):
        brancas = tabuleiro_com(("c3", TipoPeca.PEAO, Cor.BRANCA))
        pretas  = tabuleiro_com(("c6", TipoPeca.PEAO, Cor.PRETA))
        assert avaliar_posicional(brancas) == -avaliar_posicional(pretas)

    def test_nao_altera_o_tabuleiro(self):
        tab = Tabuleiro.inicial()
        fen_antes = tab.para_fen()
        avaliar_posicional(tab)
        assert tab.para_fen() == fen_antes


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
