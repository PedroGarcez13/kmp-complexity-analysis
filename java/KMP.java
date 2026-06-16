import java.io.*;
import java.util.*;

/**
 * Implementação e análise experimental do algoritmo KMP (Knuth-Morris-Pratt).
 * Linguagem : Java
 * Disciplina: Teoria da Computação
 *
 * Compilar : javac KMP.java
 * Executar : java KMP
 */
public class KMP {

    // =========================================================================
    // ALGORITMO KMP
    // =========================================================================

    /**
     * Constrói a tabela de falhas LPS (Longest Proper Prefix which is also Suffix).
     *
     * LPS[i] = comprimento do maior prefixo próprio de padrao[0..i]
     * que também é sufixo. Permite deslocar o padrão sem retroceder
     * o ponteiro do texto.
     *
     * Complexidade: O(m)
     */
    static int[] construirLPS(char[] padrao) {
        int m = padrao.length;
        int[] lps = new int[m];
        int comprimento = 0;
        int i = 1;

        while (i < m) {
            if (padrao[i] == padrao[comprimento]) {
                comprimento++;
                lps[i] = comprimento;
                i++;
            } else {
                if (comprimento != 0) {
                    comprimento = lps[comprimento - 1];
                } else {
                    lps[i] = 0;
                    i++;
                }
            }
        }
        return lps;
    }

    /**
     * Busca todas as ocorrências de padrao em texto usando o algoritmo KMP.
     *
     * Fase 1 – pré-processamento : constrói a tabela LPS em O(m).
     * Fase 2 – busca             : percorre o texto em O(n), consultando
     *                              a LPS ao encontrar falhas.
     *
     * Complexidade total: O(n + m)
     *
     * @return Lista com os índices de início de cada ocorrência.
     */
    static List<Integer> kmpBusca(char[] texto, char[] padrao) {
        int n = texto.length;
        int m = padrao.length;
        List<Integer> ocorrencias = new ArrayList<>();
        if (m == 0) return ocorrencias;

        int[] lps = construirLPS(padrao);
        int i = 0, j = 0;   // i = ponteiro no texto, j = ponteiro no padrão

        while (i < n) {
            if (texto[i] == padrao[j]) {
                i++;
                j++;
            }
            if (j == m) {                           // ocorrência encontrada
                ocorrencias.add(i - j);
                j = lps[j - 1];
            } else if (i < n && texto[i] != padrao[j]) {
                if (j != 0) {
                    j = lps[j - 1];                 // desloca padrão via LPS
                } else {
                    i++;                            // avança texto
                }
            }
        }
        return ocorrencias;
    }

    // =========================================================================
    // GERADORES DE CASOS
    // =========================================================================

    /**
     * Melhor caso: primeiro caractere do padrão nunca aparece no texto.
     * → Sem retrocesso na LPS; ≈ n comparações na busca.
     * Estrutura: texto = 'a'*n, padrao = 'b' + 'a'*(m-1)
     */
    static char[][] melhorCaso(int n, int m) {
        char[] texto  = new char[n];
        char[] padrao = new char[m];
        Arrays.fill(texto, 'a');
        padrao[0] = 'b';
        Arrays.fill(padrao, 1, m, 'a');
        return new char[][]{texto, padrao};
    }

    /**
     * Pior caso: máximo retrocesso via tabela LPS.
     * → LPS = [0,1,2,...,m-2,0]; ≈ 2n comparações na busca.
     * Estrutura: texto = 'a'*n, padrao = 'a'*(m-1) + 'b'
     */
    static char[][] piorCaso(int n, int m) {
        char[] texto  = new char[n];
        char[] padrao = new char[m];
        Arrays.fill(texto,  'a');
        Arrays.fill(padrao, 'a');
        padrao[m - 1] = 'b';
        return new char[][]{texto, padrao};
    }

    /**
     * Caso médio: texto e padrão aleatórios sobre alfabeto de 10 letras.
     * Representa distribuição uniforme típica de entrada real.
     */
    static char[][] casoMedio(int n, int m, Random rng) {
        char[] texto  = new char[n];
        char[] padrao = new char[m];
        for (int i = 0; i < n; i++) texto[i]  = (char) ('a' + rng.nextInt(10));
        for (int i = 0; i < m; i++) padrao[i] = (char) ('a' + rng.nextInt(10));
        return new char[][]{texto, padrao};
    }

    // =========================================================================
    // AUXILIAR – despacho de casos
    // =========================================================================
    static char[][] gerarEntrada(String caso, int n, int m, Random rng) {
        return switch (caso) {
            case "melhor" -> melhorCaso(n, m);
            case "pior"   -> piorCaso(n, m);
            default       -> casoMedio(n, m, rng);
        };
    }

    // =========================================================================
    // ESTATÍSTICAS
    // =========================================================================
    static double media(double[] v) {
        double soma = 0;
        for (double x : v) soma += x;
        return soma / v.length;
    }

    static double desvio(double[] v, double media) {
        double soma = 0;
        for (double x : v) soma += (x - media) * (x - media);
        return Math.sqrt(soma / (v.length - 1));   // desvio-padrão amostral
    }

    // =========================================================================
    // EXPERIMENTOS
    // =========================================================================
    public static void main(String[] args) throws IOException {

        int[]  tamanhos    = {1_000, 10_000, 100_000};
        double razaoM      = 0.01;
        int    rodadas     = 30;
        int    aquecimento = 5;
        String[] casos     = {"melhor", "medio", "pior"};
        Random rng         = new Random(42);

        System.out.println("=".repeat(68));
        System.out.println("  KMP – Experimentos em Java");
        System.out.printf ("  Tamanhos: %s  |  Rodadas: %d  |  Aquecimento: %d%n",
                Arrays.toString(tamanhos), rodadas, aquecimento);
        System.out.println("=".repeat(68));

        // Cabeçalho do CSV
        List<String> linhasCSV = new ArrayList<>();
        linhasCSV.add("linguagem,caso,n,media_us,desvio_us");

        for (String caso : casos) {
            for (int n : tamanhos) {
                int m = Math.max(1, (int) (n * razaoM));

                // Aquecimento: permite que a JVM aplique otimizações JIT
                for (int r = 0; r < aquecimento; r++) {
                    char[][] entrada = gerarEntrada(caso, n, m, rng);
                    kmpBusca(entrada[0], entrada[1]);
                }

                // Coleta de tempos (30 rodadas)
                double[] tempos = new double[rodadas];
                for (int r = 0; r < rodadas; r++) {
                    char[][] entrada = gerarEntrada(caso, n, m, rng);
                    long inicio = System.nanoTime();
                    kmpBusca(entrada[0], entrada[1]);
                    long fim    = System.nanoTime();
                    tempos[r] = (fim - inicio) / 1_000.0;   // ns → µs
                }

                double med = media(tempos);
                double dp  = desvio(tempos, med);

                System.out.printf("  %-7s | n=%7d | m=%5d | média=%9.2f µs | dp=%7.2f µs%n",
                        caso, n, m, med, dp);

                linhasCSV.add(String.format(Locale.US,
                        "Java,%s,%d,%.4f,%.4f", caso, n, med, dp));
            }
        }

        System.out.println();

        // Salvar CSV
        new File("../data").mkdirs();
        try (PrintWriter pw = new PrintWriter("../data/resultados_java.csv", "UTF-8")) {
            for (String linha : linhasCSV) pw.println(linha);
        }
        System.out.println("✓ CSV salvo em ../data/resultados_java.csv");
    }
}
