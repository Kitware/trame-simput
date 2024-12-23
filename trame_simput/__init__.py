from trame_client.utils.version import get_version

from .core import get_simput_manager

__version__ = get_version("trame_simput")

__all__ = [
    "__version__",
    "get_simput_manager",
]
