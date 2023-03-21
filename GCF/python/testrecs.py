#!/usr/bin/python3

# Command line test for recommendion.py GCF

from unittest.mock import Mock

import recommendation

def test_recommendation():
    data = {"visitorid": "goo", "productid": "12345"}
    req = Mock(get_json=Mock(return_value=data), args=data)

    result = recommendation.recommend(req)
    print(result)

test_recommendation()
