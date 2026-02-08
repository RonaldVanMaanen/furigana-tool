import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;
import java.io.IOException;

public class RemoveDuplicates {
    public static void main(String[] args) {
        String source = "L:\\FuriganaTool\\Combined.csv";
        String out = "L:\\FuriganaTool\\JP_Total_List_D.CSV";
        // String source = "L:\\FuriganaTool\\Verb_Type_Definition.csv";
        // String out = "L:\\FuriganaTool\\Verb_Type_Definition_D.csv";
        Path inputPath = Paths.get(source);
        Path outputPath = Paths.get(out);

        try {
            // 1. Load file and filter duplicates using Stream.distinct()
            List<String> uniqueLines = Files.lines(inputPath)
                                            .distinct()
                                            .collect(Collectors.toList());

            // 2. Save the result back to a file
            Files.write(outputPath, uniqueLines);

            System.out.println("Duplicates removed successfully!");

        } catch (IOException e) {
            System.err.println("An error occurred: " + e.getMessage());
            e.printStackTrace(); // This prints the sequence of method calls leading to the error
        }
    }
}