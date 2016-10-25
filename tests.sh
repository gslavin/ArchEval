#! /bin/bash

test_script() {
    ./"$1" &> /dev/null || echo "Test Failed! $1"
}

test_script SimulationWrappers/gem5_sim.py
test_script SimulationWrappers/mcpat_sim.py
test_script SimulationWrappers/simulation_wrappers.py
test_script validate_json.py
