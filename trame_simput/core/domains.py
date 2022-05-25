import logging

logger = logging.getLogger("simput.core.domains")
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# PropertyDomain
# -----------------------------------------------------------------------------
class PropertyDomain:
    """
    A Domain is responsible for:
      - testing if a property is valid
      - compute and set a property value
      - list what are the possible value options

     Domain meta information:
     - level describe the importance of the domain
        (0: info), (1: warning), (2: error)
     - message personalize the context in which a given domain is used to help
       understand why a given value is not valid.
    """

    def __init__(self, _proxy, _property: str, **kwargs):
        self._proxy = _proxy
        self._property_name = _property
        self._dependent_properties = set([self._property_name])
        self._need_set = "initial" in kwargs
        self._level = kwargs.get("level", 0)
        self._message = kwargs.get("message", str(__class__))
        self._should_compute_value = "initial" in kwargs

    def __del__(self):
        logger.info(
            "PropertyDomain::__del__ %s[%s].%s",
            self._proxy.type,
            self._proxy.id,
            self._property_name,
        )

    def enable_set_value(self):
        """Reset domain set so it can re-compute a default value"""
        self._should_compute_value = True

    def set_value(self):
        """
        Ask domain to compute and set a value to a property.
        return True if the action was succesful.
        """
        return False

    def available(self):
        """List the available options"""
        return None

    @property
    def value(self):
        """Return the current proxy property value on which the domain is bound"""
        return self._proxy[self._property_name]

    @value.setter
    def value(self, v):
        """Set the proxy property value"""
        self._proxy.set_property(self._property_name, v)

    def valid(self, required_level=2):
        """Return true if the current proxy property value is valid for the given level"""
        return True

    @property
    def level(self):
        """Return current domain level (0:info, 1:warn, 2:error)"""
        return self._level

    @level.setter
    def level(self, value):
        """Update domain level"""
        self._level = value

    @property
    def message(self):
        """Associated domain message that is used for hints"""
        return self._message

    @message.setter
    def message(self, value):
        """Update domain message"""
        self._message = value

    def hints(self):
        """Return a set of (level, message) when running the validation for the info level"""
        if self.valid(-1):
            return []
        return [
            {
                "level": self._level,
                "message": self._message,
            }
        ]


# -----------------------------------------------------------------------------
# LabelList
# -----------------------------------------------------------------------------
#  name: xxxx                | (optional) provide another name than its type
#  type: LabelList           | select this domain
# -----------------------------------------------------------------------------
#  values: [{ text, value}, ...]
# -----------------------------------------------------------------------------
class LabelList(PropertyDomain):
    def __init__(self, _proxy, _property: str, **kwargs):
        super().__init__(_proxy, _property, **kwargs)
        self._values = kwargs.get("values", [])
        self._message = "LabelList"

    def set_value(self):
        if self._should_compute_value and self._values:
            self._should_compute_value = False
            # first
            self.value = self._values[0].get("value")
            return True
        return False

    def available(self):
        return self._values

    def valid(self, required_level=2):
        if self._level < required_level:
            return True

        v = self.value
        for item in self._values:
            if item.get("value", None) == v:
                return True
        return False


# -----------------------------------------------------------------------------
# Factory management of PropertyDomain
# -----------------------------------------------------------------------------
REGISTERED_DOMAIN_BY_TYPE = {}


def create_property_domain(proxy, proxy_prop_name, type=None, **domain_config):
    if type in REGISTERED_DOMAIN_BY_TYPE:
        domain = REGISTERED_DOMAIN_BY_TYPE[type]
        if domain:
            return domain(proxy, proxy_prop_name, **domain_config)
        return False


def register_property_domain(domain_type, domain_class):
    global REGISTERED_DOMAIN_BY_TYPE
    REGISTERED_DOMAIN_BY_TYPE[domain_type] = domain_class


# -----------------------------------------------------------------------------
# Default initialization
# -----------------------------------------------------------------------------
register_property_domain("LabelList", LabelList)

# Skip
SKIP_NAMES = [
    "PropertyList",
    "Boolean",
    "UI",
]
for name in SKIP_NAMES:
    register_property_domain(name, False)
