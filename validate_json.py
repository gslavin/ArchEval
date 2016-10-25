#!/usr/bin/python3

import json
import glob

def check_json_file(filename):
    with open(filename, "r") as f:
        try:
            json.loads(f.read())
        except ValueError:
            print("{} is invalid json".format(filename))

def main():
    files = glob.glob("DataFormats/*.json")
    for filename in files:
        check_json_file(filename)

if __name__ == "__main__":
  main()
