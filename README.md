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

cli example:
```
http post :4567/align language="en-GB" textInputType="FILE" text=~/git/wikispeech-annotator/test_data/shakespeare_part1_par1.txt audioInputType="FILE" audioInput=~/git/wikispeech-annotator/test_data/shakespeare_part1_par1.wav

http post :4567/align language="sv-SE" audioInputType="FILE" audioInput=~/git/karin_boye/audio/boye_javisstgordetont.mp3 textInputType="FILE" text=~/git/karin_boye/text/boye_javisstgordetont.txt
```


Second example:
input is sentence soundfile and text
output is json with text+word time points and phonemes+time points
