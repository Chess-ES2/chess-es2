from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class TipoPeca(Enum):
    PEAO   = "p"
    CAVALO = "n"
    BISPO  = "b"
    TORRE  = "r"
    DAMA   = "q"
    REI    = "k"


class Cor(Enum):
    BRANCA = "w"
    PRETA  = "b"

    def oposta(self) -> Cor:
        #Retorna a cor adversária.
        return Cor.PRETA if self == Cor.BRANCA else Cor.BRANCA
@dataclass(frozen=True)
class Peca:
    tipo: TipoPeca
    cor:  Cor

    @staticmethod
    def de_char_fen(char: str) -> Peca:
        """Cria uma Peca a partir de um caractere FEN.
        Letras maiúsculas representam peças brancas; minúsculas, pretas."""

        cor  = Cor.BRANCA if char.isupper() else Cor.PRETA
        try:
            tipo = TipoPeca(char.lower())
        except ValueError:
            raise ValueError(f"Caractere FEN inválido para peça: '{char}'")
        return Peca(tipo=tipo, cor=cor)

    def para_char_fen(self) -> str:
        #Serializa a peça de volta para um caractere FEN.

        char = self.tipo.value
        return char.upper() if self.cor == Cor.BRANCA else char.lower()

