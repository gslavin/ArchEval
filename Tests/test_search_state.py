#!/usr/bin/python3

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
        mock.eval(sys_config)

    @log_name
    def test_stats_to_json(self):
        sys_config = {"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}
        mock = MockSearchState({}, {})
        mock.eval(sys_config)
        logging.info(mock.stats_to_json())

    @log_name
    def test_generate_job_output(self):
        sys_config = {"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}
        mock = MockSearchState({}, {})
        mock.eval(sys_config)
        logging.info(mock.generate_job_output())

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name = script_name.split(".")[0]
    logging.basicConfig(filename=defs.LOG_DIR + '/{}.log'.format(script_name), level=logging.INFO)
    logging.info("START {} TESTS: {:%Y-%m-%d %H:%M:%S}".format(script_name, datetime.datetime.now()))
    unittest.main()
