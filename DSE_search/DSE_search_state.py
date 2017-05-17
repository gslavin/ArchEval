import json
import datetime
import defs
import logging

"""
The search algorithm expects the user to provide a fitness function.
This fitness function runs simulations using the simulation wrappers
in order to determine the score for each node.

After the search is finished, the visualization platform needs the following
to display meaningful results:
    user_constraints
    system_configuration of the final arch
    simulation results of the final arch

This information is recorded by the SearchState class
while the search program operates using the SearchState's
fitness function.

After the search is finished, the SearchState class is
used to generate the job_output.json file that is sent
to the visualization platform.
"""

from mock_sim import MockSim
from gem5_sim import Gem5Sim
from gem5_fs_sim import Gem5FSSim
from mcpat_sim import McPatSim
from range_string import RangeString

def dict_to_key(d):
    """
    NOTE: This doesn't work for nested dicts
    """
    return tuple(sorted(d.items()))


class SearchState:
    """
    Parent class for all search state classes.
    Search comprises:
        fitness function
        most recent simulation results
        most recent fitness value

    Members:
        eval_fitness()
            Applies fitness func to current sys_config and records the stats
            for the current sys_config in self.stats.
        stats
            A dictionary of sys_config -> stats
        fitness
            The most recent fitness score
    """

    def __init__(self, constraints, benchmark, options):

        if (not isinstance(constraints, dict)):
            raise ValueError("Parameter ranges takes the form of a dictionary.")

        self.constraints = {}
        for key in constraints.keys():
            self.constraints[key] = RangeString(constraints[key])

        pass

    def eval_fitness(self, sys_config):
        """
        Runs the simulations and places the statistics in the stats dictionary
        """
        # Replace the old system configuration
        self.sys_config = sys_config

        # Reset fitness value
        self.fitness = 0
        # Don't run repeat simulations (just reuse results)
        if not dict_to_key(sys_config) in self.stats.keys():
            # initialize sub dictionary if it doesn't already
            # exist
            self.stats[dict_to_key(sys_config)] = {}
            for sim in self.sims:
                sim.set_config(self.sys_config)
                sim.run()
                # For each sys_config, each simulation_wrapper has a dictionary of stats.
                self.stats[dict_to_key(sys_config)][sim.__class__.__name__] = sim.stats

        for sim in self.sims:
            # We need to search the stats of the current simulation
            # runs for constraint violations
            sim_stats = self.stats[dict_to_key(sys_config)][sim.__class__.__name__]
            for stat in self.constraints.keys():
                # TODO: need translation from abstract constraint name -> simulator stat name
                if stat in sim_stats:
                    stat_value = sim_stats[stat]
                    if (not self.constraints[stat].in_range(stat_value)):
                        self.fitness = float("inf")
                else:
                    logging.warning("Stat not found: {}".format(stat))

        if self.fitness != float("inf"):
            all_stats = {}
            for sim in self.sims:
                all_stats.update(sim.stats)
            self.fitness = self.fitness_func(all_stats)

        return self.fitness

    def stats_to_json(self, sys_config):
        """
        Outputs the stats of the simulation with the simulation class name as
        the top level key
        """
        return json.dumps(self.stats[dict_to_key(sys_config)], sort_keys=True, indent=4)


    def generate_job_output(self, sys_configs):
        job_output = {}

        job_output["job_name"] = "Mock Test"
        job_output["job_timestamp"] = "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())
        job_output["constraints"] = self.constraints
        job_output["search_parties"] = []
        for sys_config in sys_configs:
            search_party = {}
            search_party["system_configuration"] = sys_config
            search_party["simulation_results"] = self.stats[dict_to_key(sys_config)]
            job_output["search_parties"].append(search_party)

        return json.dumps(job_output, sort_keys=True, indent=4)

"""
Default MockSim class
"""
def mock_eval_stats(stats):
    """
    Basic function to minimize for the Mock Simulator
    """
    #TODO:  How to calibrate parameters?
    a = 10e9
    b = 1/(1048576)
    result = a*stats["execution time (s)"] + b*stats["Area (mm2)"]

    return result

class MockSearchState(SearchState):
    """
    Parent class for all MockSim classes. Child classes will set set a
        different fitness_func.

    Members:
        eval_fitness()
            Applies fitness func to current sys_config and records the stats
            for the current sys_config in self.stats.
        mock_sim
            Wrapper class used to interface to the MockSim
        stats
            A dictionary of sys_config -> stats
        fitness
            The most recent fitness score
        fitness_func
            Heuristic used to the performance of each system configuration
    """

    def __init__(self, constraints, sys_config, benchmark, options, fitness_func = mock_eval_stats):
        """
        Each search party has ONE fitness function and ONE set of simulation wrappers,
        But each sys_config has its own set of associated stats. Every (sys_config, stats) pair that is generated by
        eval_fitness() is perserved in self.stats.  At the end of the search, the output statistics for the winning
        sys_config are retreived by passing the winning sys_config to generate_job_output(sys_config)
        """

        super().__init__(constraints, benchmark, options)
        self.sims = [MockSim(sys_config)]
        self.stats = {}
        self.fitness = None
        self.fitness_func = fitness_func

"""
Embedded MockSim Class
"""

