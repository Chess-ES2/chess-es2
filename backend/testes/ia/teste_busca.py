import pytest
from unittest.mock import MagicMock

from ia import busca
from ia.busca import (
    PROFUNDIDADES,
    VALOR_XEQUE_MATE,
    _negamax,
    _nota,
    _ordenar,
    melhor_jogada,
)
from motor.movimentacao import Jogada
from motor.peca import Cor, Peca, TipoPeca
from motor.tabuleiro import Tabuleiro
from motor.validacao import esta_em_xeque, obter_todos_movimentos_validos


# ============================================================================
# 1. TESTES DE _nota() — V(G) = 2
# ============================================================================

class TestNota:
    """Valida a normalização da avaliação conforme o turno (convenção Negamax)."""

    def test_nota_turno_brancas_mantem_valor_positivo(self, monkeypatch):
        """Caminho N1: Brancas jogam. A nota deve manter o sinal de avaliar()."""
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA

        mock_avaliar = MagicMock(return_value=150)
        monkeypatch.setattr(busca, "avaliar", mock_avaliar)

        resultado = _nota(tabuleiro)

        assert resultado == 150
        mock_avaliar.assert_called_once_with(tabuleiro)

    def test_nota_turno_pretas_inverte_sinal(self, monkeypatch):
        """Caminho N2: Pretas jogam. A nota deve inverter o sinal de avaliar()."""
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.PRETA

        mock_avaliar = MagicMock(return_value=150)
        monkeypatch.setattr(busca, "avaliar", mock_avaliar)

        resultado = _nota(tabuleiro)

        assert resultado == -150
        mock_avaliar.assert_called_once_with(tabuleiro)


# ============================================================================
# 2. TESTES DE _ordenar() — V(G) = 1 (Classes de Equivalência de Dados)
# ============================================================================

class TestOrdenar:
    """Valida a ordenação heurística de lances (capturas e promoções primeiro).

    Importante: V(G) = 1. As 4 combinações de captura e promoção constituem
    classes de equivalência da partição de dados de entrada, e não caminhos
    independentes de fluxo de controle.
    """

    def test_ordenar_classes_de_equivalencia_e_preservacao(self):
        """Testa a prioridade das 4 classes de equivalência e a integridade da lista.

        Prioridade esperada (reverse=True):
        1. Captura + Promoção  (True, True)
        2. Captura simples     (True, False)
        3. Promoção simples    (False, True)
        4. Lance quieto        (False, False)
        """
        peca_branca = Peca(TipoPeca.PEAO, Cor.BRANCA)
        peca_alvo = Peca(TipoPeca.BISPO, Cor.PRETA)

        j_captura_promocao = Jogada(
            origem="a7", destino="b8", peca=peca_branca,
            captura=peca_alvo, promocao=TipoPeca.DAMA
        )
        j_captura = Jogada(
            origem="e4", destino="d5", peca=peca_branca,
            captura=peca_alvo
        )
        j_promocao = Jogada(
            origem="a7", destino="a8", peca=peca_branca,
            promocao=TipoPeca.DAMA
        )
        j_quieto = Jogada(
            origem="e2", destino="e4", peca=peca_branca
        )

        # Submete fora da ordem esperada
        desordenados = [j_quieto, j_captura, j_promocao, j_captura_promocao]
        ordenados = _ordenar(desordenados)

        # Verifica preservação de todos os lances
        assert len(ordenados) == 4
        assert all(j in ordenados for j in desordenados)

        # Verifica hierarquia estrita de ordenação
        assert ordenados[0] == j_captura_promocao
        assert ordenados[1] == j_captura
        assert ordenados[2] == j_promocao
        assert ordenados[3] == j_quieto

    def test_ordenar_lista_vazia(self):
        """Condição de contorno: lista vazia de movimentos deve retornar lista vazia."""
        assert _ordenar([]) == []


# ============================================================================
# 3. TESTES DE _negamax() — V(G) = 6 (Caminhos Independentes G1 a G6)
# ============================================================================

