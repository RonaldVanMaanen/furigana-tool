import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class FilterSuruVerbs {

    public static void main(String[] args) {
        // Filenames - update extensions if necessary (e.g., .csv)
        String verbTypeFile = "L:\\FuriganaTool\\Verb_Type_Definition.csv"; 
        String otherWordsFile = "L:\\FuriganaTool\\Other_words_3.txt";
        String outputFile = "L:\\FuriganaTool\\Other_words_4.txt";

        try {
            // 1. Identify Suru Verbs from the CSV
            Set<String> suruVerbs = new HashSet<>();
            List<String> definitionLines = Files.readAllLines(Paths.get(verbTypeFile), StandardCharsets.UTF_8);

            for (String line : definitionLines) {
                if (line.trim().isEmpty()) continue;

                // Split by comma for CSV
                String[] columns = line.split(",");
                
                if (columns.length >= 3) {
                    String verb = columns[0].trim();
                    String type = columns[2].trim(); // 3rd Column
                    
                    if ("suru".equalsIgnoreCase(type)) {
                        suruVerbs.add(verb);
                    }
                }
            }

            // DEBUG: Check if we actually loaded any suru verbs
            System.out.println("Suru verbs found in definitions: " + suruVerbs.size());

            // 2. Read and filter Other_words_3.txt (assuming it's also CSV)
            List<String> otherWordsLines = Files.readAllLines(Paths.get(otherWordsFile), StandardCharsets.UTF_8);
            
            List<String> filteredList = otherWordsLines.stream()
                .filter(line -> !line.trim().isEmpty())
                .filter(line -> {
                    String[] parts = line.split(",");
                    if (parts.length > 0) {
                        String kanjiInFile = parts[0].trim();
                        // If this word is in our suru set, return false (remove it)
                        return !suruVerbs.contains(kanjiInFile);
                    }
                    return true;
                })
                .collect(Collectors.toList());

            // 3. Save the result
            Files.write(Paths.get(outputFile), filteredList);

            System.out.println("--- Results ---");
            System.out.println("Original word count: " + otherWordsLines.size());
            System.out.println("Remaining word count: " + filteredList.size());
            System.out.println("Total removed: " + (otherWordsLines.size() - filteredList.size()));

        } catch (IOException e) {
            System.err.println("Error reading files. Check if filenames and extensions are correct: " + e.getMessage());
        }
    }
}