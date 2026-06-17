"""
Algoritmo KMP (Knuth-Morris-Pratt) — implementação pura.

Este módulo contém APENAS o algoritmo (tabela LPS + busca). A geração de
entradas fica em `gerar_entradas.py` e a medição de tempo em `benchmark.py`.
Disciplina: Teoria da Computação.
"""

from __future__ import annotations


def construir_lps(padrao: str) -> list[int]:
    """
    Constrói a tabela de falhas LPS (Longest Proper Prefix which is also Suffix).

    LPS[i] = comprimento do maior prefixo próprio de padrao[0..i] que também é
    sufixo. Permite reaproveitar correspondências anteriores sem retroceder o
    ponteiro do texto.

    Complexidade: O(m), onde m = len(padrao).

    Exemplo:
        construir_lps("ABABCABAB") == [0, 0, 1, 2, 0, 1, 2, 3, 4]
    """
    m = len(padrao)
    lps = [0] * m
    comprimento = 0   # comprimento do prefixo-sufixo atual
    i = 1

    while i < m:
        if padrao[i] == padrao[comprimento]:
            comprimento += 1
            lps[i] = comprimento
            i += 1
        elif comprimento != 0:
            comprimento = lps[comprimento - 1]
        else:
            lps[i] = 0
            i += 1

    return lps


def kmp_busca(texto: str, padrao: str) -> list[int]:
    """
    Busca todas as ocorrências de `padrao` em `texto` usando o algoritmo KMP.

    Fase 1 – pré-processamento: constrói a tabela LPS em O(m).
    Fase 2 – busca: percorre o texto em O(n) usando a LPS para deslocar o
              padrão sem retroceder o ponteiro do texto.

    Complexidade total: O(n + m).

    Retorna a lista com os índices de início de cada ocorrência.
    """
    n, m = len(texto), len(padrao)
    if m == 0:
        return []

    lps = construir_lps(padrao)
    ocorrencias: list[int] = []
    i = 0   # ponteiro no texto
    j = 0   # ponteiro no padrão

    while i < n:
        if texto[i] == padrao[j]:
            i += 1
            j += 1

        if j == m:                           # ocorrência encontrada
            ocorrencias.append(i - j)
            j = lps[j - 1]
        elif i < n and texto[i] != padrao[j]:
            if j != 0:
                j = lps[j - 1]              # desloca padrão via LPS
            else:
                i += 1                       # avança no texto

    return ocorrencias


def contar_ocorrencias(texto: str, padrao: str) -> int:
    """Conta ocorrências sem materializar a lista (útil para benchmarks)."""
    return len(kmp_busca(texto, padrao))


if __name__ == "__main__":
    exemplo_texto = "ABABDABACDABABCABAB"
    exemplo_padrao = "ABABCABAB"
    print("Texto :", exemplo_texto)
    print("Padrão:", exemplo_padrao)
    print("LPS   :", construir_lps(exemplo_padrao))
    print("Ocorrências:", kmp_busca(exemplo_texto, exemplo_padrao))
