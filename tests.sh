#! /bin/bash

test_script() {
    ./"$1" &> /dev/null || echo "Test Failed! $1"
}

export PYTHONPATH=${PYTHONPATH}:${PWD}/SimulationWrappers:${PWD}/DSE_search

make all

if [ ! -d _TestOut ]; then
    mkdir _TestOut
fi

./Tests/test_sim_wrappers.py

./Tests/test_searcher.py

# TODO:  Remove these tests when they are all replaced by unit tests
test_script SimulationWrappers/gem5_sim.py
test_script SimulationWrappers/simulation_wrapper.py
test_script DSE_search/DSE_searcher.py
test_script validate_json.py
