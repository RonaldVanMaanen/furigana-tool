import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class FileSorter {
    public static void main(String[] args) {
        // 1. Define input and output paths
        String source = "L:\\FuriganaTool\\JP_Total_List_D.CSV";
        String out = "L:\\FuriganaTool\\JP_Total_List_S.CSV";
        
        Path inputPath = Paths.get(source);
        Path outputPath = Paths.get(out);

        // 2. Process the file
        // Using try-with-resources ensures the Stream closes automatically
        try (Stream<String> lineStream = Files.lines(inputPath)) {

            List<String> sortedLines = lineStream
                // Filter out empty lines to prevent errors
                .filter(line -> line != null && !line.trim().isEmpty())
                // 3. Sort logic: Split by comma, get length of first part
                .sorted(Comparator.comparingInt((String line) -> {
                    // Split by comma (limit 2 is slightly faster as we don't need the rest)
                    String[] parts = line.split(",", 2); 
                    // Return length of first part, or 0 if line is empty
                    return parts.length > 0 ? parts[0].length() : 0;
                }).reversed()) // .reversed() keeps it Longest -> Shortest
                .collect(Collectors.toList());

            // 4. Save the sorted lines
            Files.write(outputPath, sortedLines);

            System.out.println("File processed successfully!");
            System.out.println("Source: " + inputPath.toAbsolutePath());
            System.out.println("Output: " + outputPath.toAbsolutePath());

        } catch (IOException e) {
            System.err.println("An error occurred processing the file.");
            e.printStackTrace();
        }
    }
}