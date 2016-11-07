#!/usr/bin/python3

def gen_cache_config(template, output_file, cache_size):
    with open(template, 'r') as f_in, open(output_file, 'w') as f_out:
        config = f_in.read()
        config = config.replace("$CACHE_SIZE", str(cache_size))
        f_out.write(config)

def main():
    gen_cache_config("cache_template.cfg", "new_config.cfg", 2097152)

if __name__ == "__main__":
    main()
