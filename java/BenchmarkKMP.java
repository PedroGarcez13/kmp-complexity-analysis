import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

/**
 * Benchmark do KMP em Java (System.nanoTime()).
 *
 * Mantém o desenho de casos do projeto (melhor / médio / pior) com |padrão| = 1% de n.
 * O caso médio usa o MESMO LCG e as mesmas sementes do gerador Python
 * (gerar_entradas.py), de modo que Python e Java rodem sobre entradas idênticas.
 *
 * Compilar : javac KMP.java BenchmarkKMP.java
 * Executar (a partir da RAIZ do projeto): java -cp java BenchmarkKMP 30
 */
public class BenchmarkKMP {

    private static final String[] TAMANHOS_NOME = {"pequena", "media", "grande"};
    private static final int[] TAMANHOS_N = {1_000, 10_000, 100_000};
    private static final String[] CASOS = {"melhor", "medio", "pior"};
    private static final String ALFABETO_MEDIO = "abcdefghij";

    // Constantes do LCG (iguais às do Python).
    private static final long LCG_A = 1103515245L;
    private static final long LCG_C = 12345L;
    private static final long LCG_MASK = 0x7FFFFFFFL;

    private record Entrada(String caso, int n, int m, char[] texto, char[] padrao) {}

    private static int tamanhoPadrao(int n) {
        return Math.max(1, n / 100);
    }

    private static char[] lcgCaracteres(int quantidade, long semente, String alfabeto) {
        long estado = semente & LCG_MASK;
        char[] saida = new char[quantidade];
        for (int i = 0; i < quantidade; i++) {
            estado = (LCG_A * estado + LCG_C) & LCG_MASK;
            saida[i] = alfabeto.charAt((int) (estado % alfabeto.length()));
        }
        return saida;
    }

    private static Entrada gerarEntrada(String caso, int n) {
        int m = tamanhoPadrao(n);
        char[] texto;
        char[] padrao;

        if (caso.equals("melhor")) {
            texto = "a".repeat(n).toCharArray();
            padrao = ("b" + "a".repeat(m - 1)).toCharArray();
        } else if (caso.equals("pior")) {
            texto = "a".repeat(n).toCharArray();
            padrao = ("a".repeat(m - 1) + "b").toCharArray();
        } else { // medio
            texto = lcgCaracteres(n, (long) n * 31 + 7, ALFABETO_MEDIO);
            padrao = lcgCaracteres(m, (long) n * 17 + 13, ALFABETO_MEDIO);
        }
        return new Entrada(caso, n, m, texto, padrao);
    }

    private static double media(double[] v) {
        double soma = 0;
        for (double x : v) soma += x;
        return soma / v.length;
    }

    private static double desvio(double[] v, double media) {
        double soma = 0;
        for (double x : v) soma += (x - media) * (x - media);
        return Math.sqrt(soma / (v.length - 1));   // desvio-padrão amostral
    }

    public static void main(String[] args) throws IOException {
        Locale.setDefault(Locale.US);
        int runs = args.length > 0 ? Integer.parseInt(args[0]) : 30;
        int aquecimento = 5;
        if (runs <= 0) {
            throw new IllegalArgumentException("runs deve ser maior que zero");
        }

        System.out.println("=".repeat(68));
        System.out.println("  KMP – Experimentos em Java");
        System.out.printf("  Tamanhos: %s  |  Rodadas: %d  |  Aquecimento: %d%n",
                java.util.Arrays.toString(TAMANHOS_N), runs, aquecimento);
        System.out.println("=".repeat(68));

        Path data = Path.of("data");
        Files.createDirectories(data);
        Path csvResumo = data.resolve("resultados_java.csv");
        Path csvBruto = data.resolve("resultados_java_raw.csv");

        try (BufferedWriter resumo = Files.newBufferedWriter(csvResumo, StandardCharsets.UTF_8);
             BufferedWriter bruto = Files.newBufferedWriter(csvBruto, StandardCharsets.UTF_8)) {

            resumo.write("linguagem,caso,n,media_us,desvio_us");
            resumo.newLine();
            bruto.write("linguagem,caso,n,m,rodada,ocorrencias,tempo_us");
            bruto.newLine();

            for (String caso : CASOS) {
                for (int n : TAMANHOS_N) {
                    Entrada e = gerarEntrada(caso, n);

                    // Aquecimento: permite que a JVM aplique otimizações JIT.
                    for (int r = 0; r < aquecimento; r++) {
                        KMP.contarOcorrencias(e.texto(), e.padrao());
                    }

                    double[] tempos = new double[runs];
                    for (int r = 0; r < runs; r++) {
                        long inicio = System.nanoTime();
                        int ocorrencias = KMP.contarOcorrencias(e.texto(), e.padrao());
                        long fim = System.nanoTime();
                        double tUs = (fim - inicio) / 1_000.0;
                        tempos[r] = tUs;
                        bruto.write(String.format(Locale.US, "Java,%s,%d,%d,%d,%d,%.4f",
                                caso, n, e.m(), r + 1, ocorrencias, tUs));
                        bruto.newLine();
                    }

                    double med = media(tempos);
                    double dp = desvio(tempos, med);
                    System.out.printf("  %-7s | n=%7d | m=%5d | média=%9.2f µs | dp=%7.2f µs%n",
                            caso, n, e.m(), med, dp);
                    resumo.write(String.format(Locale.US, "Java,%s,%d,%.4f,%.4f", caso, n, med, dp));
                    resumo.newLine();
                }
            }
        }

        System.out.println();
        System.out.println("✓ Resumo salvo em " + csvResumo.toAbsolutePath());
        System.out.println("✓ Medições brutas salvas em " + csvBruto.toAbsolutePath());
    }
}
