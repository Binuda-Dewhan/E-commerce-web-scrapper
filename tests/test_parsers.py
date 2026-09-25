import pytest
from app.utils.parsers import parse_price, parse_rating, parse_review_count

def test_parse_price():
    assert parse_price("$1,299.00") == 1299.0
    assert parse_price("$999") == 999.0
    assert parse_price("") is None
    assert parse_price(None) is None
    assert parse_price("N/A") is None
    assert parse_price("$1,299.00 - $1,499.00") == 1299.0
    assert parse_price("Current price is $45.99") == 45.99

def test_parse_rating():
    assert parse_rating("4.6 out of 5 stars") == 4.6
    assert parse_rating("4.6") == 4.6
    assert parse_rating("4") == 4.0
    assert parse_rating("") is None
    assert parse_rating(None) is None
    assert parse_rating("No ratings") is None

def test_parse_review_count():
    assert parse_review_count("1,245 ratings") == 1245
    assert parse_review_count("(1,245)") == 1245
    assert parse_review_count("5") == 5
    assert parse_review_count("") is None
    assert parse_review_count(None) is None
    assert parse_review_count("No reviews yet") is None
