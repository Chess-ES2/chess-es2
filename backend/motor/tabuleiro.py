from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field

from motor.peca import Cor, Peca, TipoPeca

COLUNAS = "abcdefgh"
LINHAS  = "12345678"

# Posição inicial padrão das peças e turno das brancas
FEN_INICIAL = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"

def casa_valida(casa: str) -> bool:
    return (
        len(casa) == 2
        and casa[0] in COLUNAS
        and casa[1] in LINHAS
    )

def coordenadas(casa: str) -> tuple[int, int]:
    #Converte notação algebrica para indices (coluna, linha) com base 0.
    return COLUNAS.index(casa[0]), int(casa[1]) - 1

def de_coordenadas(col: int, lin: int) -> str | None:
    #Converte índices (coluna, linha) para notação algebrica.
    if 0 <= col <= 7 and 0 <= lin <= 7:
        return f"{COLUNAS[col]}{LINHAS[lin]}"
    return None

@dataclass
class Tabuleiro:
    pecas: dict[str, Peca] = field(default_factory=dict)
    turno: Cor             = Cor.BRANCA
    direitos_roque: dict[str, bool] = field(default_factory=lambda: {"K": True, "Q": True, "k": True, "q": True})
    casa_en_passant: str | None = None
    _formato_completo: bool = False

    # Construtores

    @staticmethod
    def inicial() -> Tabuleiro:
        return Tabuleiro.de_fen(FEN_INICIAL)

    @staticmethod
    def de_fen(fen: str) -> Tabuleiro:
        """Parseia a disposição de peças e o turno a partir de uma FEN.
        Suporta tanto FEN simplificada ('<posicao> <turno>') quanto FEN completa."""
        partes = fen.strip().split()
        if len(partes) < 2:
            raise ValueError(f"FEN inválida: esperados ao menos posição e turno: '{fen}'")

        posicao, turno_str = partes[0], partes[1]

        pecas: dict[str, Peca] = {}
        linha_idx = 7  # FEN começa pela linha 8 (índice 7)
        for linha_fen in posicao.split("/"):
            col_idx = 0
            for char in linha_fen:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    casa = f"{COLUNAS[col_idx]}{LINHAS[linha_idx]}"
                    pecas[casa] = Peca.de_char_fen(char)
                    col_idx += 1
            linha_idx -= 1

        turno = Cor.BRANCA if turno_str.lower() == "w" else Cor.PRETA

        direitos_roque = {"K": True, "Q": True, "k": True, "q": True}
        casa_en_passant = None
        formato_completo = len(partes) >= 3

        if len(partes) >= 3:
            roque_str = partes[2]
            direitos_roque = {
                "K": "K" in roque_str,
                "Q": "Q" in roque_str,
                "k": "k" in roque_str,
                "q": "q" in roque_str,
            }

        if len(partes) >= 4:
            ep_str = partes[3]
            casa_en_passant = None if ep_str == "-" else ep_str

        return Tabuleiro(
            pecas=pecas,
            turno=turno,
            direitos_roque=direitos_roque,
            casa_en_passant=casa_en_passant,
            _formato_completo=formato_completo,
        )

    #Serialização:

    def para_fen(self) -> str:
        linhas_fen: list[str] = []

        for lin in range(7, -1, -1):
            trecho = ""
            vazias = 0
            for col in range(8):
                casa = f"{COLUNAS[col]}{LINHAS[lin]}"
                peca = self.pecas.get(casa)
                if peca:
                    if vazias:
                        trecho += str(vazias)
                        vazias = 0
                    trecho += peca.para_char_fen()
                else:
                    vazias += 1
            if vazias:
                trecho += str(vazias)
            linhas_fen.append(trecho)

        posicao = "/".join(linhas_fen)
        turno_str = "w" if self.turno == Cor.BRANCA else "b"

        if self._formato_completo:
            roque_chars = "".join(k for k, v in self.direitos_roque.items() if v) or "-"
            ep_char = self.casa_en_passant or "-"
            return f"{posicao} {turno_str} {roque_chars} {ep_char}"

        return f"{posicao} {turno_str}"


    #Acesso as casas:

    def obter(self, casa: str) -> Peca | None:
        return self.pecas.get(casa)

    def definir(self, casa: str, peca: Peca | None) -> None:
        if peca is None:
            self.pecas.pop(casa, None)
        else:
            self.pecas[casa] = peca

    def esta_vazia(self, casa: str) -> bool:
        return casa not in self.pecas

    def casas_ocupadas_por(self, cor: Cor) -> list[str]:
        return [casa for casa, peca in self.pecas.items() if peca.cor == cor]

    def encontrar_rei(self, cor: Cor) -> str:
        for casa, peca in self.pecas.items():
            if peca.tipo == TipoPeca.REI and peca.cor == cor:
                return casa
        raise ValueError(f"Rei {'branco' if cor == Cor.BRANCA else 'preto'} não encontrado no tabuleiro.")

    def copiar(self) -> Tabuleiro:
        return deepcopy(self)

    def __repr__(self) -> str:
        return f"Tabuleiro({self.para_fen()})"
