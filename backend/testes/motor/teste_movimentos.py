import pytest

from motor.movimentacao import (
    _movimentos_cavalo,
    _movimentos_peao,
    gerar_movimentos_peca,
)
from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro


class TestGeracaoGenerica:
    def test_gerar_movimentos_casa_vazia_retorna_vazio(self):
        tab = Tabuleiro()
        assert gerar_movimentos_peca(tab, "e4") == []

    def test_gerar_movimentos_delega_para_tipo_correto(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.CAVALO, Cor.BRANCA))
        jogadas = gerar_movimentos_peca(tab, "e4")
        assert len(jogadas) == 8
        assert {j.destino for j in jogadas} == {"c3", "c5", "d2", "d6", "f2", "f6", "g3", "g5"}


class TestMovimentosPeao:
    def test_peao_avanca_uma_casa_a_frente(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e2", peca)
        destinos = {j.destino for j in _movimentos_peao(tab, "e2", peca)}
        assert "e3" in destinos

    def test_peao_bloqueado_a_frente_nao_tem_movimento(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e2", peca)
        tab.definir("e3", Peca(TipoPeca.PEAO, Cor.PRETA))
        assert _movimentos_peao(tab, "e2", peca) == []

    def test_peao_avanca_duas_casas_da_posicao_inicial(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e2", peca)
        destinos = {j.destino for j in _movimentos_peao(tab, "e2", peca)}
        assert "e4" in destinos

    def test_peao_nao_avanca_duas_casas_se_intermediaria_bloqueada(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e2", peca)
        tab.definir("e3", Peca(TipoPeca.PEAO, Cor.PRETA))
        destinos = {j.destino for j in _movimentos_peao(tab, "e2", peca)}
        assert "e4" not in destinos

    def test_peao_captura_peca_adversaria_nas_duas_diagonais(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e4", peca)
        tab.definir("d5", Peca(TipoPeca.PEAO, Cor.PRETA))
        tab.definir("f5", Peca(TipoPeca.TORRE, Cor.PRETA))
        destinos = {j.destino for j in _movimentos_peao(tab, "e4", peca)}
        assert {"d5", "f5"} <= destinos

    def test_peao_nao_captura_peca_propria(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e4", peca)
        tab.definir("d5", Peca(TipoPeca.PEAO, Cor.BRANCA))
        destinos = {j.destino for j in _movimentos_peao(tab, "e4", peca)}
        assert "d5" not in destinos

    def test_peao_nao_vai_a_diagonal_vazia(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e4", peca)
        destinos = {j.destino for j in _movimentos_peao(tab, "e4", peca)}
        assert "d5" not in destinos
        assert "f5" not in destinos

    def test_peao_na_setima_gera_quatro_promocoes_no_avanco(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e7", peca)
        jogadas = _movimentos_peao(tab, "e7", peca)
        assert {j.promocao for j in jogadas if j.destino == "e8"} == {
            TipoPeca.DAMA, TipoPeca.TORRE, TipoPeca.BISPO, TipoPeca.CAVALO
        }

    def test_peao_na_setima_gera_quatro_promocoes_na_captura(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        tab.definir("e7", peca)
        tab.definir("d8", Peca(TipoPeca.TORRE, Cor.PRETA))
        jogadas = _movimentos_peao(tab, "e7", peca)
        assert len([j for j in jogadas if j.destino == "d8"]) == 4
        assert {j.promocao for j in jogadas if j.destino == "d8"} == {
            TipoPeca.DAMA, TipoPeca.TORRE, TipoPeca.BISPO, TipoPeca.CAVALO
        }

    def test_peao_gera_en_passant_quando_disponivel(self):
        tab = Tabuleiro.de_fen("8/8/8/3pP3/8/8/8/8 w - d6")
        peca = tab.obter("e5")
        jogadas = _movimentos_peao(tab, "e5", peca)
        assert any(j.destino == "d6" and j.e_en_passant for j in jogadas)

    def test_peao_ignora_en_passant_invalido(self):
        tab = Tabuleiro.de_fen("8/8/8/4P3/8/8/8/8 w - d6")
        peca = tab.obter("e5")
        assert not any(j.e_en_passant for j in _movimentos_peao(tab, "e5", peca))


class TestMovimentosCavalo:
    def test_cavalo_no_canto_tem_apenas_dois_movimentos(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.CAVALO, Cor.BRANCA)
        tab.definir("a1", peca)
        assert {j.destino for j in _movimentos_cavalo(tab, "a1", peca)} == {"b3", "c2"}

    def test_cavalo_no_centro_tem_oito_movimentos(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.CAVALO, Cor.BRANCA)
        tab.definir("e4", peca)
        assert len(_movimentos_cavalo(tab, "e4", peca)) == 8

    def test_cavalo_captura_peca_adversaria(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.CAVALO, Cor.BRANCA)
        tab.definir("e4", peca)
        tab.definir("c3", Peca(TipoPeca.PEAO, Cor.PRETA))
        jogada = next(j for j in _movimentos_cavalo(tab, "e4", peca) if j.destino == "c3")
        assert jogada.captura == Peca(TipoPeca.PEAO, Cor.PRETA)

    def test_cavalo_nao_move_para_casa_com_peca_propria(self):
        tab = Tabuleiro()
        peca = Peca(TipoPeca.CAVALO, Cor.BRANCA)
        tab.definir("e4", peca)
        tab.definir("c3", Peca(TipoPeca.PEAO, Cor.BRANCA))
        assert "c3" not in {j.destino for j in _movimentos_cavalo(tab, "e4", peca)}


class TestMovimentosDeslize:
    def test_torre_desliza_ate_a_borda_sem_bloqueio(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.TORRE, Cor.BRANCA))
        destinos = {j.destino for j in gerar_movimentos_peca(tab, "e4")}
        assert {"e1", "e8", "a4", "h4"} <= destinos

    def test_torre_captura_adversaria_e_para(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.TORRE, Cor.BRANCA))
        tab.definir("e7", Peca(TipoPeca.PEAO, Cor.PRETA))
        jogadas = gerar_movimentos_peca(tab, "e4")
        assert any(j.destino == "e7" and j.captura is not None for j in jogadas)
        assert "e8" not in {j.destino for j in jogadas}

    def test_torre_parada_por_peca_propria_nao_captura(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.TORRE, Cor.BRANCA))
        tab.definir("e7", Peca(TipoPeca.PEAO, Cor.BRANCA))
        jogadas = gerar_movimentos_peca(tab, "e4")
        assert "e7" not in {j.destino for j in jogadas}
        assert "e8" not in {j.destino for j in jogadas}

    def test_bispo_no_canto_desliza_numa_unica_diagonal(self):
        tab = Tabuleiro()
        tab.definir("a1", Peca(TipoPeca.BISPO, Cor.BRANCA))
        assert {j.destino for j in gerar_movimentos_peca(tab, "a1")} == {
            "b2", "c3", "d4", "e5", "f6", "g7", "h8"
        }


class TestMovimentosRei:
    def test_rei_move_para_casa_adjacente_livre(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.REI, Cor.BRANCA))
        jogadas = gerar_movimentos_peca(tab, "e4")
        assert "d5" in {j.destino for j in jogadas}

    def test_rei_captura_peca_adversaria_adjacente(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.REI, Cor.BRANCA))
        tab.definir("d5", Peca(TipoPeca.PEAO, Cor.PRETA))
        jogada = next(j for j in gerar_movimentos_peca(tab, "e4") if j.destino == "d5")
        assert jogada.captura is not None

    def test_rei_nao_move_para_casa_propria(self):
        tab = Tabuleiro()
        tab.definir("e4", Peca(TipoPeca.REI, Cor.BRANCA))
        tab.definir("d5", Peca(TipoPeca.PEAO, Cor.BRANCA))
        assert "d5" not in {j.destino for j in gerar_movimentos_peca(tab, "e4")}

    def test_rei_gera_roque_menor_brancas(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K2R w K -")
        jogada = next(j for j in gerar_movimentos_peca(tab, "e1") if j.e_roque)
        assert jogada.destino == "g1"

    def test_rei_gera_roque_maior_brancas(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/R3K3 w Q -")
        jogada = next(j for j in gerar_movimentos_peca(tab, "e1") if j.e_roque)
        assert jogada.destino == "c1"

    def test_rei_nao_gera_roque_sem_direito(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4K2R w - -")
        assert not any(j.e_roque for j in gerar_movimentos_peca(tab, "e1"))

    def test_rei_nao_gera_roque_se_caminho_bloqueado(self):
        tab = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/4KB1R w K -")
        assert not any(j.e_roque for j in gerar_movimentos_peca(tab, "e1"))
