import java.util.ArrayList;
import java.util.List;

/**
 * Algoritmo KMP (Knuth-Morris-Pratt) — implementação pura.
 *
 * Contém APENAS o algoritmo (tabela LPS + busca). A geração de entradas e a
 * medição de tempo ficam em BenchmarkKMP.java.
 *
 * Compilar : javac KMP.java BenchmarkKMP.java
 * Disciplina: Teoria da Computação.
 */
public class KMP {

    /**
     * Constrói a tabela de falhas LPS (Longest Proper Prefix which is also Suffix).
     * LPS[i] = comprimento do maior prefixo próprio de padrao[0..i] que também é sufixo.
     * Complexidade: O(m).
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
            } else if (comprimento != 0) {
                comprimento = lps[comprimento - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
        return lps;
    }

    /**
     * Busca todas as ocorrências de padrao em texto usando o algoritmo KMP.
     * Fase 1 – pré-processamento: LPS em O(m). Fase 2 – busca em O(n).
     * Complexidade total: O(n + m).
     *
     * @return lista com os índices de início de cada ocorrência.
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
                    i++;                            // avança no texto
                }
            }
        }
        return ocorrencias;
    }

    /** Conta ocorrências sem materializar a lista (útil para benchmarks). */
    static int contarOcorrencias(char[] texto, char[] padrao) {
        return kmpBusca(texto, padrao).size();
    }

    public static void main(String[] args) {
        char[] texto = "ABABDABACDABABCABAB".toCharArray();
        char[] padrao = "ABABCABAB".toCharArray();
        System.out.println("Ocorrências: " + kmpBusca(texto, padrao));
    }
}
