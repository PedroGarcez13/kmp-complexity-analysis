"""
Geração determinística das entradas dos benchmarks do KMP.

Mantém o desenho de casos clássico do projeto (melhor / médio / pior), com
|padrão| = 1% de n. O caso médio usa um gerador linear congruente (LCG) com
a MESMA fórmula e as mesmas sementes da versão Java (BenchmarkKMP.java),
garantindo que Python e Java rodem sobre entradas IDÊNTICAS — o que torna a
comparação entre linguagens justa e reprodutível.
"""

from __future__ import annotations

from dataclasses import dataclass

# Tamanhos de entrada: pequeno / médio / grande.
TAMANHOS = {
    "pequena": 1_000,
    "media": 10_000,
    "grande": 100_000,
}

CASOS = ("melhor", "medio", "pior")

# Caso médio: alfabeto de 10 letras (coerente com o relatório).
ALFABETO_MEDIO = "abcdefghij"

# Constantes do LCG (mesmas em Python e Java).
_LCG_A = 1103515245
_LCG_C = 12345
_LCG_MASK = 0x7FFFFFFF


@dataclass(frozen=True)
class EntradaKMP:
    caso: str
    n: int
    m: int
    texto: str
    padrao: str


def tamanho_padrao(n: int) -> int:
    """|padrão| = 1% de n, com mínimo de 1."""
    return max(1, n // 100)


def _lcg_caracteres(quantidade: int, semente: int, alfabeto: str) -> str:
    """Gera `quantidade` caracteres por LCG (determinístico e portável)."""
    estado = semente & _LCG_MASK
    saida: list[str] = []
    for _ in range(quantidade):
        estado = (_LCG_A * estado + _LCG_C) & _LCG_MASK
        saida.append(alfabeto[estado % len(alfabeto)])
    return "".join(saida)


def gerar_entrada(caso: str, n: int) -> EntradaKMP:
    """
    Constrói (texto, padrão) para um cenário.

    melhor: texto = 'a'*n, padrão = 'b' + 'a'*(m-1)
            → 1º caractere do padrão nunca aparece; LPS não é consultada (~n comparações).
    pior  : texto = 'a'*n, padrão = 'a'*(m-1) + 'b'
            → LPS = [0,1,...,m-2,0]; retrocesso máximo (~2n comparações).
    medio : texto e padrão pseudoaleatórios determinísticos (LCG, alfabeto de 10 letras).
    """
    m = tamanho_padrao(n)

    if caso == "melhor":
        texto = "a" * n
        padrao = "b" + "a" * (m - 1)
    elif caso == "pior":
        texto = "a" * n
        padrao = "a" * (m - 1) + "b"
    elif caso == "medio":
        texto = _lcg_caracteres(n, n * 31 + 7, ALFABETO_MEDIO)
        padrao = _lcg_caracteres(m, n * 17 + 13, ALFABETO_MEDIO)
    else:
        raise ValueError(f"Caso desconhecido: {caso!r}")

    return EntradaKMP(caso=caso, n=n, m=m, texto=texto, padrao=padrao)


if __name__ == "__main__":
    # Imprime uma amostra para conferência de paridade com o Java.
    for caso in CASOS:
        e = gerar_entrada(caso, 1_000)
        print(f"{caso:7s} | n={e.n} | m={e.m} | padrão[:12]={e.padrao[:12]!r} | texto[:12]={e.texto[:12]!r}")
