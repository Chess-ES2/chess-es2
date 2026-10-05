import pytest

from motor.jogo import Jogo, JogadaInvalida
from motor.peca import Cor, TipoPeca


class TestRoque:

    def test_roque_menor_brancas(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq -")
        jogada = jogo.fazer_jogada("e1", "g1")

        assert jogada.e_roque is True
        assert jogo.tabuleiro.obter("g1").tipo == TipoPeca.REI
        assert jogo.tabuleiro.obter("f1").tipo == TipoPeca.TORRE
        assert jogo.tabuleiro.obter("e1") is None
        assert jogo.tabuleiro.obter("h1") is None

    def test_roque_maior_brancas(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq -")
        jogada = jogo.fazer_jogada("e1", "c1")

        assert jogada.e_roque is True
        assert jogo.tabuleiro.obter("c1").tipo == TipoPeca.REI
        assert jogo.tabuleiro.obter("d1").tipo == TipoPeca.TORRE
        assert jogo.tabuleiro.obter("e1") is None
        assert jogo.tabuleiro.obter("a1") is None

    def test_roque_menor_pretas(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq -")
        jogada = jogo.fazer_jogada("e8", "g8")

        assert jogada.e_roque is True
        assert jogo.tabuleiro.obter("g8").tipo == TipoPeca.REI
        assert jogo.tabuleiro.obter("f8").tipo == TipoPeca.TORRE
        assert jogo.tabuleiro.obter("e8") is None
        assert jogo.tabuleiro.obter("h8") is None

    def test_roque_maior_pretas(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq -")
        jogada = jogo.fazer_jogada("e8", "c8")

        assert jogada.e_roque is True
        assert jogo.tabuleiro.obter("c8").tipo == TipoPeca.REI
        assert jogo.tabuleiro.obter("d8").tipo == TipoPeca.TORRE
        assert jogo.tabuleiro.obter("e8") is None
        assert jogo.tabuleiro.obter("a8") is None

    def test_roque_bloqueado_por_peca_no_caminho(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3KB1R w KQkq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")

    def test_roque_bloqueado_se_rei_ja_moveu(self):
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w kq -")
        with pytest.raises(JogadaInvalida):
            jogo.fazer_jogada("e1", "g1")

    def test_roque_bloqueado_se_torre_ja_moveu(self):
        # Brancas tem direito apenas ao roque maior (Q)
        jogo = Jogo.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w Qkq -")
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
        assert jogo.tabuleiro.obter("d6").tipo == TipoPeca.PEAO
        assert jogo.tabuleiro.obter("d6").cor == Cor.BRANCA
        assert jogo.tabuleiro.obter("e5") is None
        assert jogo.tabuleiro.obter("d5") is None  # Peao capturado removido

    def test_captura_en_passant_pretas(self):
        # Peao preto em d4, peao branco acabou de avancar de e2 para e4
        jogo = Jogo.de_fen("rnbqkbnr/pppp1ppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR b KQkq d3")
        jogada = jogo.fazer_jogada("e4", "d3")

        assert jogada.e_en_passant is True
        assert jogo.tabuleiro.obter("d3").tipo == TipoPeca.PEAO
        assert jogo.tabuleiro.obter("d3").cor == Cor.PRETA
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
        assert peca_promovida.tipo == TipoPeca.DAMA
        assert peca_promovida.cor == Cor.BRANCA

    def test_promocao_para_cavalo(self):
        jogo = Jogo.de_fen("8/4P3/8/8/8/8/8/4K2k w - -")
        jogada = jogo.fazer_jogada("e7", "e8", promocao=TipoPeca.CAVALO)

        assert jogada.promocao == TipoPeca.CAVALO
        peca_promovida = jogo.tabuleiro.obter("e8")
        assert peca_promovida.tipo == TipoPeca.CAVALO
        assert peca_promovida.cor == Cor.BRANCA

    def test_promocao_com_captura(self):
        # Peao branco em e7 captura torre preta em d8 e promove para torre
        jogo = Jogo.de_fen("3r4/4P3/8/8/8/8/8/4K2k w - -")
        jogada = jogo.fazer_jogada("e7", "d8", promocao=TipoPeca.TORRE)

        assert jogada.e_captura() is True
        assert jogada.promocao == TipoPeca.TORRE
        peca_promovida = jogo.tabuleiro.obter("d8")
        assert peca_promovida.tipo == TipoPeca.TORRE
        assert peca_promovida.cor == Cor.BRANCA
