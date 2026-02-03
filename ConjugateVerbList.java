
import java.io.Console;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

public class ConjugateVerbList {
    
    public static void main(String[] args) {
        String source  = "L:\\FuriganaTool\\Verb_Type_Definition.csv";
        String out  = "L:\\FuriganaTool\\Verbs_out.csv";
        String outCheck  = "L:\\FuriganaTool\\Verbs_out_Check.csv";
        String output="";
        String outputCheck="";
        int countedLines=0;
        int cutOff=0;
        String stemKanji="";
        String stemKana="";
        String pronounciation="";
        //String[] godanUEnding={"買う","会う","","",""};

        try {
            List<String> lines = Files.readAllLines(Paths.get(source));
            for (String line : lines) {
                countedLines=countedLines+1;
                outputCheck=outputCheck+">> Line : "+countedLines+"\r\n";
                outputCheck=outputCheck+">> Start : "+line+"\r\n";
                String[] aParts = line.split((","));
                System.out.println(aParts[2]);
                
                outputCheck=outputCheck+">> Start : "+aParts[0]+"\r\n"; 

                // Determine cut off
                if (aParts[2].equals("ichidan")) {
                    cutOff=1;
                    outputCheck=outputCheck+">"+aParts[0]+" = ichidan\r\n";
                } else if (aParts[2].equals("godan")) {
                    cutOff=1;
                    outputCheck=outputCheck+">"+aParts[0]+" = godan\r\n";
                } else if (aParts[2].equals("special")) {
                    cutOff=2;
                    outputCheck=outputCheck+">"+aParts[0]+" = special\r\n";
                } else if (aParts[2].equals("suru")) {
                    cutOff=2;
                    outputCheck=outputCheck+">"+aParts[0]+" = suru\r\n";
                }

                // Strip to renyoukei
                if (aParts[2].equals("suru")) {
                    // No stripping
                    stemKanji=aParts[0];
                    stemKana=aParts[1];
                    
                    pronounciation=aParts[3];
                    outputCheck=outputCheck+">"+aParts[0]+" = suru stripping \r\n";
                } else if (aParts[2].equals("ichidan")) {
                    stemKanji=getStem(aParts[0],cutOff,false);
                    stemKana=getStem(aParts[1],cutOff,false);
                    //pronounciation=getStem(aParts[3],cutOff,false);
                    pronounciation=aParts[3];
                    
                    outputCheck=outputCheck+">"+aParts[0]+" = ichidan stripping \r\n";
                    outputCheck=outputCheck+"stem Kanji = "+stemKanji+"\r\n";
                    outputCheck=outputCheck+"stem kana = "+stemKana+"\r\n";
                    outputCheck=outputCheck+"pronounciation = "+pronounciation+"\r\n";
                } else if (aParts[2].equals("godan")) {
                    stemKanji=getStem(aParts[0],cutOff,true);
                    stemKana=getStem(aParts[1],cutOff,true);
                    // pronounciation=getStem(aParts[3],cutOff,true);
                    pronounciation=aParts[3];

                    outputCheck=outputCheck+"> Forced stripping\r\n";
                    outputCheck=outputCheck+">"+aParts[0]+" = godan stripping \r\n";
                    outputCheck=outputCheck+"stem Kanji = "+stemKanji+"\r\n";
                    outputCheck=outputCheck+"stem kana = "+stemKana+"\r\n";
                    outputCheck=outputCheck+"pronounciation = "+pronounciation+"\r\n";
                } else if (!aParts[2].equals("special")) {
                    // Ichidan, Godan, Special
                    stemKanji=getStem(aParts[0],cutOff,false);
                    stemKana=getStem(aParts[1],cutOff, false);
                    // pronounciation=getStem(aParts[3],cutOff,false);
                    pronounciation=aParts[3];

                    outputCheck=outputCheck+">"+aParts[0]+" = special stripping \r\n";
                    outputCheck=outputCheck+"stem Kanji = "+stemKanji+"\r\n";
                    outputCheck=outputCheck+"stem kana = "+stemKana+"\r\n";
                    outputCheck=outputCheck+"pronounciation = "+pronounciation+"\r\n";
                } 
            
                // Build output
                if(aParts[2].equals("suru")){
                    output=output+stemKanji+","+pronounciation+"\r\n";
                }

                if(aParts[2].equals("ichidan")){
                    outputCheck=outputCheck+"> Entering ichidan\r\n";
                    // Create conjugations
                    // Polite, TT / VT + Ontkennend
                    output=output+stemKanji+"ま"+","+pronounciation+"\r\n";
                    // Coll., TT 
                    output=output+stemKanji+"る"+","+pronounciation+"\r\n";
                    // Coll., VT 
                    output=output+stemKanji+"た"+","+pronounciation+"\r\n";
                    // Coll., Ont, TT+VT
                    output=output+stemKanji+"な"+","+pronounciation+"\r\n";
                    // Coll., Ont, TT+VT　(oud japans)
                    output=output+stemKanji+"ず"+","+pronounciation+"\r\n";
                    // Te-form
                    output=output+stemKanji+"て"+","+pronounciation+"\r\n";
                    // Volitional
                    // output=output+stemKanji+"よう"+","+pronounciation+"\r\n";
                    output=output+stemKanji+"よ"+","+pronounciation+"\r\n";
                    // Potential　Bev. + Ont + Passive　Bev. + Ont
                    // output=output+stemKanji+"られ"+","+pronounciation+"\r\n";
                    output=output+stemKanji+"ら"+","+pronounciation+"\r\n";
                    // Passive　Bev. + Ont
                    // output=output+stemKanji+"られ"+","+pronounciation+"\r\n";
                    // Causative　Bev. + Ont
                    // output=output+stemKanji+"させ"+","+pronounciation+"\r\n";
                    output=output+stemKanji+"さ"+","+pronounciation+"\r\n";
                    // Imperative　
                    output=output+stemKanji+"ろ"+","+pronounciation+"\r\n";

                }

                if(aParts[2].equals("godan")){
                    String endSound="";
                    outputCheck=outputCheck+"> Entering godan\r\n";
                    // Get end sound
                    endSound=getEndSound(aParts[0]);
                    if(endSound.equals("く")){
                        outputCheck=outputCheck+"> Entering godan > く\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"き"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"く"+","+pronounciation+"\r\n";
                        // Coll., VT + Te-form
                        // output=output+stemKanji+"いた"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"い"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Coll., Ont, TT+VT　(oud japans) + Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"かな"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"か"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT　(oud japans)
                        // output=output+stemKanji+"かず"+","+pronounciation+"\r\n";
                        // Te-form
                        // output=output+stemKanji+"いて"+","+pronounciation+"\r\n";
                        // Volitional
                        output=output+stemKanji+"おう"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont
                        output=output+stemKanji+"け"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"かれ"+","+pronounciation+"\r\n";
                        // output=output+stemKanji+"か"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"かせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        output=output+stemKanji+"え"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("ぐ")){
                        outputCheck=outputCheck+"> Entering godan > ぐ\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"ぎ"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"ぐ"+","+pronounciation+"\r\n";
                        // Coll., VT +Te-form
                        // output=output+stemKanji+"いた"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"い"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Coll., Ont, TT+VT　(oud japans) + Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"がな"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"が"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT　(oud japans)
                        //output=output+stemKanji+"がず"+","+pronounciation+"\r\n";
                        // Te-form
                        // output=output+stemKanji+"いて"+","+pronounciation+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"おう"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"お"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont
                        output=output+stemKanji+"げ"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"がれ"+","+pronounciation+"\r\n";
                        // output=output+stemKanji+"が"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"がせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        output=output+stemKanji+"え"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("す")){
                        outputCheck=outputCheck+"> Entering godan > す\r\n";

                        // Create conjugations
                        // Polite, TT / VT + Ontkennend + te-form + ta form
                        output=output+stemKanji+"し"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"す"+","+pronounciation+"\r\n";
                        // Coll., VT 
                        // output=output+stemKanji+"した"+","+stemKana+"した"+"\r\n";
                        // Coll., Ont, TT+VT
                        // output=output+stemKanji+"さな"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT　(oud japans) + Coll., Ont, TT+VT + Passive　Bev. + Ont + Causative　Bev. + Ont
                        output=output+stemKanji+"さ"+","+pronounciation+"\r\n";
                        // Te-form
                        // output=output+stemKanji+"して"+","+stemKana+"して"+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"そう"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"そ"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont + Imperative　
                        output=output+stemKanji+"せ"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont
                        // output=output+stemKanji+"され"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"させ"+","+pronounciation+"\r\n";
                        // Imperative　
                        // output=output+stemKanji+"せ"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("つ")){
                        outputCheck=outputCheck+"> Entering godan > つ\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"ち"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"つ"+","+pronounciation+"\r\n";
                        // Coll., VT 
                        output=output+stemKanji+"った"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Oud japans ontkennend
                        output=output+stemKanji+"た"+","+pronounciation+"\r\n";
                        // Te-form
                        output=output+stemKanji+"って"+","+pronounciation+"\r\n";
                        // Volitional
                        output=output+stemKanji+"とう"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont
                        output=output+stemKanji+"げ"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"たれ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"た"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"たせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        output=output+stemKanji+"て"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("ぬ")){
                        outputCheck=outputCheck+"> Entering godan > ぬ\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"に"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"ぬ"+","+pronounciation+"\r\n";
                        // Coll., VT + Te-form
                        // output=output+stemKanji+"んだ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ん"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Oud japans ont
                        output=output+stemKanji+"な"+","+pronounciation+"\r\n";
                        // Te-form
                        // output=output+stemKanji+"んで"+","+pronounciation+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"のう"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"の"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont
                        output=output+stemKanji+"ね"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"なれ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"な"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"なせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        output=output+stemKanji+"ね"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("む")){
                        outputCheck=outputCheck+"> Entering godan > む\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"み"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"む"+","+pronounciation+"\r\n";
                        // Coll., VT + Volitional + Te-form
                        // output=output+stemKanji+"んだ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ん"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Oud japans ont + Causative　Bev. + Ont
                        output=output+stemKanji+"ま"+","+pronounciation+"\r\n";
                        // Te-form
                        // output=output+stemKanji+"んで"+","+pronounciation+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"もう"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont + Imperative　
                        output=output+stemKanji+"め"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont
                        // output=output+stemKanji+"なれ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"な"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"ませ"+","+pronounciation+"\r\n";
                        // Imperative　
                        // output=output+stemKanji+"め"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("ぶ")){
                        outputCheck=outputCheck+"> Entering godan > ぶ\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"び"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"ぶ"+","+pronounciation+"\r\n";
                        // Coll., VT + Te-form
                        // output=output+stemKanji+"んだ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ん"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Oud japans ont
                        output=output+stemKanji+"ば"+","+pronounciation+"\r\n";
                        // Te-form
                        //output=output+stemKanji+"んで"+","+pronounciation+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"ぼう"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ぼ"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont
                        output=output+stemKanji+"べ"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"ばれ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ば"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"ばせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        output=output+stemKanji+"べ"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("る")){
                        // Create conjugations
                        outputCheck=outputCheck+"> Entering godan > る\r\n";
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"り"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"る"+","+pronounciation+"\r\n";
                        // Coll., VT 
                        output=output+stemKanji+"った"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Oud japans ontkennend
                        output=output+stemKanji+"ら"+","+pronounciation+"\r\n";
                        // Te-form
                        output=output+stemKanji+"って"+","+pronounciation+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"ろう"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ろ"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont + Imperative　
                        output=output+stemKanji+"れ"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"られ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"ら"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"らせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        // output=output+stemKanji+"れ"+","+pronounciation+"\r\n";
                    }

                    if(endSound.equals("う")){
                        outputCheck=outputCheck+"> Entering godan > う\r\n";
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        output=output+stemKanji+"い"+","+pronounciation+"\r\n";
                        // Coll., TT 
                        output=output+stemKanji+"う"+","+pronounciation+"\r\n";
                        // Coll., VT 
                        output=output+stemKanji+"った"+","+pronounciation+"\r\n";
                        // Coll., Ont, TT+VT + Oud japans ontkennend
                        output=output+stemKanji+"わ"+","+pronounciation+"\r\n";
                        // Te-form
                        output=output+stemKanji+"って"+","+pronounciation+"\r\n";
                        // Volitional
                        // output=output+stemKanji+"おう"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"お"+","+pronounciation+"\r\n";
                        // Potential　Bev. + Ont + Imperative　
                        output=output+stemKanji+"え"+","+pronounciation+"\r\n";
                        // Passive　Bev. + Ont + Causative　Bev. + Ont
                        // output=output+stemKanji+"われ"+","+pronounciation+"\r\n";
                        output=output+stemKanji+"わ"+","+pronounciation+"\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"わせ"+","+pronounciation+"\r\n";
                        // Imperative　
                        // output=output+stemKanji+"え"+","+pronounciation+"\r\n";
                    }
                }
                if(aParts[2].equals("irregular")){
                    outputCheck=outputCheck+"> irregular \r\n";
                    if (aParts[0].equals("来る")) {
                        // Create conjugations
                        // Polite, TT / VT + Ontkennend
                        // output=output+stemKanji+"ま"+",き\r\n";
                        output=output+"来ま,き\r\n";
                        // Coll., TT 
                        // output=output+stemKanji+"る"+",く\r\n";
                        output=output+"来る,く\r\n";
                        // Coll., VT 
                        // output=output+stemKanji+"た"+",き\r\n";
                        output=output+"来た,き\r\n";
                        // Coll., Ont, TT+VT + Oud japans ontkennend
                        // output=output+"来な,こな\r\n";
                        output=output+"来な,こ\r\n";
                        // Te-form
                        // output=output+stemKanji+"て"+",き\r\n";
                        output=output+"来て,き\r\n";
                        // Volitional
                        // output=output+stemKanji+"よ"+",こ\r\n";
                        output=output+"来よ,こ\r\n";
                        // Potential　Bev. + Ont　+　Passive　Bev. + Ont
                        // output=output+stemKanji+"られ"+",こられ\r\n";
                        output=output+"来ら,こ\r\n";
                        // Passive　Bev. + Ont
                        // output=output+stemKanji+"られ,こられ\r\n";
                        // Causative　Bev. + Ont
                        // output=output+stemKanji+"させ,こされ\r\n";
                        output=output+"来さ,こ\r\n";
                        // Imperative　
                        // output=output+stemKanji+"おい,こい\r\n";
                        output=output+"来お,こ\r\n";
                    }
                }

                if(aParts[2].equals("special")){
                    outputCheck=outputCheck+"> sepcial \r\n";
                    // Create conjugations for e.g. 愛する､
                    // Polite, TT / VT + Ontkennend
                    output=output+stemKanji+"します"+","+pronounciation+"\r\n";
                    // Coll., TT 
                    output=output+stemKanji+"する"+","+pronounciation+"\r\n";
                    // Coll., VT + Ont, TT+VT + Coll., Ont, TT+VT　(oud japans) + Te-form
                    output=output+stemKanji+"し"+","+pronounciation+"\r\n";
                    // Coll., VT 
                    // output=output+stemKanji+"した"+","+pronounciation+"\r\n";
                    // Coll., Ont, TT+VT
                    // output=output+stemKanji+"しな"+","+pronounciation+"\r\n";
                    // Coll., Ont, TT+VT　(oud japans)
                    // output=output+stemKanji+"しず"+","+pronounciation+"\r\n";
                    // Te-form
                    // output=output+stemKanji+"して"+","+pronounciation+"\r\n";
                    // Volitional
                    output=output+stemKanji+"そ"+","+pronounciation+"\r\n";
                    // Potential　Bev. + Ont
                    output=output+stemKanji+"せ"+","+pronounciation+"\r\n";
                    // Passive　Bev. + Ont
                    // output=output+stemKanji+"さら"+","+pronounciation+"\r\n";
                    // Causative　Bev. + Ont
                    output=output+stemKanji+"さ"+","+pronounciation+"\r\n";
                    // Imperative　
                    output=output+stemKanji+"せ"+","+pronounciation+"\r\n";

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

        try {
            FileWriter myWriter = new FileWriter(outCheck);
            myWriter.write(outputCheck);
            myWriter.close();  // must close manually
            System.out.println("Successfully wrote to the file.");
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }
    private static String getStem(String string, int cutOff, boolean forceCutOff ) {
        // Split the last kana from the string to get renyoukei
        String sOut="";
        if (string.length()>1){
            if (forceCutOff) {    
                sOut=string.substring(0, string.length()-cutOff);
            } else { // false
                if(string.length()>2){
                    sOut=string.substring(0, string.length()-cutOff);
                } else {
                    sOut=string;
                }
            }
        } else {
            sOut=string;
        }
        
        return sOut;
    }

    private static String getEndSound(String string) {
        String sOut="";
        sOut=string.substring(string.length()-1,string.length());
        return sOut;
    }
}