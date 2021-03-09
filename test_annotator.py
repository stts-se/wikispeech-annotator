import sys, json
import argparse
import base64


from fastapi.testclient import TestClient
from annotator import app

client = TestClient(app)

#Test 1
#Post audio and text file to aeneas for sentence alignment

def test_align_sentences_aeneas_files():
    params = {
        "language": "en-GB",
        "text": "test_data/shakespeare_part1_par1.txt",
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "URL"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    
    print("test_align_sentences_aeneas_files OK")

#Test 2
#Post audio and text data to aeneas for sentence alignment
def test_align_sentences_aeneas_data():
    textfile = "test_data/shakespeare_part1_par1.txt"
    audiofile = "test_data/shakespeare_part1_par1.wav"

    with open(textfile) as fh:
        textdata = fh.read()

    with open(audiofile, "rb") as fh:
        audiodata = base64.b64encode(fh.read())

    
    params = {
        "language": "en-GB",
        "text": textdata,
        "audioInput": audiodata
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))
    print("test_align_sentences_aeneas_data OK")

#Test 3
#Post audio and label file to SHIRO for label alignment
def test_align_phonemes_shiro_files():
    params = {
        "language": "en-GB",
        "text": "hh iy ah n f ow l d ah d ah l ao ng t ay p r ih t ah n l eh t er sil ah n d hh ae n d ah d ih t t uw g r eh g s ah n",
        "audioInput": "test_data/nnc_test/wav/nnc_arctic_0033.wav",
        "audioInputType": "URL",
        "alignMethod": "SHIRO"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))
    print("test_align_phonemes_shiro_files OK")

#Test 4
#Post audio and label data to SHIRO for label alignment

#Test 5
#Post audio and text file to pronlex and SHIRO for label alignment

#Test 6
#Post audio and text file to pronlex and SHIRO for label alignment

def debug(msg):
    if verbose:
        print(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Print verbose output.', action='store_true')

    args = parser.parse_args()
    
    verbose = args.verbose
    
    test_align_sentences_aeneas_files()
    test_align_sentences_aeneas_data()
    test_align_phonemes_shiro_files()

#cli example:
#http post :4567/align language="en-GB" audioInputType="URL" text="test_data/shakespeare_part1_par1.txt" audioInput="test_data/shakespeare_part1_par1.wav"

