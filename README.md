# KMP – Análise de Complexidade de Tempo

Projeto da disciplina **Teoria da Computação**.
Implementação e análise experimental do algoritmo **Knuth-Morris-Pratt (KMP)**
em **Python** e **Java**.

---

## Estrutura do repositório

```
kmp-complexity-analysis/
├── python/
│   ├── kmp.py               # Algoritmo puro (LPS + busca)
│   ├── gerar_entradas.py    # Geração determinística das entradas
│   └── benchmark.py         # Medição de tempo + CSVs (CLI)
├── java/
│   ├── KMP.java             # Algoritmo puro (LPS + busca)
│   └── BenchmarkKMP.java    # Medição de tempo + CSVs
├── data/                    # CSVs (resumo + medições brutas)
├── graficos/                # Imagens geradas
├── relatorio/               # PDF do relatório
├── slides/                  # Slides da apresentação
├── graficos.py              # Geração dos gráficos
└── README.md
```

O código é **modular**: o algoritmo (`kmp.py` / `KMP.java`) é separado da geração
de entradas e da medição de tempo, facilitando reuso e teste.

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|------------|--------------|
| Python     | 3.10+        |
| Java (JDK) | 17+          |

```bash
pip install numpy pandas matplotlib
```

---

## Como executar

Todos os comandos são executados **a partir da raiz do projeto**.

### 1. Benchmark em Python
```bash
python python/benchmark.py --runs 30
```
Saídas: `data/resultados_python.csv` (resumo) e `data/resultados_python_raw.csv` (bruto).

### 2. Benchmark em Java
```bash
javac java/KMP.java java/BenchmarkKMP.java
java -cp java BenchmarkKMP 30
```
Saídas: `data/resultados_java.csv` (resumo) e `data/resultados_java_raw.csv` (bruto).

### 3. Gerar os gráficos
```bash
python graficos.py
```
Saída em `graficos/`: `kmp_python_casos.png`, `kmp_java_casos.png`,
`kmp_python_vs_java.png`, `kmp_loglog.png`.

---

## Metodologia experimental

| Parâmetro | Valor |
|-----------|-------|
| Tamanhos de entrada (n) | 1.000 / 10.000 / 100.000 |
| Tamanho do padrão (m) | 1% de n |
| Rodadas por cenário | 30 |
| Aquecimento | 5 rodadas (não contabilizadas) |
| Medição de tempo | `time.perf_counter()` (Python) · `System.nanoTime()` (Java) |
| Estatísticas | Média e desvio-padrão amostral |

**Entradas determinísticas e idênticas entre linguagens.** O caso médio é gerado
por um LCG (gerador linear congruente) com a mesma fórmula e as mesmas sementes em
Python e Java, de modo que as duas implementações rodem sobre **exatamente as mesmas
entradas** — tornando a comparação entre lingua