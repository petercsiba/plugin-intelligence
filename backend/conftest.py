# Putting it top-level, as pytest will search parent directories for `conftest.py`


from common.config import ENV, ENV_LOCAL, ENV_TEST


def pytest_sessionstart(session):
    assert ENV in (
        ENV_LOCAL,
        ENV_TEST,
    ), "Tests should only run in 'local' or 'test' environments. Current ENV: {}".format(
        ENV
    )
