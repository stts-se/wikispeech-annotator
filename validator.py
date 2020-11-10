
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
