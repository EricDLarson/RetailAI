#!/usr/bin/python3

# command line test for search.py GCF

from unittest.mock import Mock

import autocomplete

data = {"q": "cat"}
req = Mock(get_json=Mock(return_value=data), args=data)

result = autocomplete.complete(req)
print(result)
