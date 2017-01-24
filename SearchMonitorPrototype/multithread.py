#!/usr/bin/python3

from multiprocessing import Process, Lock
import multiprocessing
import time
import random

# TODO: implement loggging
#       The logging module is already threadsafe

class SearchParty():
    def __init__(self, p, search_state):
        self.process = p
        self.search_state = search_state
    def __str__(self):
        return "Search Party: {}".format(self.process)
    def __repr__(self):
        return "Search Party: {}".format(self.process)


class SearchState():
    def __init__(self, config):
        self.config = config

class LockedList(list):
    def __init__(self, lock, *args):
        list.__init__(self, *args)
        self.lock = lock

def run_monitor(search_parties):
    """
    Kills certain processes
    TODO: modify to accept the number of the process to kill
    """
    while True:
        time.sleep(5)
        cull_parties(search_parties)
        print("Monitor:")
        print_parties(search_parties)


def run_search_party(search_state):
    # Run simulation
    for i in range(50):
        time.sleep(0.5 * random.random())
        (tid, value) = search_state.config
        search_state.config = (tid, value + 1)
        print(search_state.config)

def cull_parties(parties):
    with parties.lock:
        x = parties.pop()
        x.process.terminate()

def print_parties(parties):
    with parties.lock:
        for party in parties:
            print(party)

if __name__ == '__main__':
    num_search_parties = 3
    initial_sys_configs = []
    # Set initial node values  for each search party (each have a copy of the search state)
    for i in range(num_search_parties):
        initial_sys_config = (i, i)
        initial_sys_configs.append(initial_sys_config)

    # Create each search party
    parties = LockedList(Lock())
    for config in initial_sys_configs:
        search_state = SearchState(config)
        p = Process(target=run_search_party, args=(search_state,))
        parties.append(SearchParty(p, search_state))

    # Create monitoring thread
    monitor_thread = Process(target=run_monitor, args=(parties, ))


    # Run search parties
    for party in parties:
        party.process.start()

    print_parties(parties)
    # Run monitor
    monitor_thread.start()

    # Wait until only the monitor process is active
    while True:
        print("Main:")
        print_parties(parties)
        with parties.lock:
            parties_remaining =  map(lambda x: x.process.is_alive(), parties)
        if not any(parties_remaining):
            break
        time.sleep(4)
  
    monitor_thread.terminate()
    print("all done: {}".format(parties))