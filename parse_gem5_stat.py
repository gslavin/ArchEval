import string
import re
import json

def parse_gem5_stat_file(filename):
    """
    Parses the gem5 stat.txt file and returns the
    indicated fields.  Currently only works for
    op classes
    """
    with open(filename, 'r') as f:
        stats = {'op_class':{}}
        params = ['op_class']
        for line in f:
            # strip out comment
            line = line.split("#")[0].strip()
            #Split into fields
            fields = re.split(' +', line)
            name = fields[0]

            # Get class, field names, and field values
            if any(x in name for x in params):
                key = re.split('[.:]+', name)[2]
                var = re.split('[.:]+', name)[3]
                val = fields[1]
                stats[key][var] = val
    return stats

def main():
    filename = "stats.txt"
    stats = parse_gem5_stat_file(filename)
    f = open("src.json", 'w')
    f.write(json.dumps(stats, sort_keys=True, indent=4))

if __name__ == "__main__":
  main()
