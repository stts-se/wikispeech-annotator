# wikispeech-annotator

Dependencies:

python3 -m pip install numpy
python3 -m pip install -r requirements.txt 

Run test server:
python3 -m uvicorn --reload --port 4567 annotator:app

Run server as system service:
sudo make install
sudo systemctl start ws-annotator
sudo systemctl status ws-annotator
journalctl -r -u ws-annotator

sudo systemctl stop ws-annotator
sudo make uninstall




1) json format for annotation:
audio: (file,url,data,..) (timepoints?)
transcription: text, phonetic, .. (timepoints)
other annotations (what? timepoints)

2) simple rest api + cli 

python3 -m uvicorn --port 4567 annotator:app

annotate/text
annotate/transcribe
etc

3) first example:
input is longer soundfile and text
output is json with text+sentence time points

4) second example:
input is sentence soundfile and text
output is json with text+word time points and phonemes+time points


#cli example:
#http post :4567/align language="en-GB" audioInputType="FILE" text="test_data/shakespeare_part1_par1.txt" audioInput="test_data/shakespeare_part1_par1.wav"

http post :4567/align language="sv-SE" audioInputType="FILE" audioInput="/home/harald/git/karin_boye/audio/boye_javisstgordetont.mp3" textInputType="FILE" text="/home/harald/git/karin_boye/text/boye_javisstgordetont.txt"
