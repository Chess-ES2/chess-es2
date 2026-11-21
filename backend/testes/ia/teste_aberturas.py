import pytest
from ia import aberturas
from ia.aberturas import consultar_livro
from motor.jogo import Jogo


class TestConsultarLivro:
    def test_livro_vazio_retorna_none(self, monkeypatch):
        monkeypatch.setattr(aberturas, "LIVRO_ABERTURAS", {})
        jogo = Jogo.de_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")

        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None

    @pytest.mark.parametrize("fen_invalida", ["", "   ", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"])
    def test_fen_invalida_retorna_none(self, monkeypatch, fen_invalida):
        monkeypatch.setattr(
            aberturas,
            "LIVRO_ABERTURAS",
            {"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": [{"uci": "e2e4", "games": 100}]},
        )
        jogo = Jogo.de_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")

        resultado = consultar_livro(fen_invalida, jogo.movimentos_validos())

        assert resultado is None

    def test_posicao_fora_do_livro_retorna_none(self, monkeypatch):
        monkeypatch.setattr(
            aberturas,
            "LIVRO_ABERTURAS",
            {"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -": [{"uci": "e7e5", "games": 500}]},
        )
        jogo = Jogo.de_fen("7k/6Q1/5K2/8/8/8/8/8 b")

        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None

    def test_retorna_jogada_valida_do_top_3(self, monkeypatch):
        fen_chave = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        lances_simulados = [
            {"uci": "e2e4", "games": 1000},
            {"uci": "d2d4", "games": 800},
            {"uci": "g1f3", "games": 600},
            {"uci": "c2c4", "games": 400},
            {"uci": "a2a3", "games": 10},
        ]
        monkeypatch.setattr(aberturas, "LIVRO_ABERTURAS", {fen_chave: lances_simulados})

        jogo = Jogo.novo()
        movimentos_validos = jogo.movimentos_validos()

        top_3_coords = {"e2e4", "d2d4", "g1f3"}
        for _ in range(30):
            jogada = consultar_livro(jogo.tabuleiro.para_fen(), movimentos_validos)
            assert jogada is not None
            assert f"{jogada.origem}{jogada.destino}" in top_3_coords

    def test_lance_do_livro_ausente_nos_movimentos_validos_retorna_none(self, monkeypatch):
        fen_chave = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        monkeypatch.setattr(
            aberturas,
            "LIVRO_ABERTURAS",
            {fen_chave: [{"uci": "e7e5", "games": 999}]},
        )
        jogo = Jogo.novo()

        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None