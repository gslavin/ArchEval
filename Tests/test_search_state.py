#!/usr/bin/env python3


import datetime
import logging
import unittest
import os
import defs

from DSE_search_state import MockSearchState
from test_utils import log_name

class TestSearcher(unittest.TestCase):
    @log_name
    def test_defaults(self):
        sys_config = {"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}
        mock = MockSearchState({}, {})
        mock.eval_fitness(sys_config)

    @log_name
    def test_stats_to_json(self):
        sys_config = {"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}
        mock = MockSearchState({}, {})
        mock.eval_fitness(sys_config)
        logging.info(mock.stats_to_json(sys_config))

    @log_name
    def test_generate_job_output(self):
        sys_config = {"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}
        mock = MockSearchState({}, {})
        mock.eval_fitness(sys_config)
        logging.info(mock.generate_job_output([sys_config]))

    @log_name
    def test_constraints(self):
        C = { "Area (mm2)": "[1048576, 1048576]",
              "execution time (s)": "(0.0, 2.00e-11)"
            }
        mock = MockSearchState(C, {})
        sys_config = {"cache_size": 1024, "cpu_frequency" : 7e9, "cpu_count" : 7}
        fitness = mock.eval_fitness(sys_config)
        logging.info(mock.stats_to_json(sys_config))
        self.assertTrue(fitness < float("inf"))

        C = { "Area (mm2)": "(-inf, 1048575]" }
        mock = MockSearchState(C, {})
        fitness = mock.eval_fitness(sys_config)
        self.assertTrue(fitness == float("inf"))

        C = { "execution time (s)": "(0.0, 1.99e-11]" }
        mock = MockSearchState(C, {})
        fitness = mock.eval_fitness(sys_config)
        self.assertTrue(fitness == float("inf"))

        C = { "Area (mm2)": "(-inf, 1048575]",
              "execution time (s)": "(0.0, 1.99e-11)"
            }
        mock = MockSearchState(C, {})
        fitness = mock.eval_fitness(sys_config)
        self.assertTrue(fitness == float("inf"))

    @log_name
    def test_memoization(self):
        """
        Tests that redundant simulations aren't run

        """
        def call_once(f):
            def one_time_f():
                if not hasattr(one_time_f, "called"):
                    one_time_f.called = True
                else:
                    raise ValueError()
                return f()
            return one_time_f

        mock = MockSearchState({}, {})
        mock.sims[0].run = call_once(mock.sims[0].run)

        sys_config = {"cache_size": 1024, "cpu_frequency" : 7e9, "cpu_count" : 7}
        expected_fitness = mock.eval_fitness(sys_config)
        # The simulation should not be called again or the call_once
        # wrapper will throw an exception
        fitness = mock.eval_fitness(sys_config)

        self.assertTrue(expected_fitness, fitness)

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name = script_name.split(".")[0]
    logging.basicConfig(filename=defs.LOG_DIR + '/{}.log'.format(script_name), level=logging.INFO)
    logging.info("START {} TESTS: {:%Y-%m-%d %H:%M:%S}".format(script_name, datetime.datetime.now()))
    unittest.main()
