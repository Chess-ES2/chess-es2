import pytest

from motor.peca import Cor
from motor.tabuleiro import Tabuleiro
from motor.validacao import (
    esta_em_xeque,
    esta_em_xeque_mate,
    esta_em_afogamento,
    empate_por_material_insuficiente,
    obter_movimentos_validos,
    obter_todos_movimentos_validos,
)


class TestXeque:

    def test_rei_branco_em_xeque_por_torre(self):
        tab = Tabuleiro.de_fen("4r3/8/8/8/8/8/8/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is True

    def test_rei_branco_nao_esta_em_xeque(self):
        tab = Tabuleiro.de_fen("4r3/8/8/8/8/8/4R3/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is False

    def test_rei_preto_em_xeque_por_torre(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4R3 b")
        assert esta_em_xeque(tab, Cor.PRETA) is True

    def test_rei_branco_em_xeque_por_bispo(self):
        tab = Tabuleiro.de_fen("8/8/8/8/1b6/8/8/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is True

    def test_rei_branco_em_xeque_por_cavalo(self):
        tab = Tabuleiro.de_fen("8/8/8/8/8/8/2n5/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is True

    def test_rei_branco_em_xeque_por_dama(self):
        tab = Tabuleiro.de_fen("4q3/8/8/8/8/8/8/4K3 w")
        assert esta_em_xeque(tab, Cor.BRANCA) is True

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