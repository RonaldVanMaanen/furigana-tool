
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

public class FileSplitter {
    public static void main(String[] args) {
        String source  = "L:\\ふりがなのプロジェクト\\words.csv";
        String out  = "L:\\ふりがなのプロジェクト\\words_2.csv";
        String output="";

        try {
            List<String> lines = Files.readAllLines(Paths.get(source));
            for (String line : lines) {
                String[] aParts = line.split(("\t"));
                if(aParts[0]!=aParts[1]) {
                    output=output+aParts[0]+","+aParts[1]+"\r\n";
                }
            }
        } catch (Exception e) {
            // TODO: handle exception
        }

        try {
            FileWriter myWriter = new FileWriter(out);
            myWriter.write(output);
            myWriter.close();  // must close manually
            System.out.println("Successfully wrote to the file.");
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }
}