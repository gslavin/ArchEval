#!/usr/bin/python3

import subprocess

def gen_cache_config(template, output_file, cache_size):
    with open(template, 'r') as f_in, open(output_file, 'w') as f_out:
        config = f_in.read()
        config = config.replace("$CACHE_SIZE", str(cache_size))
        f_out.write(config)

def run_cacti():
    return_code = subprocess.call("./cacti -infile new_config.cfg -outfile results.csv", shell=True)  
    if (return_code != 0):
        raise ValueError("cacti failed!")

def main():
    run_cacti()

if __name__ == "__main__":
    main()