class TestNegamax:
    """Valida os caminhos básicos independentes do algoritmo Negamax com poda Alfa-Beta."""

    def test_negamax_profundidade_zero_retorna_nota(self, monkeypatch):
        """Caminho G1: Nó folha por profundidade.

        Deve retornar _nota() imediatamente e não gerar movimentos válidos.
        """
        tabuleiro = Tabuleiro.inicial()
        mock_nota = MagicMock(return_value=75)
        mock_movs = MagicMock()

        monkeypatch.setattr(busca, "_nota", mock_nota)
        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", mock_movs)

        resultado = _negamax(tabuleiro, profundidade=0, alpha=-1000, beta=1000)

        assert resultado == 75
        mock_nota.assert_called_once_with(tabuleiro)
        mock_movs.assert_not_called()

    def test_negamax_no_terminal_xeque_mate(self):
        """Caminho G2: Nó terminal em Xeque-Mate.

        Posição FEN: 7k/6Q1/5K2/8/8/8/8/8 b - -
        Pretas sem lances válidos e em xeque -> retorna -VALOR_XEQUE_MATE - profundidade.
        """
        fen_mate = "7k/6Q1/5K2/8/8/8/8/8 b - -"
        tabuleiro = Tabuleiro.de_fen(fen_mate)

        assert len(obter_todos_movimentos_validos(tabuleiro)) == 0
        assert esta_em_xeque(tabuleiro, tabuleiro.turno) is True

        profundidade = 2
        resultado = _negamax(tabuleiro, profundidade=profundidade, alpha=-2_000_000, beta=2_000_000)

        assert resultado == -VALOR_XEQUE_MATE - profundidade

    def test_negamax_no_terminal_afogamento(self):
        """Caminho G3: Nó terminal em Afogamento (Empate).

        Posição FEN: 7k/5Q2/6K1/8/8/8/8/8 b - -
        Pretas sem lances válidos e fora de xeque -> retorna 0.
        """
        fen_afogamento = "7k/5Q2/6K1/8/8/8/8/8 b - -"
        tabuleiro = Tabuleiro.de_fen(fen_afogamento)

        assert len(obter_todos_movimentos_validos(tabuleiro)) == 0
        assert esta_em_xeque(tabuleiro, tabuleiro.turno) is False

        resultado = _negamax(tabuleiro, profundidade=2, alpha=-2_000_000, beta=2_000_000)

        assert resultado == 0

    def test_negamax_uma_iteracao_sem_poda_argumentos_e_inversao(self, monkeypatch):
        """Caminho G4: Laço com exatamente 1 iteração sem poda Alfa-Beta.

        Verifica:
        - Profundidade decrementada (profundidade - 1).
        - Inversão dos limites de janela: (-beta, -alpha).
        - Atualização do valor acumulado e do alpha.
        """
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA
        lance_unico = Jogada(origem="e2", destino="e4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA))

        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", lambda tab: [lance_unico])
        monkeypatch.setattr(busca, "aplicar_jogada", lambda tab, j: None)

        chamadas_filho = []

        def mock_filho(tab, p, a, b):
            chamadas_filho.append({"prof": p, "alpha": a, "beta": b})
            return -50  # Pai receberá -(-50) = +50

        monkeypatch.setattr(busca, "_negamax", mock_filho)

        # Entrada: profundidade=3, alpha=-100, beta=200
        # Esperado no filho: profundidade=2, alpha=-200 (-beta), beta=100 (-alpha)
        resultado = _negamax(tabuleiro, profundidade=3, alpha=-100, beta=200)

        assert resultado == 50
        assert len(chamadas_filho) == 1
        assert chamadas_filho[0]["prof"] == 2
        assert chamadas_filho[0]["alpha"] == -200
        assert chamadas_filho[0]["beta"] == 100

    def test_negamax_poda_alfa_beta_interrompe_busca_e_descarta_posteriores(self, monkeypatch):
        """Caminho G5: Poda Alfa-Beta via break.

        Verifica:
        - Argumentos enviados à chamada recursiva: (-beta, -alpha).
        - O primeiro lance atinge alpha >= beta, acionando a condição de poda.
        - Movimentos posteriores ao corte NUNCA são avaliados.
        """
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA
        lances = [
            Jogada(origem="e2", destino="e4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA)),
            Jogada(origem="d2", destino="d4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA)),
            Jogada(origem="c2", destino="c4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA)),
        ]

        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", lambda tab: lances)
        lances_aplicados = []
        monkeypatch.setattr(busca, "aplicar_jogada", lambda tab, j: lances_aplicados.append(j))

        chamadas_recursivas = []

        def mock_negamax_recursivo(tab, p, a, b):
            chamadas_recursivas.append({"prof": p, "alpha": a, "beta": b})
            # Filho retorna -300 -> Pai calcula -(-300) = 300
            return -300

        monkeypatch.setattr(busca, "_negamax", mock_negamax_recursivo)

        # Chamada com profundidade=2, alpha=100, beta=200
        # No 1º lance: filho recebe prof=1, alpha=-200, beta=-100
        # Pai calcula valor = 300 -> alpha = max(100, 300) = 300
        # Condição 300 >= 200 (alpha >= beta) é VERDADEIRA -> break
        resultado = _negamax(tabuleiro, profundidade=2, alpha=100, beta=200)

        assert resultado == 300
        # Comprova que os argumentos foram invertidos corretamente
        assert chamadas_recursivas[0]["prof"] == 1
        assert chamadas_recursivas[0]["alpha"] == -200
        assert chamadas_recursivas[0]["beta"] == -100

        # Comprova que EXATAMENTE 1 lance foi aplicado e avaliado; lances 2 e 3 foram podados
        assert len(chamadas_recursivas) == 1
        assert len(lances_aplicados) == 1
        assert lances_aplicados[0] == lances[0]

    def test_negamax_multiplas_iteracoes_sem_poda_re_percurso_do_laco(self, monkeypatch):
        """Caminho G6: Laço com múltiplas iterações sem poda.

        Verifica:
        - O laço executa pelo menos duas iterações.
        - Em ambas, alpha < beta permanece (condição de poda não dispara).
        - A execução retorna ao cabeçalho do laço entre as iterações.
        - O valor retornado é o máximo acumulado entre todos os filhos.
        """
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA
        lances = [
            Jogada(origem="e2", destino="e4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA)),
            Jogada(origem="d2", destino="d4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA)),
        ]

        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", lambda tab: lances)
        monkeypatch.setattr(busca, "aplicar_jogada", lambda tab, j: None)

        # Lance 1: filho retorna -100 -> pai calcula +100
        # Lance 2: filho retorna -250 -> pai calcula +250
        respostas = [-100, -250]
        chamadas = []

        def mock_negamax_recursivo(tab, p, a, b):
            chamadas.append({"prof": p, "alpha": a, "beta": b})
            return respostas.pop(0)

        monkeypatch.setattr(busca, "_negamax", mock_negamax_recursivo)

        # Com alpha=-500 e beta=500:
        # Iteração 1: valor=100, alpha=100 (100 < 500) -> volta ao cabeçalho
        # Iteração 2: filho recebe alpha=-500, beta=-100 (-alpha atualizado!)
        #             valor=max(100, 250)=250, alpha=250 (250 < 500) -> laço termina por esgotamento
        resultado = _negamax(tabuleiro, profundidade=2, alpha=-500, beta=500)

        assert resultado == 250
        assert len(chamadas) == 2
        # Comprova que o beta do filho na 2ª iteração recebeu o alpha atualizado da 1ª (-100)
        assert chamadas[1]["beta"] == -100


# ============================================================================
# 4. TESTES DE melhor_jogada() — V(G) = 5 (Caminhos Independentes M1 a M5)
# ============================================================================

class TestMelhorJogada:
    """Valida a seleção da melhor jogada integrando livro de abertura e busca."""

    def test_melhor_jogada_sem_movimentos_retorna_none(self, monkeypatch):
        """Caminho M1: Posição terminal sem lances válidos. Retorna None e não consulta livro."""
        tabuleiro = Tabuleiro.de_fen("7k/6Q1/5K2/8/8/8/8/8 b - -")
        mock_livro = MagicMock()
        monkeypatch.setattr(busca, "consultar_livro", mock_livro)

        resultado = melhor_jogada(tabuleiro, profundidade=2)

        assert resultado is None
        mock_livro.assert_not_called()

    def test_melhor_jogada_retorna_lance_do_livro_quando_presente(self, monkeypatch):
        """Caminho M2: Lance encontrado no livro de abertura.

        Retorna a jogada do livro e não executa a busca Negamax.
        """
        tabuleiro = Tabuleiro.inicial()
        lance_livro = Jogada(
            origem="e2", destino="e4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA)
        )

        monkeypatch.setattr(busca, "consultar_livro", lambda fen, movs: lance_livro)
        mock_negamax = MagicMock()
        monkeypatch.setattr(busca, "_negamax", mock_negamax)

        resultado = melhor_jogada(tabuleiro, profundidade=2)

        assert resultado == lance_livro
        mock_negamax.assert_not_called()

    def test_melhor_jogada_primeiro_lance_melhora_alpha(self, monkeypatch):
        """Caminho M3: Posição com 1 lance fora do livro.

        O primeiro lance supera o alpha inicial (-2_000_000) e é retornado.
        """
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA
        lance_unico = Jogada(origem="e2", destino="e4", peca=Peca(TipoPeca.PEAO, Cor.BRANCA))

        monkeypatch.setattr(busca, "consultar_livro", lambda fen, movs: None)
        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", lambda tab: [lance_unico])
        monkeypatch.setattr(busca, "aplicar_jogada", lambda tab, j: None)

        # _negamax retorna -50 -> valor = -(-50) = 50 > -2M -> atualiza alpha e melhor
        monkeypatch.setattr(busca, "_negamax", lambda tab, p, a, b: -50)

        resultado = melhor_jogada(tabuleiro, profundidade=2)

        assert resultado == lance_unico

    def test_melhor_jogada_primeiro_melhora_e_segundo_nao_melhora(self, monkeypatch):
        """Caminho M4: Dois lances avaliados.

        O 1º lance melhora alpha. O 2º lance tem valor inferior e não melhora alpha.
        O 1º lance deve permanecer selecionado.
        """
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA
        lance_forte = Jogada(origem="e1", destino="e8", peca=Peca(TipoPeca.TORRE, Cor.BRANCA))
        lance_fraco = Jogada(origem="e1", destino="e2", peca=Peca(TipoPeca.TORRE, Cor.BRANCA))

        monkeypatch.setattr(busca, "consultar_livro", lambda fen, movs: None)
        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", lambda tab: [lance_forte, lance_fraco])
        monkeypatch.setattr(busca, "aplicar_jogada", lambda tab, j: None)

        # Inversão: valor = -_negamax(...)
        # Lance forte: _negamax = -100 -> valor = +100 (atualiza alpha=-2M para 100)
        # Lance fraco: _negamax = -40  -> valor = +40  (40 <= 100: ramo Falso de valor > alpha)
        respostas = [-100, -40]
        monkeypatch.setattr(busca, "_negamax", lambda tab, p, a, b: respostas.pop(0))

        resultado = melhor_jogada(tabuleiro, profundidade=2)

        assert resultado == lance_forte

    def test_melhor_jogada_melhorias_sucessivas_de_alpha(self, monkeypatch):
        """Caminho M5: Três lances avaliados com melhorias sucessivas.

        Sequência de valores:
        1. Lance 1: _negamax = -10 -> valor = 10 (melhora alpha: -2M -> 10)
        2. Lance 2: _negamax = -15 -> valor = 15 (melhora alpha novamente: 10 -> 15)
        3. Lance 3: _negamax = -8  -> valor = 8  (8 <= 15: descartado)

        Verifica se todos foram avaliados e se o Lance 2 é o retornado final.
        """
        tabuleiro = Tabuleiro()
        tabuleiro.turno = Cor.BRANCA
        j1 = Jogada(origem="a1", destino="a2", peca=Peca(TipoPeca.TORRE, Cor.BRANCA))
        j2 = Jogada(origem="b1", destino="b2", peca=Peca(TipoPeca.TORRE, Cor.BRANCA))
        j3 = Jogada(origem="c1", destino="c2", peca=Peca(TipoPeca.TORRE, Cor.BRANCA))

        monkeypatch.setattr(busca, "consultar_livro", lambda fen, movs: None)
        monkeypatch.setattr(busca, "obter_todos_movimentos_validos", lambda tab: [j1, j2, j3])
        monkeypatch.setattr(busca, "aplicar_jogada", lambda tab, j: None)

        respostas = [-10, -15, -8]
        avaliados = []

        def mock_negamax(tab, p, a, b):
            avaliados.append((p, a, b))
            return respostas.pop(0)

        monkeypatch.setattr(busca, "_negamax", mock_negamax)

        resultado = melhor_jogada(tabuleiro, profundidade=2)

        assert len(avaliados) == 3
        assert resultado == j2


# ============================================================================
# 5. TESTES COM POSIÇÕES REAIS (VALIDAÇÃO TÁTICA DO MOTOR)
# ============================================================================

class TestTaticasReais:
    """Valida o cálculo tático concreto da IA em tabuleiros reais sem mocks de busca."""

    def test_melhor_jogada_captura_dama_desprotegida(self):
        """Posição real: Dama preta pendurada em e5 atacada por Torre em e1.

        FEN: 4k3/8/8/4q3/8/8/8/4R1K1 w - -
        IA jogando de Brancas deve escolher a captura imediata e1e5.
        """
        tabuleiro = Tabuleiro.de_fen("4k3/8/8/4q3/8/8/8/4R1K1 w - -")
        jogada = melhor_jogada(tabuleiro, profundidade=1)

        assert jogada is not None
        assert jogada.origem == "e1"
        assert jogada.destino == "e5"

    def test_melhor_jogada_promove_peao_para_dama(self):
        """Posição real: Peão branco na 7ª fileira avança promovendo.

        FEN: 8/P7/8/8/8/8/k7/4K3 w - -
        IA jogando de Brancas deve escolher a promoção ótima para Dama (a7a8=q).
        """
        tabuleiro = Tabuleiro.de_fen("8/P7/8/8/8/8/k7/4K3 w - -")
        jogada = melhor_jogada(tabuleiro, profundidade=1)

        assert jogada is not None
        assert jogada.origem == "a7"
        assert jogada.destino == "a8"
        assert jogada.promocao == TipoPeca.DAMA

    def test_melhor_jogada_encontra_xeque_mate_do_corredor(self):
        """Posição real: Mate do corredor na 8ª fileira.

        FEN: 6k1/5ppp/8/8/8/8/8/4R1K1 w - -
        Com profundidade 2, a IA calcula a resposta adversária e seleciona e1e8#.
        """
        tabuleiro = Tabuleiro.de_fen("6k1/5ppp/8/8/8/8/8/4R1K1 w - -")
        jogada = melhor_jogada(tabuleiro, profundidade=2)

        assert jogada is not None
        assert jogada.origem == "e1"
        assert jogada.destino == "e8"

    def test_melhor_jogada_pretas_encontram_xeque_mate_do_corredor(self):
        """Posição real com turno das Pretas (Cor.PRETA).

        FEN: 4r1k1/8/8/8/8/8/5PPP/6K1 b - -
        Comprova que a simetria Negamax funciona quando a IA joga de Pretas,
        selecionando o mate imediato em e8e1#.
        """
        tabuleiro = Tabuleiro.de_fen("4r1k1/8/8/8/8/8/5PPP/6K1 b - -")
        assert tabuleiro.turno == Cor.PRETA

        jogada = melhor_jogada(tabuleiro, profundidade=2)

        assert jogada is not None
        assert jogada.origem == "e8"
        assert jogada.destino == "e1"

    def test_melhor_jogada_defende_xeque_capturando_dama(self):
        """Posição real: Rei branco sob xeque da Dama preta em e2.

        FEN: 4k3/8/8/8/8/8/4q3/4K3 w - -
        A IA identifica que o único lance legal de sobrevivência é capturar a Dama (e1e2).
        """
        tabuleiro = Tabuleiro.de_fen("4k3/8/8/8/8/8/4q3/4K3 w - -")
        assert esta_em_xeque(tabuleiro, tabuleiro.turno) is True

        jogada = melhor_jogada(tabuleiro, profundidade=1)

        assert jogada is not None
        assert jogada.origem == "e1"
        assert jogada.destino == "e2"


# ============================================================================
# 6. TESTES DE NÍVEIS DE PROFUNDIDADE (PROFUNDIDADES DA IA)
# ============================================================================

class TestProfundidadesIA:
    """Valida o mapeamento e o comportamento das dificuldades configuradas."""

    def test_mapeamento_dicionario_profundidades(self):
        """Verifica a integridade do dicionário PROFUNDIDADES do módulo busca."""
        assert PROFUNDIDADES == {"easy": 1, "medium": 2, "hard": 3}

    def test_diferenciacao_tatica_entre_easy_e_medium(self):
        """Comprova a expansão do horizonte tático conforme a profundidade.

        Na posição FEN '6k1/5ppp/8/8/8/8/8/4R1K1 w - -':
        - Dificuldade 'easy' (profundidade 1): não calcula resposta do adversário,
          escolhendo o lance posicionalmente atraente na 7ª fileira (e1e7).
        - Dificuldade 'medium' (profundidade 2): calcula 2 plies à frente,
          identifica o nó terminal de xeque-mate e escolhe e1e8#.
        """
        tabuleiro = Tabuleiro.de_fen("6k1/5ppp/8/8/8/8/8/4R1K1 w - -")

        lance_easy = melhor_jogada(tabuleiro, profundidade=PROFUNDIDADES["easy"])
        lance_medium = melhor_jogada(tabuleiro, profundidade=PROFUNDIDADES["medium"])

        assert lance_easy is not None
        assert lance_medium is not None

        # Easy escolhe e1e7 pela tabela posicional de torre na 7ª
        assert lance_easy.origem == "e1" and lance_easy.destino == "e7"

        # Medium enxerga o mate em 2 plies e joga e1e8#
        assert lance_medium.origem == "e1" and lance_medium.destino == "e8"
