#!/usr/bin/python3

import unittest

from DSE_searcher import DSE_searcher

class TestSearcher(unittest.TestCase):
    def test_defaults(self):
        s = DSE_searcher(None, {})
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])

    def test_more_seeds(self):
        s = DSE_searcher(None, {}, num_search_parties = 2)
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])

    def test_min_start(self):
        s = DSE_searcher(None, {})
        s.sys_configs = [{"cache_size": 2**10, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])
        
    def test_max_start(self):
        s = DSE_searcher(None, {})
        s.sys_configs = [{"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}]
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            s = DSE_searcher(None, [])

        with self.assertRaises(ValueError):
            s = DSE_searcher(None, {}, num_search_parties = -1)

        with self.assertRaises(ValueError):
            s = DSE_searcher(None, {}, max_iterations = -1)

if __name__ == '__main__':
    unittest.main()
