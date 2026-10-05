from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro
from ia.avaliacao import avaliar, avaliar_material, avaliar_posicional
from ia.tabelas import BONUS_POSICAO, VALOR_PECA

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


class TestTabelas:
    def test_toda_peca_tem_valor_e_bonus(self):
        for tipo in TipoPeca:
            assert tipo in VALOR_PECA
            assert tipo in BONUS_POSICAO

    def test_tabelas_sao_8x8(self):
        for tabela in BONUS_POSICAO.values():
            assert len(tabela) == 8
            assert all(len(linha) == 8 for linha in tabela)


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

    def test_bispo_no_centro_vale_mais_que_no_canto(self):
        centro = tabuleiro_com(("d4", TipoPeca.BISPO, Cor.BRANCA))
        canto  = tabuleiro_com(("a1", TipoPeca.BISPO, Cor.BRANCA))
        assert avaliar_posicional(centro) > avaliar_posicional(canto)

    def test_torre_na_setima_fileira_vale_mais_que_no_meio(self):
        setima = tabuleiro_com(("e7", TipoPeca.TORRE, Cor.BRANCA))
        meio   = tabuleiro_com(("e4", TipoPeca.TORRE, Cor.BRANCA))
        assert avaliar_posicional(setima) > avaliar_posicional(meio)

    def test_dama_no_centro_vale_mais_que_no_canto(self):
        centro = tabuleiro_com(("e4", TipoPeca.DAMA, Cor.BRANCA))
        canto  = tabuleiro_com(("a1", TipoPeca.DAMA, Cor.BRANCA))
        assert avaliar_posicional(centro) > avaliar_posicional(canto)

    def test_rei_protegido_vale_mais_que_no_centro(self):
        protegido = tabuleiro_com(("g1", TipoPeca.REI, Cor.BRANCA))
        centro    = tabuleiro_com(("e4", TipoPeca.REI, Cor.BRANCA))
        assert avaliar_posicional(protegido) > avaliar_posicional(centro)

    def test_simetria_de_todas_as_pecas(self):
        #Cada peça branca em uma casa deve valer o oposto da peça preta na casa espelhada.
        for tipo in TipoPeca:
            brancas = tabuleiro_com(("b2", tipo, Cor.BRANCA), ("f4", tipo, Cor.BRANCA))
            pretas  = tabuleiro_com(("b7", tipo, Cor.PRETA),  ("f5", tipo, Cor.PRETA))
            assert avaliar_posicional(brancas) == -avaliar_posicional(pretas)

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

    def test_soma_material_e_posicional(self):
        tab = Tabuleiro.de_fen(FEN_SEM_DAMA_PRETA)
        assert avaliar(tab) == avaliar_material(tab) + avaliar_posicional(tab)

    def test_posicao_influencia_a_nota(self):
        #Mesmo material, casas diferentes: o cavalo central deve render nota maior.
        centro = tabuleiro_com(("e4", TipoPeca.CAVALO, Cor.BRANCA))
        borda  = tabuleiro_com(("a1", TipoPeca.CAVALO, Cor.BRANCA))
        assert avaliar_material(centro) == avaliar_material(borda)
        assert avaliar(centro) > avaliar(borda)

    def test_material_pesa_mais_que_a_posicao(self):
        #Uma dama no pior canto ainda vale muito mais que nenhuma dama.
        com_dama_no_canto = tabuleiro_com(("a1", TipoPeca.DAMA, Cor.BRANCA))
        sem_dama = Tabuleiro()
        assert avaliar(com_dama_no_canto) > avaliar(sem_dama)

    def test_simetria_da_nota_total(self):
        brancas = tabuleiro_com(("e4", TipoPeca.CAVALO, Cor.BRANCA), ("d1", TipoPeca.DAMA, Cor.BRANCA))
        pretas  = tabuleiro_com(("e5", TipoPeca.CAVALO, Cor.PRETA),  ("d8", TipoPeca.DAMA, Cor.PRETA))
        assert avaliar(brancas) == -avaliar(pretas)

    def test_nao_altera_o_tabuleiro(self):
        tab = Tabuleiro.inicial()
        fen_antes = tab.para_fen()
        avaliar(tab)
        assert tab.para_fen() == fen_antes

    def test_resultado_estavel(self):
        tab = Tabuleiro.de_fen(FEN_SEM_DAMA_PRETA)
        assert avaliar(tab) == avaliar(tab)
