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
        "textInputType": "FILE",
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "FILE"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    

def test_align_sentences_aeneas_files_html_out():
    params = {
        "language": "en-GB",
        "text": "test_data/shakespeare_part1_par1.txt",
        "textInputType": "FILE",
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "FILE",
        "returnType": "HTML"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(response.text)    


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

def test_align_sentences_aeneas_data_html_out():
    textfile = "test_data/shakespeare_part1_par1.txt"
    audiofile = "test_data/shakespeare_part1_par1.wav"

    with open(textfile) as fh:
        textdata = fh.read()

    with open(audiofile, "rb") as fh:
        audiodata = base64.b64encode(fh.read())

    
    params = {
        "language": "en-GB",
        "text": textdata,
        "audioInput": audiodata,
        "returnType": "HTML"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(response.text)


#Test 3
#Post audio and label file to SHIRO for label alignment
def test_align_phonemes_shiro_files():
    params = {
        "language": "en-GB",
        "text": "test_data/nnc_test/lab/nnc_arctic_0033.phones",
        "textInputType": "FILE",
        "audioInput": "test_data/nnc_test/wav/nnc_arctic_0033.wav",
        "audioInputType": "FILE",
        "alignMethod": "SHIRO"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))


#Test 4
#Post audio and label data to SHIRO for label alignment
def test_align_phonemes_shiro_data():

    audiofile = "test_data/nnc_test/wav/nnc_arctic_0033.wav"
    with open(audiofile, "rb") as fh:
        audiodata = base64.b64encode(fh.read())

    params = {
        "language": "en-GB",
        "text": "hh iy ah n f ow l d ah d ah l ao ng t ay p r ih t ah n l eh t er sil ah n d hh ae n d ah d ih t t uw g r eh g s ah n",
        "audioInput": audiodata,
        "alignMethod": "SHIRO"
        }
    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))



#Test 5
#Post audio and transcribed json file to SHIRO for label alignment
def test_align_json_shiro_files():
    params = {
        "language": "en-GB",
        "text": "test_data/nnc_test/lab/nnc_arctic_0033.json",
        "textInputType": "FILE",
        "audioInput": "test_data/nnc_test/wav/nnc_arctic_0033.wav",
        "audioInputType": "FILE",
        "alignMethod": "JSON_SHIRO"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))


#Test 6
#Post audio and transcribed json data to SHIRO for label alignment
def test_align_json_shiro_data():
    textfile = "test_data/nnc_test/lab/nnc_arctic_0033.json"
    audiofile = "test_data/nnc_test/wav/nnc_arctic_0033.wav"

    with open(textfile) as fh:
        textdata = fh.read()

    with open(audiofile, "rb") as fh:
        audiodata = base64.b64encode(fh.read())

    params = {
        "language": "en-GB",
        "text": textdata,
        "audioInput": audiodata,
        "alignMethod": "JSON_SHIRO"
        }

    response = client.post("/align", json=params)
    if response.status_code != 200:
        print(response)
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))


    
#Test 7
#Post audio and text file to pronlex and SHIRO for label alignment

#Test 8
#Post audio and text data to pronlex and SHIRO for label alignment



#Test 9
#Post audio file to vad
def test_vad_file():
    params = {
        "language": "en-GB",
        "audioInput": "test_data/shakespeare_part1_par1.wav",
        "audioInputType": "FILE"
        }

    response = client.post("/vad", json=params)
    if response.status_code != 200:
        print(response)
        print(response.json())
    assert response.status_code == 200
    debug(json.dumps(response.json(), indent=4))    




verbose = False
def debug(msg):
    if verbose:
        print(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Print verbose output.', action='store_true')
    parser.add_argument('-e', '--exit-on-error', help='Exit on first error.', action='store_true')

    args = parser.parse_args()
    
    verbose = args.verbose

    #HB 
    test_align_sentences_aeneas_files_html_out()
    sys.exit()
    
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
            if args.exit_on_error:
                sys.exit()
    sys.stdout.write("\n")
    sys.exit()
    
    test_align_sentences_aeneas_files()
    test_align_sentences_aeneas_data()
    test_align_phonemes_shiro_files()
    test_align_phonemes_shiro_data()
    test_align_json_shiro_files()
    test_align_json_shiro_data()



#Run from this main, or just run "pytest"

    
#cli example:
#http post :4567/align language="en-GB" audioInputType="FILE" text="test_data/shakespeare_part1_par1.txt" audioInput="test_data/shakespeare_part1_par1.wav"
#http post :4567/vad language="en-GB" audioInputType="FILE" audioInput="test_data/shakespeare_part1_par1.wav"

