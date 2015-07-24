#! /usr/bin/python

import unittest

def pretty_print(gen):
    for line in gen:
        print line

class APITestCase(unittest.TestCase):

    def setUp(self):
        import requests
        self.requests = requests
        self.requests.configure('******', '********')

    def test_configure(self):
        self.assertEqual(self.requests.ACCESS_KEY, '****')

    def test_api(self):
        import apibus

        fetcher = apibus.APIFetcher()
        with fetcher.set_args(service = 'http', date = '2015-07-25', fop = 'grep/socket'):
            pretty_print(fetcher.get_log(ident = '1-debug'))

if __name__ == '__main__':
    unittest.main()