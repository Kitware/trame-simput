import pytest

from trame_simput import get_simput_manager


@pytest.fixture(scope="session")
def manager():
    return get_simput_manager()


@pytest.fixture
def proxymanager(manager):
    return manager.proxymanager
