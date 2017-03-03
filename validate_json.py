#!/usr/bin/env python3

import json
import glob
import sys

def check_json_file(filename):
    with open(filename, "r") as f:
        try:
            text = json.load(f)
            print(text)
        except ValueError:
            print("{} is invalid json".format(filename))
            exit(1)

def main():
    if len(sys.argv) == 2:
        check_json_file(sys.argv[1])
    else:
        files = glob.glob("DataFormats/*.json")
        for filename in files:
            check_json_file(filename)

if __name__ == "__main__":
  main()
