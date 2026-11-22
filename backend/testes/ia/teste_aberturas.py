import pytest
from ia import aberturas
from ia.aberturas import LIVRO_ABERTURAS, consultar_livro
from motor.jogo import Jogo


class TestConsultarLivro:
    """Suíte de testes para a consulta ao livro de aberturas (aberturas.py)."""

    def test_livro_vazio_retorna_none(self, monkeypatch):
        """Caminho A1: Quando LIVRO_ABERTURAS está vazio, retorna None."""
        monkeypatch.setattr(aberturas, "LIVRO_ABERTURAS", {})
        jogo = Jogo.de_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")

        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None

    @pytest.mark.parametrize("fen_invalida", ["", "   ", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"])
    def test_fen_invalida_retorna_none(self, monkeypatch, fen_invalida):
        """Caminho A2: String FEN com menos de 2 partes (sem turno) retorna None."""
        monkeypatch.setattr(
            aberturas,
            "LIVRO_ABERTURAS",
            {"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": [{"uci": "e2e4", "games": 100}]},
        )
        jogo = Jogo.de_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")

        resultado = consultar_livro(fen_invalida, jogo.movimentos_validos())

        assert resultado is None

    def test_posicao_fora_do_livro_retorna_none(self, monkeypatch):
        """Caminho A3: FEN válida com 2 partes, mas não catalogada no livro, retorna None."""
        monkeypatch.setattr(
            aberturas,
            "LIVRO_ABERTURAS",
            {"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -": [{"uci": "e7e5", "games": 500}]},
        )
        jogo = Jogo.de_fen("7k/6Q1/5K2/8/8/8/8/8 b - -")

        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None

    def test_posicao_com_lista_de_lances_vazia_retorna_none(self, monkeypatch):
        """Caminho A4: Posição encontrada no livro, mas com lista de lances vazia (not lances).

        Cobre a linha 39 de aberturas.py: `if not lances: return None`.
        """
        fen_chave = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        monkeypatch.setattr(aberturas, "LIVRO_ABERTURAS", {fen_chave: []})

        jogo = Jogo.novo()
        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None

    def test_retorna_jogada_valida_do_top_3(self, monkeypatch):
        """Caminho A5: Seleciona aleatoriamente entre o top 3 de lances válidos."""
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

    def test_retorna_jogada_quando_menos_de_tres_lances_disponiveis(self, monkeypatch):
        """Caminho A5 (borda): Seleção quando a posição possui menos de 3 lances (ex.: apenas 1 lance)."""
        fen_chave = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        lances_simulados = [
            {"uci": "e2e4", "games": 500}
        ]
        monkeypatch.setattr(aberturas, "LIVRO_ABERTURAS", {fen_chave: lances_simulados})

        jogo = Jogo.novo()
        jogada = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert jogada is not None
        assert f"{jogada.origem}{jogada.destino}" == "e2e4"

    def test_lance_do_livro_ausente_nos_movimentos_validos_retorna_none(self, monkeypatch):
        """Caminho A6: Lance do livro é ilegal para o jogador da vez (não está em movimentos_validos)."""
        fen_chave = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        monkeypatch.setattr(
            aberturas,
            "LIVRO_ABERTURAS",
            {fen_chave: [{"uci": "e7e5", "games": 999}]},
        )
        jogo = Jogo.novo()

        resultado = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert resultado is None

    def test_consulta_livro_real_posicao_inicial(self):
        """Integração real: Consulta a posição inicial diretamente no livro carregado (aberturas.json).

        Garante que a base real de 29,8 MB é consultada sem mock e retorna um lance legal de abertura.
        """
        jogo = Jogo.novo()
        jogada = consultar_livro(jogo.tabuleiro.para_fen(), jogo.movimentos_validos())

        assert jogada is not None
        lances_iniciais_validos = {f"{m.origem}{m.destino}" for m in jogo.movimentos_validos()}
        assert f"{jogada.origem}{jogada.destino}" in lances_iniciais_validos

    def test_evidencia_defeito_producao_chave_games_vs_count(self):
        """Documentação de teste do defeito identificado no código de produção.

        No arquivo real aberturas.json, o campo de contagem é 'count', enquanto
        em aberturas.py linha 42 o código busca 'games'.
        Este teste documenta a discrepância sem quebrar a suíte.
        """
        assert len(LIVRO_ABERTURAS) > 0
        primeira_chave = next(iter(LIVRO_ABERTURAS))
        primeiro_lance = LIVRO_ABERTURAS[primeira_chave][0]

        # Evidência: o JSON real usa 'count' e não 'games'
        assert "count" in primeiro_lance
        assert "games" not in primeiro_lance
