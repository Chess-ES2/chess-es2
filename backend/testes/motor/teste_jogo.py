import pytest

from motor.jogo import Jogo, JogadaInvalida
from motor.peca import Cor


class TestJogoControleTurno:

    def test_jogo_inicia_com_brancas(self):
        jogo = Jogo.novo()
        assert jogo.turno_atual() == Cor.BRANCA

    def test_fazer_jogada_alterna_o_turno(self):
        jogo = Jogo.novo()
        jogo.fazer_jogada("e2", "e4")
        assert jogo.turno_atual() == Cor.PRETA
        jogo.fazer_jogada("e7", "e5")
        assert jogo.turno_atual() == Cor.BRANCA


class TestJogoExcecoes:

    def test_jogada_em_casa_vazia_lanca_excecao(self):
        jogo = Jogo.novo()
        with pytest.raises(JogadaInvalida, match="Não há nenhuma peça"):
            jogo.fazer_jogada("e4", "e5")

    def test_jogada_com_peca_do_adversario_lanca_excecao(self):
        jogo = Jogo.novo()
        with pytest.raises(JogadaInvalida, match="pertence ao adversário"):
            jogo.fazer_jogada("e7", "e5")

    def test_jogada_ilegal_para_peca_lanca_excecao(self):
        jogo = Jogo.novo()
        with pytest.raises(JogadaInvalida, match="não é válido para esta peça"):
            jogo.fazer_jogada("e2", "e5")


class TestJogoMovimentosValidos:

    def test_movimentos_validos_sem_casa_retorna_todos_do_turno(self):
        jogo = Jogo.novo()
        movimentos = jogo.movimentos_validos()
        assert len(movimentos) == 20

    def test_movimentos_validos_com_casa_da_vez(self):
        jogo = Jogo.novo()
        movimentos = jogo.movimentos_validos("e2")
        destinos = {m.destino for m in movimentos}
        assert destinos == {"e3", "e4"}

    def test_movimentos_validos_com_casa_vazia_retorna_vazio(self):
        jogo = Jogo.novo()
        assert jogo.movimentos_validos("e4") == []

    def test_movimentos_validos_com_casa_do_adversario_retorna_vazio(self):
        jogo = Jogo.novo()
        assert jogo.movimentos_validos("e7") == []


class TestJogoDesfazer:

    def test_desfazer_sem_jogadas_retorna_none(self):
        jogo = Jogo.novo()
        assert jogo.desfazer() is None

    def test_desfazer_restaura_turno_e_posicao(self):
        jogo = Jogo.novo()
        fen_inicial = jogo.tabuleiro.para_fen()

        jogada = jogo.fazer_jogada("e2", "e4")
        assert jogo.turno_atual() == Cor.PRETA

        jogada_desfeita = jogo.desfazer()
        assert jogada_desfeita == jogada
        assert jogo.turno_atual() == Cor.BRANCA
        assert jogo.tabuleiro.para_fen() == fen_inicial
        assert len(jogo.obter_historico()) == 0


class TestJogoRepresentacao:

    def test_repr_contem_turno_e_fen(self):
        jogo = Jogo.novo()
        texto = repr(jogo)
        assert "Brancas" in texto
        assert "Jogo(" in texto
