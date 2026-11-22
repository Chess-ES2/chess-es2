#Testes de integração da API REST: HTTP -> Flask -> Jogo -> motor/ia

from __future__ import annotations

import pytest

from api.rotas import app, partidas

FEN_INICIAL = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"
FEN_MATE_DO_LOUCO = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w"
FEN_PROMOCAO = "8/7P/8/8/8/8/8/K6k w"


@pytest.fixture(autouse=True)
def partidas_limpas():
    """Zera o armazenamento em memória entre os testes.

    A API guarda as partidas num dicionário global do módulo, então sem isso um
    teste enxergaria as partidas criadas pelo anterior.
    """
    partidas.clear()
    yield
    partidas.clear()


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    return app.test_client()


def criar_partida(cliente, fen: str | None = None) -> str:
    corpo = {"fen": fen} if fen else {}
    resposta = cliente.post("/partida/nova", json=corpo)
    assert resposta.status_code == 201
    return resposta.get_json()["id"]


def jogar(cliente, id_partida: str, origem: str, destino: str, promocao: str | None = None):
    corpo = {"origem": origem, "destino": destino}
    if promocao is not None:
        corpo["promocao"] = promocao
    return cliente.post(f"/partida/{id_partida}/jogada", json=corpo)


# ============================================================================
# 1. POST /partida/nova
# ============================================================================

