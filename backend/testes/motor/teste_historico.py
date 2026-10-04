from motor.jogo import Jogo
from motor.validacao import ocorre_repeticao_tripla

class TestHistorico:

    def test_jogo_comeca_com_historico_vazio(self):
        jogo = Jogo.novo()

        assert jogo.obter_historico() == []

    def test_historico_registra_uma_jogada(self):
        jogo = Jogo.novo()

        jogada = jogo.fazer_jogada("e2", "e4")

        historico = jogo.obter_historico()

        assert len(historico) == 1
        assert historico[0] == jogada

    def test_historico_registra_duas_jogadas(self):
        jogo = Jogo.novo()

        jogo.fazer_jogada("e2", "e4")
        jogo.fazer_jogada("e7", "e5")

        historico = jogo.obter_historico()

        assert len(historico) == 2
        assert historico[0].origem == "e2"
        assert historico[0].destino == "e4"
        assert historico[1].origem == "e7"
        assert historico[1].destino == "e5"

    def test_historico_contem_informacoes_da_jogada(self):
        jogo = Jogo.novo()

        jogada = jogo.fazer_jogada("e2", "e4")

        assert jogada.origem == "e2"
        assert jogada.destino == "e4"
        assert jogada.peca.para_char_fen() == "P"
        assert jogada.captura is None

    def test_obter_historico_retorna_uma_copia(self):
        jogo = Jogo.novo()

        jogo.fazer_jogada("e2", "e4")

        historico = jogo.obter_historico()
        historico.clear()

        assert len(historico) == 0
        assert len(jogo.obter_historico()) == 1

    def test_historico_posicoes_comeca_com_posicao_inicial(self):
        jogo = Jogo.novo()

        posicoes = jogo.obter_historico_posicoes()

        assert len(posicoes) == 1
        assert posicoes[0] == jogo.tabuleiro.para_fen()

    def test_historico_posicoes_registra_nova_posicao(self):
        jogo = Jogo.novo()

        posicao_inicial = jogo.tabuleiro.para_fen()

        jogo.fazer_jogada("e2", "e4")

        posicoes = jogo.obter_historico_posicoes()

        assert len(posicoes) == 2
        assert posicoes[0] == posicao_inicial
        assert posicoes[1] == jogo.tabuleiro.para_fen()
        assert posicoes[0] != posicoes[1]

    def test_detecta_repeticao_tripla(self):
        posicoes = [
            "posicao_a",
            "posicao_b",
            "posicao_a",
            "posicao_c",
            "posicao_a",
        ]

        assert ocorre_repeticao_tripla(posicoes) is True

    def test_nao_detecta_repeticao_duas_vezes(self):
        posicoes = [
            "posicao_a",
            "posicao_b",
            "posicao_a",
            "posicao_c",
        ]

        assert ocorre_repeticao_tripla(posicoes) is False