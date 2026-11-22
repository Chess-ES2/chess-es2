import time

from ia.busca import (
    CONFIG_DIFICULDADES,
    PROFUNDIDADES,
    hash_zobrist,
    melhor_jogada,
    melhor_jogada_dificuldade,
)
from motor.tabuleiro import Tabuleiro


class TestBusca:
    def test_encontra_mate_em_1(self):
        # Mate em 1: Dama h5 captura f7 ou vai para f7 com apoio do bispo em c4
        tab = Tabuleiro.de_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq -")
        jogada = melhor_jogada(tab, 2, usar_livro=False)
        assert jogada is not None
        assert (jogada.origem, jogada.destino) == ("h5", "f7")

    def test_quiescencia_evita_entregar_dama(self):
        # Peão preto em d5 defendido por peão em e6; Dama branca em d4 não deve capturar d5
        tab = Tabuleiro.de_fen("4k3/8/4p3/3p4/3Q4/8/8/4K3 w - -")
        jogada = melhor_jogada(tab, 1, usar_quiescencia=True, usar_livro=False)
        assert jogada is not None
        assert (jogada.origem, jogada.destino) != ("d4", "d5")

    def test_zobrist_deterministico_e_sensivel_ao_turno(self):
        t_w = Tabuleiro.de_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -")
        t_b = Tabuleiro.de_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -")
        assert hash_zobrist(t_w) == hash_zobrist(t_w.copiar())
        assert hash_zobrist(t_w) != hash_zobrist(t_b)

    def test_dificuldade_expert_configurada_e_respeita_orcamento(self):
        assert "expert" in CONFIG_DIFICULDADES
        assert "expert" in PROFUNDIDADES
        tab = Tabuleiro.de_fen("r1b2rk1/pp2bppp/2n1pn2/q1pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 w - -")
        t0 = time.perf_counter()
        jogada = melhor_jogada_dificuldade(tab, "expert")
        dt_ms = (time.perf_counter() - t0) * 1000
        assert jogada is not None
        # Margem generosa sobre o orçamento de 1400ms
        assert dt_ms < 2500
