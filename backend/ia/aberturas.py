import json
import random
import os
from motor.movimentacao import Jogada

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_LIVRO = os.path.join(DIRETORIO_ATUAL, "aberturas.json")

LIVRO_ABERTURAS = {}
try:
    if os.path.exists(CAMINHO_LIVRO):
        with open(CAMINHO_LIVRO, 'r', encoding='utf-8') as arquivo:
            LIVRO_ABERTURAS = json.load(arquivo)
except Exception as e:
    print(f"Aviso: Não foi possível carregar o livro de aberturas. Erro: {e}")

def consultar_livro(fen_atual: str, movimentos_validos: list[Jogada]) -> Jogada | None:
    """Busca um lance no dicionário JSON usando o FEN atual."""
    if not LIVRO_ABERTURAS:
        return None

    partes = fen_atual.strip().split()
    if len(partes) < 2:
        return None

    fen_base = f"{partes[0]} {partes[1]}"

    chave_usada = None
    for chave_json in LIVRO_ABERTURAS.keys():
        if chave_json.startswith(fen_base):
            chave_usada = chave_json
            break

    if not chave_usada:
        return None

    lances = LIVRO_ABERTURAS[chave_usada]
    
    if not lances:
        return None
        
    lances_ordenados = sorted(lances, key=lambda x: x.get("games", 0), reverse=True)
    top_3 = lances_ordenados[:3]
    lance_escolhido = random.choice(top_3)
    lance_uci = lance_escolhido["uci"]

    for jogada in movimentos_validos:
        if f"{jogada.origem}{jogada.destino}" == lance_uci[:4]:
            return jogada
            
    return None