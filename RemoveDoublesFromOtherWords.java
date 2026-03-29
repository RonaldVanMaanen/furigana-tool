import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class RemoveDoublesFromOtherWords {
    public static void main(String[] args) {
        String pathA = "L:\\FuriganaTool\\Verbs_out.csv";
        String pathB = "L:\\FuriganaTool\\Other_words.txt";
        String pathC = "L:\\FuriganaTool\\Other_words_4.txt";

        try {
            // Load File A into a Set for lightning-fast lookups
            List<String> linesA = Files.readAllLines(Paths.get(pathA));
            Set<String> setA = new HashSet<>(linesA); 
            
            System.out.println("File A (Lines) Set Size: " + setA.size());

            // Read File B and split into words
            String contentB = Files.readString(Paths.get(pathB));
            String[] arrayB = contentB.split("\\s+");

            List<String> arrayC = new ArrayList<>();
            System.out.println("File B (Words) Array Length: " + arrayB.length);
            
            // Loop through File B words
            for (int i = 0; i < arrayB.length; i++) {
                String currentWord = arrayB[i];
                
                // Check if File A contains this word
                if (!setA.contains(currentWord)) {
                    arrayC.add(currentWord);
                }
            }

            // Write the result to File C
            Files.write(Paths.get(pathC), arrayC);
            System.out.println("Successfully wrote arrayC to " + pathC);

        } catch (IOException e) {
            System.err.println("Error processing files: " + e.getMessage());
        }
    }
}