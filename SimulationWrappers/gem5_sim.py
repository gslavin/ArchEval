#!/usr/bin/python3

#from simulation_wrapper import SimWrap

import string
import re
import json
import copy 

class Gem5Sim():
    """
    self.config
        simulation configuration
    self.stats ## dict of information 
        simulation results
    """

    def __init__(self):
        """
        Pass in dictionary of simulation parameters // Expecting a list preferrably
        Store configuration of simulation
        """
        ## self.validate_params(params)
        ## self.config = params
        pass

    def validate_params(self, params):
        """valid_params = [ "cpu_count", "cpu_frequency", "cache_size"]
        if not all(k in valid_params for k in params.keys()):
            raise ValueError("Not a valid gem5 config parameter")
        """
        pass
    
    def update_dict(self, d, value):
      temp = {}
      found = None
      if(value[1].isdigit() == False and 
          value[1] != 'nan' and
          '.' not in value[1]):
      
        for i in d['substat']:
          if(i['stat'] == value[0]):
            found = i
            break
      
        if (found == None):
          temp['stat'] = value[0]
          temp['substat'] = []
          d['substat'].append((temp))
          self.update_dict(temp, value[1:])
        else:
          self.update_dict(found, value[1:])
        '''
        temp['stat'] = value[0]
        temp['substat'] = []
        d['substat'].append((temp))
        self.update_dict(temp, value[1:])
        '''
      else: #base case
        temp['stat'] = value[0]
        temp['value'] = value[1]
        d['substat'].append((temp))
      
      return d
        
       

    def parse_stat_file(self, filename):
        """
        Parses the gem5 stat.txt file and returns the
        indicated fields.  Currently only works for
        op classes
        """
        master = []
        temp = {}
        with open(filename, 'r') as f:
            next(f)
            next(f)
            for line in f:
              # strip out comment
              line = line.split("#")[0].strip()
              #Split into fields
              fields = re.split('[ ]+', line)
              fields = re.split('[.:]+', fields[0]) + fields[1:]

              if fields[0] == '':
                break
              
              found = None
              if len(fields) == 2:
                temp['stat'] = fields[0]
                temp['value'] = fields[-1]
                master.append(copy.copy(temp))
                temp.clear();
              
              else:
                for i in master:
                  if i['stat'] == fields[0]:
                    found = i
                    master.remove(i)
                    break

                if (found == None):    
                  temp['stat'] = fields[0]
                  temp['substat'] = []
                  master.append(copy.copy(self.update_dict(temp, fields[1:])))
                else:
                  master.append((self.update_dict(found, fields[1:])))

        return master

    def run_simulation(self):
        pass

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.run_simulation()

        # Collect the statistics
        filename = "stats.txt"
        self.stats = parse_stat_file(filename)

def main():
    sim = Gem5Sim()
    sim.parse_stat_file("stats.txt")
    ##sim.run()
    ##print(sim.stats_to_json())

if __name__ == "__main__":
    main()