def eval_embedded(stats):
    m = [4.7721E6, 1.7763E3, 1.7763E3, 1.0427E-10]
    s = [1.0044E7, 1.2847E3, 1.2847E3, 1.2395E-10]
    w = [2, 1, 1, 10]

    result = ((stats["Area (mm2)"] - m[0]) / s[0] * w[0]) \
           + ((stats["Dynamic read energy (nJ)"] - m[1]) / s[1] * w[1]) \
           + ((stats["Dynamic write energy (nJ)"] - m[2]) / s[2] * w[2]) \
           + ((stats["execution time (s)"] - m[3]) / s[3] * w[3])

    return result

class EmbeddedSearchState(MockSearchState):
    """
    Creates a MockSearchState instance that uses a fitness function
    specialized for embedded applications
    """

    def __init__(self, constraints, sys_config, benchmark, options):
        super().__init__(constraints, sys_config, benchmark, options, eval_embedded)


"""
Balanced MockSim Class
"""

def eval_balanced(stats):
    m = [4.7721E6, 1.7763E3, 1.7763E3, 1.0427E-10]
    s = [1.0044E7, 1.2847E3, 1.2847E3, 1.2395E-10]
    w = [1, 1, 1, 1]

    result = ((stats["Area (mm2)"] - m[0]) / s[0] * w[0]) \
           + ((stats["Dynamic read energy (nJ)"] - m[1]) / s[1] * w[1]) \
           + ((stats["Dynamic write energy (nJ)"] - m[2]) / s[2] * w[2]) \
           + ((stats["execution time (s)"] - m[3]) / s[3] * w[3])

    return result


class BalancedSearchState(MockSearchState):
    """
    Creates a MockSearchState instance that uses a fitness function
    specialized for balanced applications
    """

    def __init__(self, constraints, sys_config, benchmark, options):
        super().__init__(constraints, sys_config, benchmark, options, eval_balanced)

"""
High performance MockSim Class
"""
def eval_high_performance(stats):
    m = [4.7721E6, 1.7763E3, 1.7763E3, 1.0427E-10]
    s = [1.0044E7, 1.2847E3, 1.2847E3, 1.2395E-10]
    w = [10, 10, 10, 1]

    result = ((stats["Area (mm2)"] - m[0]) / s[0] * w[0]) \
           + ((stats["Dynamic read energy (nJ)"] - m[1]) / s[1] * w[1]) \
           + ((stats["Dynamic write energy (nJ)"] - m[2]) / s[2] * w[2]) \
           + ((stats["execution time (s)"] - m[3]) / s[3] * w[3])

    return result

class HighPerformanceSearchState(MockSearchState):
    """
    Creates a MockSearchState instance that uses a fitness function
    specialized for high performance applications
    """

    def __init__(self, constraints, sys_config, benchmark, options):
        super().__init__(constraints, sys_config, benchmark, options, eval_high_performance)

def eval_temp(stats):
    features = ["sim_seconds", "Area (mm2)", "Dynamic read energy (nJ)"]
    m = [7.2927E-04, 0.0702, 0.0308]
    s = [6.7216e-05, 0.0323, 0.001]
    w = [50, 5, 1]

    result = 0

    for i in range(len(features)):
        result += ((float(stats[features[i]]) - m[i]) / s[i]) * w[i]

    return result

def eval_demo(stats):
    features = ["sim_seconds", "Area (mm2)", "Dynamic read energy (nJ)"]
    m = [2.1969E-04, 0.0861, 0.0312]
    s = [9.7346E-06, 0.0318, 8.1234e-04]
    w = [50, 5, 1]

    result = 0

    for i in range(len(features)):
        result += ((float(stats[features[i]]) - m[i]) / s[i]) * w[i]

    return result


"""
Full search state incorporating all included simulators.
"""
class FullSearchState(SearchState):

    def __init__(self, constraints, benchmark, options, fitness_func = eval_temp):
        super().__init__(constraints, benchmark, options)
        self.sims = [Gem5Sim(benchmark, options), McPatSim()]
        self.stats = {}
        self.fitness = None
        self.fitness_func = fitness_func


"""
Default McPAT class
"""
def mcpat_eval_stats(stats):
    """
    Basic function to minimize for the McPAT simulator
    """
    #TODO:  How to calibrate parameters?
    a = 1
    b = 1
    c = 1
    result = a*float(stats["Area (mm2)"]) + \
             b*float(stats["Dynamic read energy (nJ)"]) + \
             c*float(stats["Dynamic write energy (nJ)"])

    return result

class McPatSearchState(SearchState):
    """
    Parent class for all McPatSim classes. Child classes will set set a
        different fitness_func.
    """

    def __init__(self, constraints, benchmark, options, fitness_func = mcpat_eval_stats):
        super().__init__(constraints, benchmark, options)
        self.sims = [McPatSim()]
        self.stats = {}
        self.fitness = None
        self.fitness_func = fitness_func

class Gem5FSSearchState(SearchState):
    
    def __init__(self, constraints, benchmark, options, kernel, disk_image, fitness_func = eval_temp):
        super().__init__(constraints, benchmark, options)
        self.sims = [Gem5FSSim(benchmark, options, kernel, disk_image), McPatSim()]
        self.stats = {}
        self.fitness = None
        self.fitness_func = fitness_func
