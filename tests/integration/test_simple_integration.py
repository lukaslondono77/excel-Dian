"""
Simple integration tests that don't require any external services.
"""

import pytest


def test_simple_integration():
    """Simple test to verify integration test framework works."""
    assert True


def test_basic_math():
    """Basic test to verify pytest is working."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    assert "hello" + " " + "world" == "hello world"


def test_list_operations():
    """Test list operations."""
    test_list = [1, 2, 3]
    test_list.append(4)
    assert len(test_list) == 4
    assert test_list == [1, 2, 3, 4]


def test_dict_operations():
    """Test dictionary operations."""
    test_dict = {"key1": "value1"}
    test_dict["key2"] = "value2"
    assert len(test_dict) == 2
    assert test_dict["key1"] == "value1"
    assert test_dict["key2"] == "value2"
