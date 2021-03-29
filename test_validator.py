import sys, json
import argparse
import base64


from fastapi.testclient import TestClient
from annotator import app

client = TestClient(app)

#Test 1
#Post audio file, validate that it IS an audio file
def test_is_audio_file():
    params = {
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "FILE"
        }

    response = client.post("/validate", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    

def test_is_audio_file_wrong_format():
    params = {
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "FILE",
        "audioInputFormat": "MP3"
        }

    response = client.post("/validate", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    

def test_is_audio_file_undefined_format():
    params = {
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "FILE",
        "audioInputFormat": "OGG"
        }

    response = client.post("/validate", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    
    
#Test 2
#Post encoded audio, validate that it IS audio
def test_is_audio_data():
    audiofile = "test_data/shakespeare_part1_par1.wav"
    with open(audiofile, "rb") as fh:
        audiodata = base64.b64encode(fh.read())
    
    params = {
        "audioInput": audiodata
        }

    response = client.post("/validate", json=params)

    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    

#Test 3
#Test that audio contains speech
def test_audio_file_contains_speech():
    params = {
        #"audioInput": "test_data/shakespeare_part1_mono.wav",
        "audioInput": "test_data/shakespeare_part1.wav",
        "audioInputType": "FILE"
        }

    response = client.post("/validate", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    

def test_audio_file_does_not_contain_speech():
    params = {
        "audioInput": "test_data/silence15.wav",
        "audioInputType": "FILE"
        }

    response = client.post("/validate", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200

    expected_validation = {
        "source": "checkAudioContainsSpeech",
        "validation": 0,
        "message": "Audio appears not to contain speech"
    }
    assert expected_validation in response.json()["validation"]
 
    
    debug(json.dumps(response.json(), indent=4))    



verbose = False
def debug(msg):
    if verbose:
        print(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Print verbose output.', action='store_true')

    args = parser.parse_args()
    
    verbose = args.verbose

    #test_audio_file_does_not_contain_speech()
    #sys.exit()
    
    tests = [ m for m in dir() if m.startswith('test_')]
    for test in tests:
        debug(test)
        try:
            globals()[test]()
            sys.stdout.write(".")
            sys.stdout.flush()
            debug(f"OK {test}")
        except:
            print(f"FAIL {test}")
    sys.stdout.write("\n")
    sys.exit()
