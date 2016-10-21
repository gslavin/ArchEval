#! /bin/sh

test_script() {
    python $1 &> /dev/null || echo "Test Failed! $1"
}

test_script parse_mcpat_csv.py
test_script parse_gem5_stat.py
