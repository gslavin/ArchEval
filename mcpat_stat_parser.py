#!/usr/bin/python3
import csv

def parse_mcpat_csv(filename):
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

def main():
    # Extract specific fields
    fields = ["Area (mm2)", "Dynamic read energy (nJ)", "Dynamic write energy (nJ)"]
    data = parse_mcpat_csv('out.csv')
    for key in fields:
        print("{0}: {1}".format(key, str(data[key])))

if __name__ == "__main__":
    main()
