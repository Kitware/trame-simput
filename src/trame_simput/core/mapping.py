import logging

logger = logging.getLogger("simput.core.mapping")
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# Default singleton
# ----------------------------------------------------------------------------
DEFAULT_PROXY_OBJECT_ADAPTER = None


def get_default_object_adapter():
    global DEFAULT_PROXY_OBJECT_ADAPTER
    if DEFAULT_PROXY_OBJECT_ADAPTER is None:
        DEFAULT_PROXY_OBJECT_ADAPTER = ProxyObjectAdapter()

    return DEFAULT_PROXY_OBJECT_ADAPTER


# ----------------------------------------------------------------------------
# ProxyObjectAdapter
# ----------------------------------------------------------------------------
class ProxyObjectAdapter:
    """API for proxy/object synchronization"""

    @staticmethod
    def commit(proxy):
        pass

    @staticmethod
    def reset(proxy, props_to_reset=[]):
        pass

    @staticmethod
    def fetch(proxy):
        pass

    @staticmethod
    def update(proxy, *property_names):
        pass

    @staticmethod
    def before_delete(proxy):
        pass


# ----------------------------------------------------------------------------
# ObjectFactory
# ----------------------------------------------------------------------------
class ObjectFactory:
    """
    Concrete object factory

    The ObjectFactory is responsible for the creation of concrete object that
    a given proxy can control.
    """

    def __init__(self):
        self._map = {}

    def register(self, name, klass):
        """Register constructor to match definition type"""
        self._map[name] = klass

    def create(self, name, **kwargs):
        """Try to create concreate object"""
        obj = None
        if name in self._map:
            obj = self._map[name](**kwargs)

        if name in globals():
            obj = globals()[name](**kwargs)

        if obj is None:
            logger.error("Could not instantiate", name)

        return obj
