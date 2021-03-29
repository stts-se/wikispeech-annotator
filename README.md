# wikispeech-annotator

Dependencies

pip install numpy

pip install py3-aeneas 

python3 -m pip install typer[all]


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

http post :4567/align language="en-GB" audioInputType="FILE" audioInput="/home/harald/git/karin_boye/audio/boye_javisstgordetont.mp3" textInputType="FILE" text="/home/harald/git/karin_boye/text/jag_visst_gor_det_ont.txt"