class TestNovaPartida:
    """Criação de partida: posição inicial, FEN customizada e FEN inválida."""

    def test_nova_partida_retorna_201_com_estado_inicial(self, cliente):
        resposta = cliente.post("/partida/nova", json={})

        assert resposta.status_code == 201
        estado = resposta.get_json()
        assert estado["id"]
        assert estado["fen"] == FEN_INICIAL
        assert estado["turno"] == "brancas"
        assert estado["xeque_mate"] is False
        assert estado["cp"] == 0

    def test_nova_partida_com_fen_customizada(self, cliente):
        resposta = cliente.post("/partida/nova", json={"fen": FEN_MATE_DO_LOUCO})

        assert resposta.status_code == 201
        assert resposta.get_json()["xeque_mate"] is True

    @pytest.mark.parametrize("fen", ["   ", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"])
    def test_nova_partida_com_fen_invalida_retorna_400(self, cliente, fen):
        resposta = cliente.post("/partida/nova", json={"fen": fen})

        assert resposta.status_code == 400
        assert "erro" in resposta.get_json()

    def test_nova_partida_com_fen_sem_reis_retorna_400(self, cliente):
        """FEN sintaticamente válida mas sem reis virava 500 antes da correção da rota."""
        resposta = cliente.post("/partida/nova", json={"fen": "8/8/8 w"})

        assert resposta.status_code == 400
        assert "Rei" in resposta.get_json()["erro"]
        assert partidas == {}


# ============================================================================
# 2. GET /partida/<id>/estado e /jogadas
# ============================================================================

class TestConsultaDeEstado:
    """Leitura do estado e dos movimentos válidos pela camada HTTP."""

    def test_estado_retorna_o_mesmo_fen_da_criacao(self, cliente):
        id_partida = criar_partida(cliente)

        resposta = cliente.get(f"/partida/{id_partida}/estado")

        assert resposta.status_code == 200
        estado = resposta.get_json()
        assert estado["id"] == id_partida
        assert estado["fen"] == FEN_INICIAL

    def test_estado_de_partida_inexistente_retorna_404(self, cliente):
        resposta = cliente.get("/partida/nao-existe/estado")

        assert resposta.status_code == 404
        assert "não encontrada" in resposta.get_json()["erro"]

    def test_jogadas_retorna_os_20_lances_iniciais(self, cliente):
        id_partida = criar_partida(cliente)

        corpo = cliente.get(f"/partida/{id_partida}/jogadas").get_json()

        assert corpo["turno"] == "brancas"
        assert len(corpo["movimentos"]) == 20

    def test_jogadas_da_casa_traz_apenas_os_lances_daquela_peca(self, cliente):
        id_partida = criar_partida(cliente)

        corpo = cliente.get(f"/partida/{id_partida}/jogadas/e2").get_json()

        assert [m["destino"] for m in corpo["movimentos"]] == ["e3", "e4"]

    @pytest.mark.parametrize("casa", ["e7", "zz"])
    def test_jogadas_de_casa_sem_peca_da_vez_retorna_lista_vazia(self, cliente, casa):
        id_partida = criar_partida(cliente)

        corpo = cliente.get(f"/partida/{id_partida}/jogadas/{casa}").get_json()

        assert corpo["movimentos"] == []

    def test_contrato_do_movimento_tem_todas_as_chaves(self, cliente):
        id_partida = criar_partida(cliente)

        movimento = cliente.get(f"/partida/{id_partida}/jogadas").get_json()["movimentos"][0]

        assert set(movimento) == {
            "origem", "destino", "peca", "captura",
            "e_roque", "e_en_passant", "promocao",
        }


# ============================================================================
# 3. POST /partida/<id>/jogada
# ============================================================================

class TestExecucaoDeJogada:
    """Execução de lances pela API, incluindo validação e promoção."""

    def test_jogada_valida_altera_fen_e_turno(self, cliente):
        id_partida = criar_partida(cliente)

        resposta = jogar(cliente, id_partida, "e2", "e4")

        assert resposta.status_code == 200
        corpo = resposta.get_json()
        assert corpo["jogada"]["destino"] == "e4"
        assert corpo["estado"]["turno"] == "pretas"
        assert "4P3" in corpo["estado"]["fen"]

    @pytest.mark.parametrize("corpo", [{}, {"origem": "e2"}])
    def test_jogada_sem_origem_ou_destino_retorna_400(self, cliente, corpo):
        id_partida = criar_partida(cliente)

        resposta = cliente.post(f"/partida/{id_partida}/jogada", json=corpo)

        assert resposta.status_code == 400
        assert "obrigatórios" in resposta.get_json()["erro"]

    def test_jogada_ilegal_retorna_400_e_nao_altera_o_estado(self, cliente):
        id_partida = criar_partida(cliente)

        resposta = jogar(cliente, id_partida, "e2", "e5")

        assert resposta.status_code == 400
        assert cliente.get(f"/partida/{id_partida}/estado").get_json()["fen"] == FEN_INICIAL

    def test_promocao_invalida_retorna_400(self, cliente):
        id_partida = criar_partida(cliente, FEN_PROMOCAO)

        resposta = jogar(cliente, id_partida, "h7", "h8", promocao="rei")

        assert resposta.status_code == 400
        assert "promoção inválido" in resposta.get_json()["erro"]

    @pytest.mark.parametrize("promocao", ["q", "n"])
    def test_promocao_valida_troca_o_peao_pela_peca_escolhida(self, cliente, promocao):
        id_partida = criar_partida(cliente, FEN_PROMOCAO)

        resposta = jogar(cliente, id_partida, "h7", "h8", promocao=promocao)

        assert resposta.status_code == 200
        corpo = resposta.get_json()
        assert corpo["jogada"]["promocao"] == promocao
        assert corpo["estado"]["fen"].startswith(f"7{promocao.upper()}")

    def test_jogada_em_partida_inexistente_retorna_404(self, cliente):
        resposta = jogar(cliente, "nao-existe", "e2", "e4")

        assert resposta.status_code == 404


# ============================================================================
# 4. POST /partida/<id>/desfazer
# ============================================================================

class TestDesfazer:
    """Retorno ao estado anterior pelo endpoint de desfazer."""

    def test_desfazer_restaura_o_fen_inicial(self, cliente):
        id_partida = criar_partida(cliente)
        jogar(cliente, id_partida, "e2", "e4")

        resposta = cliente.post(f"/partida/{id_partida}/desfazer")

        assert resposta.status_code == 200
        corpo = resposta.get_json()
        assert corpo["jogada"]["destino"] == "e4"
        assert corpo["estado"]["fen"] == FEN_INICIAL
        assert corpo["estado"]["turno"] == "brancas"

    def test_desfazer_sem_jogadas_retorna_400(self, cliente):
        id_partida = criar_partida(cliente)

        resposta = cliente.post(f"/partida/{id_partida}/desfazer")

        assert resposta.status_code == 400
        assert "Não há jogadas para desfazer" in resposta.get_json()["erro"]

    def test_desfazer_remove_apenas_a_ultima_jogada(self, cliente):
        id_partida = criar_partida(cliente)
        jogar(cliente, id_partida, "e2", "e4")
        jogar(cliente, id_partida, "e7", "e5")
        jogar(cliente, id_partida, "g1", "f3")

        resposta = cliente.post(f"/partida/{id_partida}/desfazer")

        assert resposta.status_code == 200
        assert resposta.get_json()["estado"]["turno"] == "brancas"
        jogadas = cliente.get(f"/partida/{id_partida}/jogadas").get_json()["movimentos"]
        assert any(m["destino"] == "f3" for m in jogadas)


# ============================================================================
# 5. POST /partida/<id>/bot
# ============================================================================

class TestJogadaDoBot:
    """Lance da IA sob demanda pela API."""

    def test_bot_devolve_uma_jogada_legal_e_alterna_o_turno(self, cliente):
        id_partida = criar_partida(cliente)

        resposta = cliente.post(f"/partida/{id_partida}/bot", json={"dificuldade": "medium"})

        assert resposta.status_code == 200
        corpo = resposta.get_json()
        assert corpo["jogada"]["origem"]
        assert corpo["estado"]["turno"] == "pretas"

    def test_bot_sem_jogadas_disponiveis_retorna_400(self, cliente):
        id_partida = criar_partida(cliente, FEN_MATE_DO_LOUCO)

        resposta = cliente.post(f"/partida/{id_partida}/bot", json={"dificuldade": "easy"})

        assert resposta.status_code == 400
        assert "Não há jogadas disponíveis" in resposta.get_json()["erro"]


# ============================================================================
# 6. Integração ponta a ponta pela API
# ============================================================================

class TestFluxoCompleto:
    """Fluxos reais atravessando HTTP -> Flask -> Jogo -> motor -> avaliacao."""

    def test_mate_do_louco_e_detectado_ao_final_da_sequencia(self, cliente):
        id_partida = criar_partida(cliente)

        for origem, destino in [("f2", "f3"), ("e7", "e5"), ("g2", "g4")]:
            assert jogar(cliente, id_partida, origem, destino).status_code == 200

        resposta = jogar(cliente, id_partida, "d8", "h4")

        assert resposta.status_code == 200
        estado = resposta.get_json()["estado"]
        assert estado["xeque_mate"] is True
        assert cliente.get(f"/partida/{id_partida}/jogadas").get_json()["movimentos"] == []

    def test_partida_humano_vs_bot_por_cinco_rodadas(self, cliente):
        id_partida = criar_partida(cliente)
        lances_humano = [("e2", "e4"), ("d2", "d4"), ("b1", "c3")]

        for origem, destino in lances_humano:
            assert jogar(cliente, id_partida, origem, destino).status_code == 200
            resposta_bot = cliente.post(f"/partida/{id_partida}/bot", json={"dificuldade": "easy"})
            assert resposta_bot.status_code == 200
            assert resposta_bot.get_json()["estado"]["turno"] == "brancas"

        assert len(partidas[id_partida].historico) == len(lances_humano) * 2

    def test_jogada_e_desfazer_preservam_isolamento_entre_partidas(self, cliente):
        primeira = criar_partida(cliente)
        segunda = criar_partida(cliente)

        jogar(cliente, primeira, "e2", "e4")

        assert cliente.get(f"/partida/{segunda}/estado").get_json()["fen"] == FEN_INICIAL
        assert cliente.get(f"/partida/{primeira}/estado").get_json()["turno"] == "pretas"
