#!/usr/bin/python3

# command line test for search.py GCF

from unittest.mock import Mock

import search

data = {"visitorid": "fakevisitorid", "productid": "12345"}
req = Mock(get_json=Mock(return_value=data), args=data)

result = search.search(req)
print(result)
