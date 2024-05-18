from api.utils import parse_fuzzy_list


def test_parse_fuzzy_list_valid_list_string():
    assert parse_fuzzy_list("[1, 2, 3]") == ['1', '2', '3']
    assert parse_fuzzy_list("['apple', 'banana', 'cherry']") == ['Apple', 'Banana', 'Cherry']

def test_parse_fuzzy_list_malformed_string():
    assert parse_fuzzy_list("apple, banana, cherry") == ['Apple', 'Banana', 'Cherry']
    assert parse_fuzzy_list("apple, banana, [cherry]") == ['Apple', 'Banana', '[cherry]']

def test_parse_fuzzy_list_empty_string():
    assert parse_fuzzy_list("") == []

def test_parse_fuzzy_list_none():
    assert parse_fuzzy_list(None) == None

def test_parse_fuzzy_list_max_elements():
    assert parse_fuzzy_list("[1, 2, 3, 4]", max_elements=2) == ['1', '2']
    assert parse_fuzzy_list("apple, banana, cherry", max_elements=2) == ['Apple', 'Banana']

def test_parse_fuzzy_list_with_quotes():
    assert parse_fuzzy_list('["apple", "banana", "cherry"]') == ['Apple', 'Banana', 'Cherry']
    assert parse_fuzzy_list("['apple', 'banana', 'cherry']") == ['Apple', 'Banana', 'Cherry']
    assert parse_fuzzy_list("'apple', 'banana', 'cherry'") == ['Apple', 'Banana', 'Cherry']
    assert parse_fuzzy_list("""["'AWS'", "'IAM'", "'Switch Roles'", "'SSO'", "'SAML'"]""", max_elements=2) == ['AWS', 'IAM']

def test_parse_fuzzy_list_with_extra_characters():
    assert parse_fuzzy_list("apple*, banana*, cherry*") == ['Apple', 'Banana', 'Cherry']
    assert parse_fuzzy_list(" apple , banana , cherry ") == ['Apple', 'Banana', 'Cherry']
