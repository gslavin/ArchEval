#! /bin/bash

test_script() {
    ./"$1" &> /dev/null || echo "Test Failed! $1"
}

test_script gem5_stat_parser.py
test_script mcpat_stat_parser.py
test_script simulation_wrappers.py
test_script validate_json.py
