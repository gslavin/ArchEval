import csv

with open('out.csv', 'r') as csvfile:
    mcpat_data = csv.reader(csvfile, delimiter=',')
    names = next(mcpat_data)
    # Strip out whitespace and null ending entry
    names = list(filter(lambda x: x, map(lambda x: x.strip(), names)))
    data = dict((name, []) for name in names)
    for line in mcpat_data:
        for (name, entry) in zip(names, line):
            data[name].append(entry)
    for key in ["Area (mm2)", "Dynamic read energy (nJ)", "Dynamic write energy (nJ)"]:
        print("{0}: {1}".format(key, str(data[key])))

