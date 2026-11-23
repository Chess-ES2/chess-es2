import pytest

from motor.jogo import Jogo, JogadaInvalida
from motor.peca import Cor, TipoPeca
from motor.tabuleiro import Tabuleiro
from motor.validacao import (
    esta_em_afogamento,
    esta_em_xeque,
    esta_em_xeque_mate,
    empate_por_material_insuficiente,
    obter_movimentos_validos,
)


class TestRoque:

    def test_roque_menor_brancas(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq -")
        jogada = jogo.fazer_jogada("e1", "g1")

        assert jogada.e_roque is True
        rei = jogo.tabuleiro.obter("g1")
        torre = jogo.tabuleiro.obter("f1")
        assert rei is not None
        assert torre is not None
        assert rei.tipo == TipoPeca.REI
        assert torre.tipo == TipoPeca.TORRE
        assert jogo.tabuleiro.obter("e1") is None
        assert jogo.tabuleiro.obter("h1") is None

    def test_roque_maior_brancas(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq -")
        jogada = jogo.fazer_jogada("e1", "c1")

        assert jogada.e_roque is True
        rei = jogo.tabuleiro.obter("c1")
        torre = jogo.tabuleiro.obter("d1")
        assert rei is not None
        assert torre is not None
        assert rei.tipo == TipoPeca.REI
        assert torre.tipo == TipoPeca.TORRE
        assert jogo.tabuleiro.obter("e1") is None
        assert jogo.tabuleiro.obter("a1") is None

    def test_roque_bloqueado_por_peca_no_caminho(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3KB1R w KQkq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")

    def test_roque_bloqueado_se_rei_ja_moveu(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w kq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")

    def test_roque_bloqueado_se_rei_em_xeque(self):
        # Torre preta em e8 dando xeque no rei em e1
        jogo = Jogo.de_fen("4r3/8/8/8/8/8/8/R3K2R w KQkq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")

    def test_roque_bloqueado_se_casa_de_passagem_atacada(self):
        # Torre preta em f8 atacando a casa f1
        jogo = Jogo.de_fen("5r2/8/8/8/8/8/8/R3K2R w KQkq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")

    def test_roque_bloqueado_se_casa_destino_atacada(self):
        # Torre preta em g8 atacando a casa g1
        jogo = Jogo.de_fen("6r1/8/8/8/8/8/8/R3K2R w KQkq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")


class TestEnPassant:

    def test_captura_en_passant_brancas(self):
        # Peao branco em e5, peao preto acabou de avancar de d7 para d5
        jogo = Jogo.de_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6")
        jogada = jogo.fazer_jogada("e5", "d6")

        assert jogada.e_en_passant is True
        peao = jogo.tabuleiro.obter("d6")
        assert peao is not None
        assert peao.tipo == TipoPeca.PEAO
        assert peao.cor == Cor.BRANCA
        assert jogo.tabuleiro.obter("e5") is None
        assert jogo.tabuleiro.obter("d5") is None  # Peao capturado removido

    def test_captura_en_passant_pretas(self):
        # Peao preto em d4, peao branco acabou de avancar de e2 para e4
        jogo = Jogo.de_fen("rnbqkbnr/pppp1ppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR b KQkq d3")
        jogada = jogo.fazer_jogada("e4", "d3")

        assert jogada.e_en_passant is True
        peao = jogo.tabuleiro.obter("d3")
        assert peao is not None
        assert peao.tipo == TipoPeca.PEAO
        assert peao.cor == Cor.PRETA
        assert jogo.tabuleiro.obter("e4") is None
        assert jogo.tabuleiro.obter("d4") is None

    def test_en_passant_expira_apos_um_lance(self):
        jogo = Jogo.de_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6")
        # Brancas fazem outro lance em vez de capturar en passant
        jogo.fazer_jogada("a2", "a3")
        jogo.fazer_jogada("a7", "a6")

        # Agora a oportunidade de en passant passou
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e5", "d6")

    def test_en_passant_impedido_se_deixar_rei_em_xeque(self):
        # Rei branco em e5, peao branco em f5, peao preto em g5 (ep g6), torre preta em h5
        # Se f5 capturar g6 en passant, a linha 5 abre e a torre em h5 da xeque no rei em e5
        jogo = Jogo.de_fen("8/8/8/4KPrr/8/8/8/8 w - g6")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("f5", "g6")


class TestPromocao:

    def test_promocao_padrao_para_dama(self):
        jogo = Jogo.de_fen("8/4P3/8/8/8/8/8/4K2k w - -")
        jogada = jogo.fazer_jogada("e7", "e8")

        assert jogada.promocao == TipoPeca.DAMA
        peca_promovida = jogo.tabuleiro.obter("e8")
        assert peca_promovida is not None
        assert peca_promovida.tipo == TipoPeca.DAMA
        assert peca_promovida.cor == Cor.BRANCA

    def test_promocao_para_cavalo(self):
        jogo = Jogo.de_fen("8/4P3/8/8/8/8/8/4K2k w - -")
        jogada = jogo.fazer_jogada("e7", "e8", promocao=TipoPeca.CAVALO)

        assert jogada.promocao == TipoPeca.CAVALO
        peca_promovida = jogo.tabuleiro.obter("e8")
        assert peca_promovida is not None
        assert peca_promovida.tipo == TipoPeca.CAVALO
        assert peca_promovida.cor == Cor.BRANCA

    def test_promocao_com_captura(self):
        # Peao branco em e7 captura torre preta em d8 e promove para torre
        jogo = Jogo.de_fen("3r4/4P3/8/8/8/8/8/4K2k w - -")
        jogada = jogo.fazer_jogada("e7", "d8", promocao=TipoPeca.TORRE)

        assert jogada.e_captura() is True
        assert jogada.promocao == TipoPeca.TORRE
        peca_promovida = jogo.tabuleiro.obter("d8")
        assert peca_promovida is not None
        assert peca_promovida.tipo == TipoPeca.TORRE
        assert peca_promovida.cor == Cor.BRANCA


class TestXeque:

    def test_rei_branco_em_xeque_por_torre(self):
        tab = Tabuleiro.de_fen("4r3/8/8/8/8/8/8/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is True

    def test_rei_branco_nao_esta_em_xeque(self):
        tab = Tabuleiro.de_fen("4r3/8/8/8/8/8/4R3/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is False

    def test_rei_branco_em_xeque_por_peao(self):
        tab = Tabuleiro.de_fen("8/8/8/8/8/8/3p4/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is True

    def test_ataque_bloqueado_nao_e_xeque(self):
        tab = Tabuleiro.de_fen("4r3/8/8/8/8/4P3/8/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is False

    def test_movimento_que_deixa_o_proprio_rei_em_xeque_e_invalido(self):
        tab = Tabuleiro.de_fen("4r3/8/8/8/8/8/4R3/4K3 w")
        movimentos = obter_movimentos_validos(tab, "e2")
        destinos = [movimento.destino for movimento in movimentos]

        assert "d2" not in destinos
        assert "f2" not in destinos

    def test_rei_preto_em_xeque_mate(self):
        tab = Tabuleiro.de_fen("7k/6Q1/5K2/8/8/8/8/8 b")
        assert esta_em_xeque_mate(tab, Cor.PRETA) is True

    def test_peao_nao_da_xeque_para_frente(self):
        tab = Tabuleiro.de_fen("8/8/8/8/8/8/4p3/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is False

    def test_rei_preto_em_afogamento(self):
        tab = Tabuleiro.de_fen("7k/5Q2/6K1/8/8/8/8/8 b")
        assert esta_em_afogamento(tab, Cor.PRETA) is True

    def test_empate_por_rei_contra_rei(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        assert empate_por_material_insuficiente(tab) is True

    def test_empate_por_rei_e_bispo_contra_rei(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/2B1K3 w")
        assert empate_por_material_insuficiente(tab) is True

    def test_empate_por_rei_e_cavalo_contra_rei(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/2N1K3 w")
        assert empate_por_material_insuficiente(tab) is True

    def test_empate_por_dois_bispos_na_mesma_cor(self):
        tab = Tabuleiro.de_fen("4kb2/8/8/8/8/8/8/2B1K3 w")
        assert empate_por_material_insuficiente(tab) is True

    def test_dois_bispos_em_cores_diferentes_nao_sao_material_insuficiente(self):
        tab = Tabuleiro.de_fen("4k1b1/8/8/8/8/8/8/2B1K3 w")
        assert empate_por_material_insuficiente(tab) is False
