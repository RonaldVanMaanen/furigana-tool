import java.io.*;
import java.util.*;

/**
 * [njp]
 * Java program to automatically split dictionary entries:
 * 1. Saves all unique entries to 'single_entries.csv'.
 * 2. Saves all rows with duplicate keys to 'multiple_entries.csv' for manual review.
 * 3. Saves a cleaned version to 'dictionary_undoubled.csv' (keeping the first occurrence).
 */
public class DictionarySplitter {

    public static void main(String[] args) {
        String inputPath = "L:\\FuriganaTool\\dictionary.csv";
        String singlePath = "L:\\FuriganaTool\single_entries.csv";
        String multiplePath = "L:\\FuriganaTool\\multiple_entries.csv";
        String outputPath = "L:\\FuriganaTool\\dictionary_undoubled.csv";

        // Map to hold Word -> List of full lines to preserve grouping
        Map<String, List<String>> dictionaryMap = new LinkedHashMap<>();

        System.out.println("Reading " + inputPath + "...");

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(inputPath), "UTF-8"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                // Split by tab to get the first element
                String word = line.split("\t")[0];
                dictionaryMap.computeIfAbsent(word, k -> new ArrayList<>()).add(line);
            }
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            return;
        }

        try (BufferedWriter singleWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(singlePath), "UTF-8"));
             BufferedWriter multiWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(multiplePath), "UTF-8"));
             BufferedWriter undoubledWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(outputPath), "UTF-8"))) {

            for (Map.Entry<String, List<String>> entry : dictionaryMap.entrySet()) {
                List<String> variants = entry.getValue();

                if (variants.size() == 1) {
                    // Unique word
                    String line = variants.get(0);
                    singleWriter.write(line);
                    singleWriter.newLine();
                    
                    // Add to the main undoubled file
                    undoubledWriter.write(line);
                    undoubledWriter.newLine();
                } else {
                    // Duplicate word detected
                    for (String line : variants) {
                        multiWriter.write(line);
                        multiWriter.newLine();
                    }
                    
                    // Automatically keep the first occurrence for the undoubled file
                    undoubledWriter.write(variants.get(0));
                    undoubledWriter.newLine();
                }
            }
            
            System.out.println("Process finished successfully.");
            System.out.println("- Singles saved to: " + singlePath);
            System.out.println("- Multiples saved to: " + multiplePath);
            System.out.println("- Default undoubled version saved to: " + outputPath);

        } catch (IOException e) {
            System.err.println("Error writing files: " + e.getMessage());
        }
    }
}