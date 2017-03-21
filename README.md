# daFre
Forced alignment tool

# File structure for daFre.py

+template\www            : contains the templates for html
+list.tx                 : contains the list of units to force aligne. The file has the following structure:
                          Title - Dialogue 1 / - Dialogue 2 p## p##  DEMO DONE
                          DEMO, DONE are keywords to ignore line. DONE is uset for bookeping
+audio_karaoke_echanges\ : contains all the audio files mp3s and text files with the same name but txt with text.
                          Eg: u1_dialogue_1.mp3 ; u1_dialogue_1.txt

+output: all audio files will generate directories with the same name and inside there will be a template directory for html and the 
        required audio file
