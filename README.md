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

python3 -m uvicorn annotator:app

annotate/text
annotate/transcribe
etc

3) first example:
input is longer soundfile and text
output is json with text+sentence time points

4) second example:
input is sentence soundfile and text
output is json with text+word time points and phonemes+time points
