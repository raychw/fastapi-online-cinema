import pytest


def pytest_generate_tests(metafunc):
    if "anyio_backend" in metafunc.fixturenames:
        metafunc.parametrize("anyio_backend", ["asyncio"])
