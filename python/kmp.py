"""
Implementação e análise experimental do algoritmo KMP (Knuth-Morris-Pratt)
Linguagem : Python
Disciplina: Teoria da Computação
"""

import time
import random
import csv
import os
import numpy as np


# =============================================================================
# ALGORITMO KMP
# =============================================================================

def construir_lps(padrao: str) -> list[int]:
    """
    Constrói a tabela de falhas LPS (Longest Proper Prefix which is also Suffix).

    A tabela LPS[i] armazena o comprimento do maior prefixo próprio de
    padrao[0..i] que também é sufixo. Ela permite que o algoritmo evite
    comparações desnecessárias ao reutilizar informações de correspondências
    anteriores.

    Complexidade: O(m), onde m = len(padrao)

    Exemplo:
        padrao = "ABABC"
        lps    =  [0, 0, 1, 2, 0]
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
        else:
            if comprimento != 0:
                comprimento = lps[comprimento - 1]
            else:
                lps[i] = 0
                i += 1

    return lps


def kmp_busca(texto: str, padrao: str) -> list[int]:
    """
    Busca todas as ocorrências de `padrao` em `texto` usando o algoritmo KMP.

    Fase 1 – pré-processamento: constrói a tabela LPS em O(m).
    Fase 2 – busca: percorre o texto em O(n), usando a tabela LPS para
              deslocar o padrão sem retroceder o ponteiro do texto.

    Complexidade total: O(n + m)

    Retorna lista com os índices de início de cada ocorrência.
    """
    n, m = len(texto), len(padrao)
    if m == 0:
        return []

    lps = construir_lps(padrao)
    ocorrencias = []
    i = 0   # ponteiro no texto
    j = 0   # ponteiro no padrão

    while i < n:
        if texto[i] == padrao[j]:
            i += 1
            j += 1

        if j == m:                          # ocorrência encontrada
            ocorrencias.append(i - j)
            j = lps[j - 1]
        elif i < n and texto[i] != padrao[j]:
            if j != 0:
                j = lps[j - 1]             # desloca padrão via LPS
            else:
                i += 1                      # avança texto

    return ocorrencias


# =============================================================================
# GERADORES DE CASOS
# =============================================================================

def gerar_melhor_caso(n: int, m: int) -> tuple[str, str]:
    """
    Melhor caso: primeiro caractere do padrão nunca aparece no texto.

    Comportamento: cada posição do texto gera apenas 1 comparação e j=0
    nunca avança, logo a tabela LPS nunca é consultada na fase de busca.

    Número de comparações ≈ n  →  O(n + m) com constante mínima.

    Estrutura: texto = 'a'*n,  padrao = 'b' + 'a'*(m-1)
    """
    texto  = 'a' * n
    padrao = 'b' + 'a' * (m - 1)
    return texto, padrao


def gerar_pior_caso(n: int, m: int) -> tuple[str, str]:
    """
    Pior caso: máximo de retrocessos via tabela LPS na fase de busca.

    Comportamento: o padrão 'aa...ab' possui LPS = [0,1,2,...,m-2,0].
    Com o texto cheio de 'a', o algoritmo combina m-1 caracteres, falha
    no último, retrocede para j = m-2 e repete — gerando ≈ 2n comparações.

    Número de comparações ≈ 2n  →  O(n + m) com constante máxima.

    Estrutura: texto = 'a'*n,  padrao = 'a'*(m-1) + 'b'
    """
    texto  = 'a' * n
    padrao = 'a' * (m - 1) + 'b'
    return texto, padrao


def gerar_caso_medio(n: int, m: int) -> tuple[str, str]:
    """
    Caso médio: texto e padrão aleatórios sobre alfabeto de 10 letras.
    Representa distribuição uniforme típica de entrada real.
    """
    alfabeto = 'abcdefghij'
    texto  = ''.join(random.choices(alfabeto, k=n))
    padrao = ''.join(random.choices(alfabeto, k=m))
    return texto, padrao


# =============================================================================
# EXPERIMENTOS
# =============================================================================

TAMANHOS    = [1_000, 10_000, 100_000]   # pequeno, médio, grande
RAZAO_M     = 0.01                        # |padrão| = 1% de n
RODADAS     = 30
AQUECIMENTO = 5                           # rodadas não contabilizadas (warmup)

CASOS = {
    'melhor': gerar_melhor_caso,
    'medio' : gerar_caso_medio,
    'pior'  : gerar_pior_caso,
}


def executar_experimentos() -> list[dict]:
    """Roda todos os cenários e retorna a lista de resultados."""
    print("=" * 68)
    print("  KMP – Experimentos em Python")
    print(f"  Tamanhos: {TAMANHOS}  |  Rodadas: {RODADAS}  |  Aquecimento: {AQUECIMENTO}")
    print("=" * 68)

    resultados = []

    for nome_caso, gerador in CASOS.items():
        for n in TAMANHOS:
            m = max(1, int(n * RAZAO_M))

            # Aquecimento: garante que o interpretador já compilou o bytecode
            for _ in range(AQUECIMENTO):
                t, p = gerador(n, m)
                kmp_busca(t, p)

            # Coleta de tempos (30 rodadas)
            tempos = []
            for _ in range(RODADAS):
                texto, padrao = gerador(n, m)
                inicio = time.perf_counter()
                kmp_busca(texto, padrao)
                fim    = time.perf_counter()
                tempos.append((fim - inicio) * 1_000_000)   # segundos → µs

            media  = float(np.mean(tempos))
            desvio = float(np.std(tempos, ddof=1))          # desvio-padrão amostral

            resultados.append({
                'linguagem': 'Python',
                'caso'     : nome_caso,
                'n'        : n,
                'media_us' : round(media, 4),
                'desvio_us': round(desvio, 4),
            })

            print(f"  {nome_caso:7s} | n={n:7d} | m={m:5d} | "
                  f"média={media:9.2f} µs | dp={desvio:7.2f} µs")

    print()
    return resultados


def salvar_csv(resultados: list[dict]) -> None:
    """Salva os resultados em ../data/resultados_python.csv."""
    os.makedirs('../data', exist_ok=True)
    caminho_csv = '../data/resultados_python.csv'

    with open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
        ca