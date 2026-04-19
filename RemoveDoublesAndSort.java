import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;
import java.io.IOException;

public class RemoveDoublesAndSort {
    public static void main(String[] args) {
        // 1. Define Paths - Verify these exist on your L: drive
        String path="L:\\Coding\\VSCode Projects\\furigana-tool\\Data files";
        String verbsPath = path+"\\Verbs_out.csv";
        String wordsPath = path+"\\Other_words.txt";
        String outputPath = path+"\\JP_Total_List_S.CSV";

        List<String> allLines = new ArrayList<>();

        try {
            // 2. Read Verbs
            Path vPath = Paths.get(verbsPath);
            if (Files.exists(vPath)) {
                List<String> vLines = Files.readAllLines(vPath);
                allLines.addAll(vLines);
                System.out.println("SUCCESS: Read " + vLines.size() + " lines from Verbs.");
            } else {
                System.err.println("ERROR: Verbs file not found at " + verbsPath);
            }

            // 3. Read Other Words
            Path wPath = Paths.get(wordsPath);
            if (Files.exists(wPath)) {
                List<String> wLines = Files.readAllLines(wPath);
                allLines.addAll(wLines);
                System.out.println("SUCCESS: Read " + wLines.size() + " lines from Other Words.");
            } else {
                System.err.println("ERROR: Other Words file not found at " + wordsPath);
            }

            System.out.println("Total combined lines before filtering: " + allLines.size());

            // 4. Remove doubles based on Column 0 (Word)
            // We use a Map to keep the FIRST instance of a word we find
            Map<String, String> uniqueMap = new LinkedHashMap<>();
            for (String line : allLines) {
                if (line == null || line.trim().isEmpty()) continue;
                
                String word = line.split(",")[0].trim();
                // putIfAbsent ensures if a verb and word are the same, we keep the verb
                uniqueMap.putIfAbsent(word, line);
            }

            // 5. Sort by Length of Column 0 (Longest First)
            List<String> sortedList = uniqueMap.values().stream()
                .sorted(Comparator.comparingInt((String line) -> {
                    String[] parts = line.split(",", 2);
                    return parts[0].length();
                }).reversed()
                .thenComparing(Comparator.naturalOrder()))
                .collect(Collectors.toList());

            // 6. Export
            Files.write(Paths.get(outputPath), sortedList);

            System.out.println("--- Results ---");
            System.out.println("Final file contains " + sortedList.size() + " unique entries.");
            System.out.println("Saved to: " + outputPath);

        } catch (IOException e) {
            System.err.println("Critical I/O Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}