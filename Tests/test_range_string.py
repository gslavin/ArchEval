#!/usr/bin/env python3

import datetime
import logging
import unittest
import os
import defs

from range_string import RangeString
from test_utils import log_name

class TestRangeString(unittest.TestCase):

    @log_name
    def test_invalid(self):
        tests = [ "invalid",
                  "(32, 43)blah",
                  "blah(32, 43)",
                  "(32, 43",
                  "32, 42",
                  "{32, 42}",
                  "[12, 11]",
                  "(12, 12)",
                  "[12, 12)",
                  "(12, 12]"
                ]
        
        for test_case in tests:
            with self.assertRaises(ValueError):
                rs = RangeString(test_case)

    @log_name
    def test_ranges(self):
        test_within = { "(-inf, inf)":  [-500, 0, 1234],
                        "(-inf, 0]":    [-1234, -500, 0],
                        "(-1, 1]":      [-0.999, -0.0001, 0.0, 0.0001, 0.999, 1.0],
                        "[1.0, inf)":   [1.000, 1.0001, 500.123, 9999.999]
                      }
        test_not_within = { "(-inf, inf)":  [float("-inf"), float("inf")],
                            "(-inf, 0]":    [0.0001, 10000],
                            "(-1, 1]":      [-500.0, -1.000, 1.0001],
                            "[1.0, inf)":   [-5000, 0.0, 0.9999]
                          }

        for test_string in test_within.keys():
            rs = RangeString(test_string)

            for test_case in test_within[test_string]:
                self.assertTrue(rs.in_range(test_case))


        for test_string in test_not_within.keys():
            rs = RangeString(test_string)

            for test_case in test_not_within[test_string]:
                self.assertFalse(rs.in_range(test_case))

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name = script_name.split(".")[0]
    logging.basicConfig(filename = defs.LOG_DIR + '/{}.log'.format(script_name),  level = logging.INFO)
    logging.info("START {} TESTS: {:%Y-%m-%d %H:%M:%S}".format(script_name, datetime.datetime.now()))
    unittest.main()
    logging.info("END {} TESTS".format(script_name))
