"""
Benchmark do KMP em Python.

- Mede APENAS a chamada ao algoritmo com time.perf_counter().
- 30 rodadas cronometradas + 5 de aquecimento (não contabilizadas) por cenário.
- Salva medições brutas (uma linha por rodada) e um resumo (média + desvio-padrão
  amostral) por linguagem/caso/n.

Uso:
    python benchmark.py                 # 30 rodadas (padrão)
    python benchmark.py --runs 30
    python benchmark.py --aquecimento 5
"""

from __future__ import annotations

import argparse
import csv
import statistics
import time
from pathlib import Path

from gerar_entradas import CASOS, TAMANHOS, gerar_entrada
from kmp import contar_ocorrencias

RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
CSV_RESUMO = DATA / "resultados_python.csv"          # consumido por graficos.py
CSV_BRUTO = DATA / "resultados_python_raw.csv"       # uma linha por rodada

CABECALHO_RESUMO = ["linguagem", "caso", "n", "media_us", "desvio_us"]
CABECALHO_BRUTO = ["linguagem", "caso", "n", "m", "rodada", "ocorrencias", "tempo_us"]


def executar(runs: int, aquecimento: int) -> tuple[list[dict], list[dict]]:
    print("=" * 68)
    print("  KMP – Experimentos em Python")
    print(f"  Tamanhos: {list(TAMANHOS.values())}  |  Rodadas: {runs}  |  Aquecimento: {aquecimento}")
    print("=" * 68)

    resumo: list[dict] = []
    bruto: list[dict] = []

    for caso in CASOS:
        for n in TAMANHOS.values():
            entrada = gerar_entrada(caso, n)

            # Aquecimento: garante que o interpretador já compilou o bytecode.
            for _ in range(aquecimento):
                contar_ocorrencias(entrada.texto, entrada.padrao)

            tempos_us: list[float] = []
            for rodada in range(1, runs + 1):
                inicio = time.perf_counter()
                ocorrencias = contar_ocorrencias(entrada.texto, entrada.padrao)
                fim = time.perf_counter()
                t_us = (fim - inicio) * 1_000_000
                tempos_us.append(t_us)
                bruto.append({
                    "linguagem": "Python", "caso": caso, "n": n, "m": entrada.m,
                    "rodada": rodada, "ocorrencias": ocorrencias, "tempo_us": f"{t_us:.4f}",
                })

            media = statistics.mean(tempos_us)
            desvio = statistics.stdev(tempos_us) if len(tempos_us) > 1 else 0.0
            resumo.append({
                "linguagem": "Python", "caso": caso, "n": n,
                "media_us": round(media, 4), "desvio_us": round(desvio, 4),
            })
            print(f"  {caso:7s} | n={n:7d} | m={entrada.m:5d} | "
                  f"média={media:9.2f} µs | dp={desvio:7.2f} µs")

    print()
    return resumo, bruto


def salvar(resumo: list[dict], bruto: list[dict]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with CSV_RESUMO.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO_RESUMO)
        w.writeheader()
        w.writerows(resumo)
    with CSV_BRUTO.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO_BRUTO)
        w.writeheader()
        w.writerows(bruto)
    print(f"✓ Resumo salvo em {CSV_RESUMO}")
    print(f"✓ Medições brutas salvas em {CSV_BRUTO}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark do KMP em Python.")
    parser.add_argument("--runs", type=int, default=30, help="Rodadas cronometradas por cenário.")
    parser.add_argument("--aquecimento", type=int, default=5, help="Rodadas de aquecimento (descartadas).")
    args = parser.parse_args()
    if args.runs <= 0:
        raise ValueError("--runs deve ser maior que zero")

    resumo, bruto = executar(args.runs, args.aquecimento)
    salvar(resumo, bruto)


if __name__ == "__main__":
    main()
