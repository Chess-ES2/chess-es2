#API REST — Rotas Flask

from __future__ import annotations
import uuid
from flask import Flask, jsonify, request, abort

from motor.jogo import Jogo, JogadaInvalida

app = Flask(__name__)

# Armazenamento em memória das partidas
partidas: dict[str, Jogo] = {}

def _obter_partida(id_partida: str) -> Jogo:
    jogo = partidas.get(id_partida)
    if jogo is None:
        abort(404, description=f"Partida '{id_partida}' não encontrada.")
    return jogo

def _estado_jogo(jogo: Jogo, id_partida: str) -> dict:
    return {
        "id":    id_partida,
        "fen":   jogo.tabuleiro.para_fen(),
        "turno": "brancas" if jogo.turno_atual().value == "w" else "pretas",
    }

@app.post("/partida/nova")
def nova_partida():
    #Cria uma nova partida com posição inicial ou FEN customizada.
    dados = request.get_json(silent=True) or {}
    fen = dados.get("fen")

    try:
        jogo = Jogo.de_fen(fen) if fen else Jogo.novo()
    except ValueError as e:
        abort(400, description=str(e))

    id_partida = str(uuid.uuid4())
    partidas[id_partida] = jogo
    return jsonify(_estado_jogo(jogo, id_partida)), 201

@app.get("/partida/<id_partida>/estado")
def estado_partida(id_partida: str):
    #Retorna a disposição das peças e o turno atual.
    jogo = _obter_partida(id_partida)
    return jsonify(_estado_jogo(jogo, id_partida))

@app.get("/partida/<id_partida>/jogadas")
def movimentos_validos(id_partida: str):
    #Retorna todos os movimentos válidos para o jogador da vez.
    jogo = _obter_partida(id_partida)
    movimentos = jogo.movimentos_validos()
    return jsonify({
        "turno":     "brancas" if jogo.turno_atual().value == "w" else "pretas",
        "movimentos": [m.para_dict() for m in movimentos],
    })

@app.get("/partida/<id_partida>/jogadas/<casa>")
def movimentos_da_casa(id_partida: str, casa: str):
    #Retorna os movimentos válidos da peça na casa indicada.
    jogo = _obter_partida(id_partida)
    movimentos = jogo.movimentos_validos(casa=casa)
    return jsonify({
        "casa":       casa,
        "movimentos": [m.para_dict() for m in movimentos],
    })

@app.post("/partida/<id_partida>/jogada")
def executar_jogada(id_partida: str):
    # Executa um movimento no tabuleiro e alterna o turno.

    jogo = _obter_partida(id_partida)
    dados = request.get_json(silent=True) or {}

    origem = dados.get("origem")
    destino = dados.get("destino")
    if not origem or not destino:
        abort(400, description="Campos 'origem' e 'destino' são obrigatórios.")

    try:
        jogada = jogo.fazer_jogada(origem, destino)
    except JogadaInvalida as e:
        abort(400, description=str(e))

    return jsonify({
        "jogada": jogada.para_dict(),
        "estado": _estado_jogo(jogo, id_partida),
    })

@app.errorhandler(400)
def erro_requisicao(e):
    return jsonify({"erro": str(e.description)}), 400

@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": str(e.description)}), 404
