
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

public class VerbFinder {
    public static void main(String[] args) {
        String source  = "E:\\Downloads_Scans\\日本語\\words.csv";
        String out  = "E:\\Downloads_Scans\\日本語\\found_verbs.csv";
        String output="";
        String[] verbEnd={"う","く","ぐ","す","つ","ぬ","む","る"};

        try {
            List<String> lines = Files.readAllLines(Paths.get(source));
            for (String line : lines) {
                String[] aParts = line.split(("\t"));
                for (int i = 0; i < verbEnd.length; i++) {
                    if(aParts[0].endsWith(verbEnd[i])) {
                        output=output+aParts[0]+"\r\n";
                    }   
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