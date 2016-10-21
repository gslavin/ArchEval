from abc import ABCMeta, abstractmethod

class SimWrap(metaclass=ABCMeta):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    @abstractmethod
    def __init__(self):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """
        pass

    @abstractmethod
    def run(self):
        """
        Run the simulation
        Store statistics
        """

class Gem5Sim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    def __init__(self, params):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """
        self.config = params

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.stats = None

class McPatSim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    def __init__(self, params):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """
        self.validate_params(params)
        self.config = params

    def validate_params(self, params):
        valid_params = ["cache_size"]
        if not all(k in valid_params for k in params.keys()):
            raise ValueError("Not a valid McPAT config parameter")

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.stats = None

def main():
    Gem5Sim({"freq" : 100})
    McPatSim({"cache_size" : 2048})

if __name__ == "__main__":
    main()
