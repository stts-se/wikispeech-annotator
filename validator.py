import os, sys
import contextlib, wave, webrtcvad, collections



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
        #print(f"{wavfile}\t{frame.timestamp}")
        if vad.is_speech(frame.bytes, sample_rate):
            return True
    return False


def getVadTimepoints(wavfile):
    #check that the file is in fact wav mono!
    with contextlib.closing(wave.open(wavfile, 'rb')) as wf:
        if wf.getnchannels() == 2:
            monofile = "/tmp/vad_tmp.wav"
            os.system(f"sox {wavfile} -c 1 {monofile}")
            wavfile = monofile
            
    (pcm_data, sample_rate) = read_wave(wavfile)
    frame_duration_ms = 10
    frames = frame_generator(frame_duration_ms, pcm_data, sample_rate)
    vad = webrtcvad.Vad()
    padding_duration_ms = 30
    segments = vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames)

    longsegments = list()
    min_dur = 1
    counter = 1
    for segment in segments:
        #skip "speech" segment starting at beginning of file (is this always the right thing to do?)
        if segment["start"] == 0.0:
            continue
        if segment["end"]-segment["start"] > min_dur:
            segment["text"] = counter
            longsegments.append(segment)
            counter += 1
    return longsegments
    
def getVadTimepointsX(wavfile):
    vad_timepoints = list()
    
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
            #vad_timepoints.append("%.2f" % frame.timestamp)
            vad_timepoints.append(round(frame.timestamp, 2))


    segments = []
    speech_segment = []
    prev_tp = 0
    for timepoint in vad_timepoints:
        print(timepoint)
        if timepoint == prev_tp+0.03:
            speech_segment.append(timepoint)
        else:
            print("HEJSAN")
            if len(speech_segment) > 10:
                segments.append("%.2f\t%.2f" % (speech_segment[0], speech_segment[-1]))
            speech_segment = []
        prev_tp = timepoint
            
    return segments            
    #return vad_timepoints




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


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                #yield b''.join([f.bytes for f in voiced_frames])
                #yield ''.join([str(f.timestamp) for f in voiced_frames])
                yield {
                    "start":round(voiced_frames[0].timestamp, 2),
                    "end":round(voiced_frames[-1].timestamp, 2)
                }
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        #yield b''.join([f.bytes for f in voiced_frames])
        #yield ''.join([str(f.timestamp) for f in voiced_frames])
        #yield "%.2f\t%.2f" % (voiced_frames[0].timestamp, voiced_frames[-1].timestamp)
        yield {
            "start":round(voiced_frames[0].timestamp, 2),
            "end":round(voiced_frames[-1].timestamp, 2)
        }

        
#END FROM py-webrtcvad example.py

