import os

from batch_jobs.gpt.revenue_estimator import extract_bounds


def test_equations():
    lower, upper = extract_bounds("Upper Bound Revenue = ARPU * Active Users = $0.10 * 6000 = $600")
    assert lower == 0
    assert upper == 600


# Utility function to load data from a specific file
def load_data_from(testdata_file: str):
    file_path = os.path.join(os.path.dirname(__file__) + "/testdata/", testdata_file)
    with open(file_path, "r") as file:
        return file.read()


def test_extract_bounds_lumio():
    lower, upper = extract_bounds(load_data_from("revenue_analysis_lumio.md"))
    assert lower == 69000000
    assert upper == 207000000

