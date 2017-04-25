import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = ROOT_DIR + "/_TestOut"
GEM5_DIR = ROOT_DIR + "/../gem5"
BENCHMARK_PATH = ROOT_DIR + "/Tests/test-progs/random_access/random_access --options=100"
SYNCHROTRACE_DIR = ROOT_DIR + "/../SynchroTrace-gem5"
# EVENT is the trace of the benchmarchn extracted via sigil2
EVENT_DIR = ROOT_DIR + "/../sigil2/build/out"
