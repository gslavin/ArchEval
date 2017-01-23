from multiprocessing import Process
import multiprocessing
import time
import random

class SearchState():
    def __init__(self, config):
        self.config = config

def run_monitor(search_parties):
    """
    Kills certain processes
    TODO: modify to accept the number of the process to kill
    """
    while search_parties:
        time.sleep(5 * random.random())
        kill_target = search_parties.pop(random.randrange(len(search_parties)))
        print(kill_target[0])
        kill_target[0].terminate()

def run_search_party(search_state):
    # Run simulation
    while True:
        time.sleep(0.5 * random.random())
        (tid, value) = search_state.config
        search_state.config = (tid, value + 1)
        print(search_state.config)

if __name__ == '__main__':
    num_search_parties = 3
    initial_sys_configs = []
    # Set initial node values  for each search party (each have a copy of the search state)
    for i in range(num_search_parties):
        initial_sys_config = (i, i)
        initial_sys_configs.append(initial_sys_config)

    # Create each search party
    parties = []
    for config in initial_sys_configs:
        search_state = SearchState(config)
        p = Process(target=run_search_party, args=(search_state,))
        parties.append((p, search_state))

    # Create monitoring thread
    monitor_thread = Process(target=run_monitor, args=(parties, ))

    # Run search parties
    for party in parties:
        party[0].start()

    # Run monitor
    monitor_thread.start()

    # Wait until only the monitor process is active
    while len(multiprocessing.active_children()) > 1:
        print("active childen: {}".format(multiprocessing.active_children()))
        time.sleep(4)

    print("all done!")
