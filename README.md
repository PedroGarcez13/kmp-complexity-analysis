# KMP – Análise de Complexidade de Tempo

Projeto da disciplina **Teoria da Computação**.  
Implementação e análise experimental do algoritmo **Knuth-Morris-Pratt (KMP)**
em **Python** e **Java**.

---

## Estrutura do repositório

```
kmp-complexity-analysis/
├── python/
│   └── kmp.py               # Implementação + experimentos Python
├── java/
│   └── KMP.java             # Implementação + experimentos Java
├── data/                    # CSVs gerados automaticamente
├── graficos/                # Imagens geradas automaticamente
├── relatorio/               # PDF do relatório
├── slides/                  # Slides da apresentação
├── graficos.py              # Script de geração de gráficos
└── README.md
```

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|------------|--------------|
| Python     | 3.10+        |
| Java (JDK) | 17+          |
| pip        | qualquer     |

Instalar dependências Python (apenas uma vez):
```bash
pip install numpy pandas matplotlib
```

---

## Como executar

### 1. Rodar experimentos em Python
```bash
cd python
python kmp.py
```
Saída: `../data/resultados_python.csv`

### 2. Rodar experimentos em Java
```bash
cd java
javac KMP.java
java KMP
```
Saída: `../data/resultados_java.csv`

### 3. Gerar os gráficos
*(executar na raiz do projeto, após os dois passos acima)*
```bash
cd ..
python graficos.py
```
Saída em `graficos/`:
- `kmp_python_casos.png`
- `kmp_java_casos.png`
- `kmp_python_vs_java.png`
- `kmp_loglog.png`

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

### Definição dos casos

| Caso | Texto | Padrão | Comportamento |
|------|-------|--------|---------------|
| Melhor | `'a' * n` | `'b' + 'a'*(m-1)` | 1 comparação por posição; LPS nunca consultada |
| Pior | `'a' * n` | `'a'*(m-1) + 'b'` | ≈ 2n comparações; retrocesso máximo na LPS |
| Médio | aleatório | aleatório | distribuição uniforme sobre alfabeto de 10 letras |

---

## Complexidade do KMP

| Fase | Complexidade |
|------|-------------|
| Pré-processamento (LPS) | O(m) |
| Busca | O(n) |
| **Total** | **O(n + m)** |

O KMP é sempre **O(n + m)** nos três casos — melhor, médio e pior.
A diferença experimental reflete apenas a constante multiplicativa.
