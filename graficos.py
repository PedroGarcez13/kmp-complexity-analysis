"""
Gerador de gráficos – Análise KMP
Execução : python graficos.py   (a partir da RAIZ do projeto)
Requer   : data/resultados_python.csv  e  data/resultados_java.csv
Saída    : graficos/kmp_python_casos.png
           graficos/kmp_java_casos.png
           graficos/kmp_python_vs_java.png
           graficos/kmp_loglog.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('graficos', exist_ok=True)

# ── Verificar se os CSVs existem ─────────────────────────────────────────────
for arq in ['data/resultados_python.csv', 'data/resultados_java.csv']:
    if not os.path.exists(arq):
        print(f"[ERRO] Arquivo não encontrado: {arq}")
        print("       Execute kmp.py e KMP.java antes de rodar este script.")
        sys.exit(1)

# ── Carregar dados ────────────────────────────────────────────────────────────
df_py   = pd.read_csv('data/resultados_python.csv')
df_java = pd.read_csv('data/resultados_java.csv')
df = pd.concat([df_py, df_java], ignore_index=True)

# ── Constantes visuais ────────────────────────────────────────────────────────
TAMANHOS    = [1_000, 10_000, 100_000]
CASOS       = ['melhor', 'medio', 'pior']
LABELS      = {'melhor': 'Melhor Caso', 'medio': 'Caso Médio', 'pior': 'Pior Caso'}
CORES_LANG  = {'Python': '#3572A5',  'Java': '#b07219'}
CORES_CASO  = {'melhor': '#2ca02c',  'medio': '#1f77b4',  'pior': '#d62728'}
MARCADORES  = {'melhor': 'o',        'medio': 's',         'pior': '^'}
LINHAS_CASO = {'melhor': '-',        'medio': '--',         'pior': ':'}


# ── Curva teórica O(n + m) escalada ──────────────────────────────────────────
def curva_teorica(lang_ref: str, caso_ref: str = 'medio'):
    """
    Retorna (ns, valores) para a curva O(n+m) com m = 0.01n,
    escalada por regressão linear para se ajustar aos dados reais.
    """
    ns  = np.array(TAMANHOS, dtype=float)
    teo = ns * 1.01   # O(n + m) com m = 0.01n  →  1.01n
    ref = df[(df['linguagem'] == lang_ref) & (df['caso'] == caso_ref)] \
            .sort_values('n')['media_us'].values
    # Mínimos quadrados: minimiza ||teo * c - ref||²
    scale = np.dot(ref, teo) / np.dot(teo, teo)
    return ns, teo * scale


# =============================================================================
# GRÁFICO 1 – Python: os 3 casos + curva teórica
# =============================================================================
fig, ax = plt.subplots(figsize=(9, 5))
sub = df[df['linguagem'] == 'Python']

for caso in CASOS:
    d = sub[sub['caso'] == caso].sort_values('n')
    ax.errorbar(d['n'], d['media_us'], yerr=d['desvio_us'],
                label=LABELS[caso], color=CORES_CASO[caso],
                marker=MARCADORES[caso], linewidth=2, capsize=5)

ns_t, teo = curva_teorica('Python')
ax.plot(ns_t, teo, 'k--', linewidth=2, label='Curva Teórica O(n+m)')

ax.set_xscale('log')
ax.set_xlabel('Tamanho da entrada (n)', fontsize=12)
ax.set_ylabel('Tempo de execução (µs)', fontsize=12)
ax.set_title('KMP – Python: Comparação de Casos', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('graficos/kmp_python_casos.png', dpi=150)
plt.close()
print('✓ graficos/kmp_python_casos.png')


# =============================================================================
# GRÁFICO 2 – Java: os 3 casos + curva teórica
# =============================================================================
fig, ax = plt.subplots(figsize=(9, 5))
sub = df[df['linguagem'] == 'Java']

for caso in CASOS:
    d = sub[sub['caso'] == caso].sort_values('n')
    ax.errorbar(d['n'], d['media_us'], yerr=d['desvio_us'],
                label=LABELS[caso], color=CORES_CASO[caso],
                marker=MARCADORES[caso], linewidth=2, capsize=5)

ns_t, teo = curva_teorica('Java')
ax.plot(ns_t, teo, 'k--', linewidth=2, label='Curva Teórica O(n+m)')

ax.set_xscale('log')
ax.set_xlabel('Tamanho da entrada (n)', fontsize=12)
ax.set_ylabel('Tempo de execução (µs)', fontsize=12)
ax.set_title('KMP – Java: Comparação de Casos', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('graficos/kmp_java_casos.png', dpi=150)
plt.close()
print('✓ graficos/kmp_java_casos.png')


# =============================================================================
# GRÁFICO 3 – Python vs Java (3 painéis, um por caso)
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

for ax, caso in zip(axes, CASOS):
    for lang in ['Python', 'Java']:
        d = df[(df['linguagem'] == lang) & (df['caso'] == caso)].sort_values('n')
        ax.errorbar(d['n'], d['media_us'], yerr=d['desvio_us'],
                    label=lang, color=CORES_LANG[lang],
                    marker='o', linewidth=2, capsize=5)
    ax.set_xscale('log')
    ax.set_title(LABELS[caso], fontsize=12, fontweight='bold')
    ax.set_xlabel('n', fontsize=11)
    ax.set_ylabel('Tempo (µs)', fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

fig.suptitle('KMP – Python vs. Java', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('graficos/kmp_python_vs_java.png', dpi=150)
plt.close()
print('✓ graficos/kmp_python_vs_java.png')


# =============================================================================
# GRÁFICO 4 – Visão geral em escala log-log (todas as séries)
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

for lang in ['Python', 'Java']:
    for caso in CASOS:
        d = df[(df['linguagem'] == lang) & (df['caso'] == caso)].sort_values('n')
        ax.plot(d['n'], d['media_us'],
                color=CORES_LANG[lang], linestyle=LINHAS_CASO[caso],
                marker=MARCADORES[caso], linewidth=2,
                label=f'{lang} – {LABELS[caso]}')

# Curva teórica (referência Python)
ns_t, teo = curva_teorica('Python')
ax.plot(ns_t, teo, 'k--', linewidth=2.5, label='Curva Teórica O(n+m)')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Tamanho da entrada (n)', fontsize=12)
ax.set_ylabel('Tempo de execução (µs) – escala log', fontsize=12)
ax.set_title('KMP – Visão Geral (escala log-log)', fontsize=13, fontweight='bold')
ax.legend(fontsize=9, ncol=2, loc='upper left')
ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig('graficos/kmp_loglog.png', dpi=150)
plt.close()
print('✓ graficos/kmp_loglog.png')

print('\n✓ Todos os gráficos gerados com sucesso em graficos/')
