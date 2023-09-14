import keyring

pytest_plugins = ["pytester"]


def pytest_sessionstart():
    """Set a test credential on session start."""
    keyring.set_password("database", "username", "pass")


def pytest_sessionfinish():
    """Clean-up test credential."""
    keyring.delete_password("database", "username")
