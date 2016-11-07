#!/usr/bin/python3

from simulation_wrapper import SimWrap
import subprocess
import csv

def parse_csv(filename):
    """
    Parse the output csv for the mcpat simulator.
    This
    """
    with open(filename, 'r') as csvfile:
        mcpat_data = csv.reader(csvfile, delimiter=',')

        # Get field name row
        names = next(mcpat_data)
        # Strip out whitespace and null ending entry
        names = list(filter(lambda x: x, map(lambda x: x.strip(), names)))

        data = dict((name, []) for name in names)
        for line in mcpat_data:
            for (name, entry) in zip(names, line):
                data[name].append(entry)

        return data

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

    def run_simulation(self, output_csv):
        #TODO: have better error handling for cacti call
        subprocess.check_call("./cacti/cacti -infile cache_config.cfg -outfile {0}".format(output_csv), shell=True)

    def gen_cache_config_file(self, template, output_file):
        cache_size = self.config["cache_size"]
        with open(template, 'r') as f_in, open(output_file, 'w') as f_out:
            config = f_in.read()
            config = config.replace("$CACHE_SIZE", str(cache_size))
            f_out.write(config)

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.gen_cache_config_file("./cacti/cache_template.cfg", "cache_config.cfg")

        output_csv = "results.csv"
        self.run_simulation(output_csv)

        # Collect the statistics
        self.stats = parse_csv(output_csv)
        fields = ["Area (mm2)", "Dynamic read energy (nJ)", "Dynamic write energy (nJ)"]
        # Mcpat csv can store the restores of multiple runs.  So each field will
        # have a list of values.  Only take the final value
        last = len(self.stats[fields[0]]) - 1
        self.stats = { key: self.stats[key][last] for key in fields }

def main():
    sim = McPatSim({"cache_size" : 2048})
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
