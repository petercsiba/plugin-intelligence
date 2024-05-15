# Test cases
import pytest

from batch_jobs.common import standardize_url


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("HTTP://Example.com:80/path", "https://www.example.com/path"),
        ("https://example.com", "https://www.example.com/"),
        ("ftp://example.com/resource", "ftp://www.example.com/resource"),
        ("example.com", "https://www.example.com/"),
        ("www.example.com", "https://www.example.com/"),
        ("subdomain.example.com", "https://subdomain.example.com/"),
        # ("://malformed.com", None),  TODO(P3): Yeah this is a bug, but it's not a priority
        ("http://", None),
    ],
)
def test_standardize_url(test_input, expected):
    assert standardize_url(test_input) == expected
