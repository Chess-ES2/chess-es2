from motor.jogo import Jogo
from motor.peca import Cor


class TestJogoFinalizacoes:

    def test_jogo_detecta_xeque(self):
        jogo = Jogo.de_fen("4r3/8/8/8/8/8/8/4K3 w")

        assert jogo.esta_em_xeque() is True

    def test_jogo_detecta_xeque_mate(self):
        jogo = Jogo.de_fen("7k/6Q1/5K2/8/8/8/8/8 b")

        assert jogo.esta_em_xeque_mate() is True

    def test_jogo_detecta_afogamento(self):
        jogo = Jogo.de_fen("7k/5Q2/6K1/8/8/8/8/8 b")

        assert jogo.esta_em_afogamento() is True

    def test_jogo_detecta_material_insuficiente(self):
        jogo = Jogo.de_fen("4k3/8/8/8/8/8/8/4K3 w")

        assert jogo.empate_por_material_insuficiente() is True