from common.company import standardize_company_name


def test_basic_suffix_removal():
    assert standardize_company_name("Example Inc") == "Example"
    assert standardize_company_name("Test LLC") == "Test"
    assert standardize_company_name("Sample Ltd") == "Sample"

def test_suffix_with_punctuation():
    assert standardize_company_name("Example Inc.") == "Example"
    assert standardize_company_name("Test, LLC") == "Test"
    assert standardize_company_name("Sample Ltd.") == "Sample"

def test_multiple_suffixes():
    assert standardize_company_name("Example Inc LLC") == "Example"
    assert standardize_company_name("Test Pvt Ltd") == "Test"

def test_suffix_with_website_info():
    assert standardize_company_name("Example Inc https://example.com") == "Example"
    assert standardize_company_name("Test LLC www.test.com") == "Test"
    assert standardize_company_name("Sample Ltd example.net") == "Sample"

def test_removal_of_special_characters():
    assert standardize_company_name("Example-Inc") == "Example"
    assert standardize_company_name("Test|LLC") == "Test"
    assert standardize_company_name("Sample, Ltd.") == "Sample"

def test_handling_extra_spaces():
    assert standardize_company_name("  Example   Inc  ") == "Example"
    assert standardize_company_name("  Test    LLC  ") == "Test"
    assert standardize_company_name("Sample  Ltd  ") == "Sample"

def test_ensuring_capitalization():
    assert standardize_company_name("example inc") == "Example"
    assert standardize_company_name("test llc") == "Test"
    assert standardize_company_name("sample ltd") == "Sample"

def test_handling_of_mixed_cases():
    assert standardize_company_name("eXamPle inc") == "Example"
    assert standardize_company_name("TesT LLc") == "Test"
    assert standardize_company_name("SaMpLe LtD") == "Sample"

def test_multi_word_company_names():
    assert standardize_company_name("Example Technologies Inc") == "Example Technologies"
    assert standardize_company_name("Advanced Solutions LLC") == "Advanced Solutions"
    assert standardize_company_name("Creative Labs Ltd.") == "Creative Labs"
    assert standardize_company_name("Innovative Systems Incorporated") == "Innovative Systems"
    assert standardize_company_name("Global Enterprises LLC") == "Global Enterprises"

def test_multi_word_company_names_with_punctuation():
    assert standardize_company_name("Example Technologies, Inc.") == "Example Technologies"
    assert standardize_company_name("Advanced Solutions - LLC") == "Advanced Solutions"
    assert standardize_company_name("Creative Labs | Ltd.") == "Creative Labs"
    assert standardize_company_name("Innovative Systems, Incorporated") == "Innovative Systems"
    assert standardize_company_name("Global Enterprises LLC.") == "Global Enterprises"

def test_multi_word_company_names_with_website_info():
    assert standardize_company_name("Example Technologies Inc https://example.com") == "Example Technologies"
    assert standardize_company_name("Advanced Solutions LLC www.advanced.com") == "Advanced Solutions"
    assert standardize_company_name("Creative Labs Ltd creativelabs.net") == "Creative Labs"
    assert standardize_company_name("Innovative Systems Incorporated innovative.org") == "Innovative Systems"
    assert standardize_company_name("Global Enterprises LLC global-enterprises.com") == "Global Enterprises"

def test_international_names():
    # assert standardize_company_name("株式会社Example") == "Example"
    # assert standardize_company_name("Example有限公司") == "Example"
    assert standardize_company_name("Example 주식회사") == "Example"
    assert standardize_company_name("Test GmbH") == "Test"
    assert standardize_company_name("Example OY") == "Example"
    assert standardize_company_name("Test AB") == "Test"
