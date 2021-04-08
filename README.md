# wikispeech-annotator

Dependencies:
```
sudo apt install python3-venv
sudo apt install libespeak-dev
```
```
python3 -m pip install numpy
python3 -m pip install -r requirements.txt 
```

Run test server:
```
python3 -m uvicorn --reload --port 4567 annotator:app
```

Run server as system service:
```
sudo make install
sudo systemctl start ws-annotator
sudo systemctl status ws-annotator
journalctl -r -u ws-annotator

sudo systemctl stop ws-annotator
sudo make uninstall
```



Example:
input is longer soundfile and text
output is json with text+sentence time points

```
python3 annotator.py align swe ~/git/karin_boye/audio/boye_javisstgordetont.mp3 ~/git/karin_boye/text/boye_javisstgordetont.txt
python3 annotator.py align eng test_data/shakespeare_part1.wav test_data/shakespeare_part1.txt
```

```
http post :4567/align language="en-GB" textInputType="FILE" text=~/git/wikispeech-annotator/test_data/shakespeare_part1_par1.txt audioInputType="FILE" audioInput=~/git/wikispeech-annotator/test_data/shakespeare_part1_par1.wav

http post :4567/align language="sv-SE" audioInputType="FILE" audioInput=~/git/karin_boye/audio/boye_javisstgordetont.mp3 textInputType="FILE" text=~/git/karin_boye/text/boye_javisstgordetont.txt
```


Example:

Validate sound file

```
python3 annotator.py validate test_data/shakespeare_part1.wav
```
```
http post :4567/validate audioInputType="FILE" audioInput=test_data/shakespeare_part1.wav
```

Example:

Get VAD time points for sound file

```
python3 annotator.py vad test_data/shakespeare_part1.wav
python3 annotator.py vad test_data/shakespeare_part1.wav --returntype LAB
```


```
http post :4567/vad audioInputType="FILE" audioInput=test_data/shakespeare_part1.wav
http post :4567/vad audioInputType="FILE" audioInput=test_data/shakespeare_part1.wav returnType=LAB
```




Example:

input is soundfile and phonemes

```
python3 annotator.py align test_data/shakespeare_sent1_phrase1.wav "w ih l ih ah m sh ey k s p iy r" --textinputtype=STRING --alignmethod=SHIRO --language=en-GB
python3 annotator.py align test_data/shakespeare_sent1_phrase1.wav test_data/shakespeare_sent1_phrase1.json --textinputtype=FILE --alignmethod=JSON_SHIRO --language=en-GB
```

```
http post :4567/align audioInputType="FILE" audioInput=test_data/shakespeare_sent1_phrase1.wav textInputType=STRING text="w ih l ih ah m sh ey k s p iy r" alignMethod=SHIRO language=en-GB
http post :4567/align audioInputType="FILE" audioInput=test_data/shakespeare_sent1_phrase1.wav textInputType=FILE text=test_data/shakespeare_sent1_phrase1.json alignMethod=JSON_SHIRO language=en-GB 
```



output is json with text+word time points and phonemes+time points
