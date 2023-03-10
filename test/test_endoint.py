import unittest
import main as local
import tracemalloc
import json
import os
import warnings
from support import get_message

tracemalloc.start()


class TestScan(unittest.TestCase):

    def setUp(self) -> None:
        local.app.testing = True

    def test_get_success(self):
        with local.app.test_client() as test_client:
            rv = test_client.get("/orders")
            code = rv.status
            print(rv.json)
            self.assertEqual("200 OK", code)


if __name__ == '__main__':
    unittest.main()
