#!/usr/bin/python3

from abc import ABCMeta, abstractmethod
import json

class SimWrap(metaclass=ABCMeta):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    def __init__(self):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """
        self.stats = None
        pass

    @abstractmethod
    def run(self):
        """
        Run the simulation
        Store statistics
        """

    def stats_to_json(self):
        return json.dumps(self.stats, sort_keys=True, indent=4)


def main():
    pass

if __name__ == "__main__":
    main()
