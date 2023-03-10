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
            rv = test_client.get("/aim_services/inbound")
            code = rv.status
            print(rv.json)
            self.assertEqual("200 OK", code)

    def test_sales_success(self):
        with local.app.test_client() as test_client:
            payload = get_message('fixture_files/pos_sales.json')
            headers = json.loads(os.environ.get("header_string"))
            rv = test_client.post("/aim_services/inbound", json=payload, headers=headers)
            code = rv.status
            print(rv.json)
            self.assertEqual("202 ACCEPTED", code)


if __name__ == '__main__':
    unittest.main()
