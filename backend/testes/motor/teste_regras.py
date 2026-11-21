from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro
from motor.validacao import (
    casa_sob_ataque,
    empate_por_material_insuficiente,
    obter_movimentos_validos,
    validar_movimento,
)


class TestObterMovimentosValidos:
    def test_movimentos_validos_casa_vazia_retorna_vazio(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        assert obter_movimentos_validos(tab, "e4") == []

    def test_movimento_legal_e_incluido(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        destinos = {j.destino for j in obter_movimentos_validos(tab, "e1")}
        assert "e2" in destinos

    def test_roque_maior_excluido_se_caminho_atacado(self):
        tab = Tabuleiro.de_fen("3rk3/8/8/8/8/8/8/R3K3 w Qkq -")
        assert not any(j.e_roque for j in obter_movimentos_validos(tab, "e1"))


class TestValidarMovimento:
    def test_validar_origem_vazia_retorna_none(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        assert validar_movimento(tab, "e4", "e5") is None

    def test_validar_peca_adversaria_retorna_none(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        assert validar_movimento(tab, "e8", "e7") is None

    def test_validar_destino_invalido_retorna_none(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        assert validar_movimento(tab, "e1", "a8") is None

    def test_validar_movimento_legal_retorna_jogada(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        jogada = validar_movimento(tab, "e1", "e2")
        assert jogada is not None
        assert jogada.destino == "e2"

    def test_validar_promocao_sem_tipo_usa_dama(self):
        tab = Tabuleiro.de_fen("k7/4P3/8/8/8/8/8/4K3 w - -")
        jogada = validar_movimento(tab, "e7", "e8")
        assert jogada is not None
        assert jogada.promocao == TipoPeca.DAMA

    def test_validar_promocao_retorna_tipo_correto(self):
        tab = Tabuleiro.de_fen("k7/4P3/8/8/8/8/8/4K3 w - -")
        jogada = validar_movimento(tab, "e7", "e8", TipoPeca.CAVALO)
        assert jogada is not None
        assert jogada.promocao == TipoPeca.CAVALO


class TestAtaque:
    def test_casa_sob_ataque_por_torre(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/R3K3 w")
        assert casa_sob_ataque(tab, "d1", Cor.BRANCA) is True

    def test_casa_sem_atacantes_nao_esta_sob_ataque(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K3 w")
        assert casa_sob_ataque(tab, "e4", Cor.PRETA) is False


class TestMaterialInsuficiente:
    def test_rei_torre_vs_rei_tem_material_suficiente(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/R3K3 w")
        assert empate_por_material_insuficiente(tab) is False
