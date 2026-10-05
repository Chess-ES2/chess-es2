from __future__ import annotations

from motor.peca import TipoPeca

# Valores em centipeões (100 = um peão). Inteiros evitam erros de arredondamento.
VALOR_PECA: dict[TipoPeca, int] = {
    TipoPeca.PEAO:   100,
    TipoPeca.CAVALO: 320,
    TipoPeca.BISPO:  330,
    TipoPeca.TORRE:  500,
    TipoPeca.DAMA:   900,
    TipoPeca.REI:    0,   # o rei nunca é capturado, então não entra na contagem de material
}
