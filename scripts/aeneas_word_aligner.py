import sys


from aeneas.exacttiming import TimeValue
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc

# create Task object
config = TaskConfiguration()
#config[gc.PPN_TASK_LANGUAGE] = Language.ENG
config[gc.PPN_TASK_LANGUAGE] = sys.argv[1]
config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.MPLAIN
config[gc.PPN_TASK_OS_FILE_FORMAT] = SyncMapFormat.AUD
config["os_task_file_levels"] = 3
task = Task()
task.configuration = config
#task.audio_file_path_absolute = u"test_data/shakespeare_sent1.wav"
#task.text_file_path_absolute = u"test_data/shakespeare_sent1.txt"
task.audio_file_path_absolute = sys.argv[2]
task.text_file_path_absolute = sys.argv[3]


rconf = RuntimeConfiguration()
rconf[RuntimeConfiguration.MFCC_MASK_NONSPEECH] = True
rconf[RuntimeConfiguration.MFCC_MASK_NONSPEECH_L3] = True

# process Task
ExecuteTask(task, rconf).execute()

# print produced sync map
for fragment in task.sync_map_leaves():
    if fragment.text != "":
        print("%f %f %s" % (fragment.begin, fragment.end, fragment.text))
