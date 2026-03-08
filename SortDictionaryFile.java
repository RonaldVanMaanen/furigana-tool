import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

public class SortDictionaryFile {

    public static void main(String[] args) {
        String inputFilePath = "L:\\FuriganaTool\\dictionary.csv";
        String outputFilePath = "L:\\FuriganaTool\\sorted_by_length.csv";
        String delimiter = "\t";

        try {
            List<String> lines = Files.readAllLines(Paths.get(inputFilePath), StandardCharsets.UTF_8);

            // Sort lines by the length of the first segment in ascending order
            lines.sort((line1, line2) -> {
                String word1 = getFirstSegment(line1, delimiter);
                String word2 = getFirstSegment(line2, delimiter);

                // Compare lengths: word1.length() - word2.length() for ascending order
                int lengthComparison = Integer.compare(word1.length(), word2.length());

                // If lengths are equal, sort alphabetically
                if (lengthComparison == 0) {
                    return word1.compareTo(word2);
                }
                return lengthComparison;
            });

            Files.write(Paths.get(outputFilePath), lines, StandardCharsets.UTF_8);
            System.out.println("Sorted shortest to longest. Output: " + outputFilePath);

        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
    }

    private static String getFirstSegment(String line, String delimiter) {
        int index = line.indexOf(delimiter);
        return (index == -1) ? line : line.substring(0, index);
    }
}