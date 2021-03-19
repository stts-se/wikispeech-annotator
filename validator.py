import os
import contextlib, wave, webrtcvad



default_config = {
    "validation_steps":
    [
        {
            "function": "segment_averageCharDuration",
            "config": {
                "minAverageCharDuration": 56,
                "maxAverageCharDuration": 85
            }
        }
    ]
}

Xdefault_config = {
    "validation_steps":
    [
        {
            "function": "segment_averageCharDuration",
            "config": {
                "minAverageCharDuration": 10,
                "maxAverageCharDuration": 100
            }
        }
    ]
}


class validator:
    def __init__(self, config={}, verbose=False):

        self.verbose = verbose

        self.valid = True
        
        self.messages = []
        self.config = config

    def debug(self, msg):
        if self.verbose:
            print(msg)

        
    def run(self, audio, data):

        config = self.validateLanguageConfig(data)

        nr = 1
        for segment in data["alignment"]:
            segment["messages"] = []
            segment["valid"] = True
            segment["nr"] = nr
            
            for step in config["validation_steps"]:
                self.debug(step)
                segment = globals()[step["function"]](segment, step["config"])
                if not segment["valid"]:
                    self.valid = False
                    self.messages.extend(segment["messages"])

                self.debug(segment)
            nr += 1
        
        return {
            "valid": self.valid,
            "messages": self.messages
        }
    

    def validateLanguageConfig(self, json):
        self.debug(json["language"])
        if not json["language"] in self.config:
            msg = "No configuration for language %s, using default configuration." % json["language"]
            self.messages.append(msg)
        else:
            msg = "Config for %s: %s" % (json["language"], self.config[json["language"]])
            self.messages.append(msg)
            return self.config[json["language"]]
        self.debug(self.messages)

        return default_config




def segment_averageCharDuration(segment, config):
    minAverageCharDuration = config["minAverageCharDuration"]
    maxAverageCharDuration = config["maxAverageCharDuration"]

    nr = segment["nr"]
     
    duration = segment["end"]-segment["start"]
    nchars = len(segment["text"])
    averageCharDuration = duration/nchars
    if averageCharDuration < minAverageCharDuration:
        msg = "Too short (segment %d): averageCharDuration: %.2f, minAverageCharDuration: %.2f" % (nr, averageCharDuration, minAverageCharDuration)
        segment["valid"] = False
    elif averageCharDuration > maxAverageCharDuration:
        msg = "Too long (segment %d): averageCharDuration: %.2f, maxAverageCharDuration: %.2f" % (nr, averageCharDuration, maxAverageCharDuration)
        segment["valid"] = False
    else:
        msg = "averageCharDuration (segment %d): %.2f" % (nr, averageCharDuration)
    segment["messages"].append(msg)

    return segment




def voice_activity_detection(wavfile):
    #check that the file is in fact wav mono!
    with contextlib.closing(wave.open(wavfile, 'rb')) as wf:
        if wf.getnchannels() == 2:
            monofile = "/tmp/vad_tmp.wav"
            os.system(f"sox {wavfile} -c 1 {monofile}")
            wavfile = monofile
            
    (pcm_data, sample_rate) = read_wave(wavfile)
    frames = frame_generator(30, pcm_data, sample_rate)
    vad = webrtcvad.Vad()
    for frame in frames:
        if vad.is_speech(frame.bytes, sample_rate):
            return True
    return False

#FROM py-webrtcvad example.py
def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate



class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n

#END FROM py-webrtcvad example.py

