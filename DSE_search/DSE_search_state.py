import json


from mock_sim import MockSim

class SearchState:
    """
    Parent class for all search state classes.
    Search search comprises:
        fitness function
        most recent simulation results
        most recent fitness value

    Members:
    eval()
        fitness function
    stats
        The most recent simulation statistics
    fitness
        The most recent fitness score  
    """

    def __init__(self):
        pass

    def eval(self, sys_config):
        pass

    def stats_to_json(self):
        """
        Outputs the stats of the simulation with the simulation class name as
        the top level key
        """
        pass

def eval_stats(stats):
    """
    Basic function to minimize
    """
    #TODO:  How to calibrate parameters?
    a = 10e9
    b = 1/(1048576)
    result = a*stats["execution time (s)"] + b*stats["Area (mm2)"]
    
    return result

class MockSearchState(SearchState):
    """
    Parent class for all search state classes.
    Search search comprises:
        fitness function
        most recent simulation results
        most recent fitness value

    Members:
    eval()
        fitness function
    stats
        The most recent simulation statistics
    fitness
        The most recent fitness score  
    """

    def __init__(self, sys_config):
        self.mock_sim = MockSim(sys_config)
        self.stats = {}
        self.fitness = None

    def eval(self, sys_config):
        """
        Runs the simulations and places the statistics in the stats dictionary
        """
        self.mock_sim.set_config(sys_config)

        self.mock_sim.run()
    
        self.stats[self.mock_sim.__class__.__name__] = self.mock_sim.stats
        self.fitness = eval_stats(self.mock_sim.stats)

        return self.fitness

    def stats_to_json(self):
        return json.dumps(self.stats, sort_keys=True, indent=4)
