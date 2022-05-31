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
        return True if the action was successful.
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
#  name: xxxx      : (optional) provide another name than its type
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
# Range
# -----------------------------------------------------------------------------
#  name: xxxx                 (optional) provide another name than its type
# -----------------------------------------------------------------------------
#  value_range: [0, 1]        Static range
# -----------------------------------------------------------------------------
#  property: PropArray        Specify property on which an array is defined
#  initial: [mean, min, max]  Computation to use for setting the value
#  component: -1 (mag)        Component to use for range computation
# -----------------------------------------------------------------------------


class Range(PropertyDomain):
    def __init__(self, _proxy, _property: str, **kwargs):
        super().__init__(_proxy, _property, **kwargs)
        self.__compute = kwargs.get("initial", "mean")
        self.__prop_array = kwargs.get("property", None)
        self.__range_component = kwargs.get("component", -1)
        self.__static_range = kwargs.get("value_range", False)
        self._message = "Range"

        # Declare dependency
        if self.__prop_array:
            # ic("Range add dep", self.__prop_array)
            self._dependent_properties.add(self.__prop_array)

    def set_value(self):
        if self._should_compute_value:
            data_range = self.get_range(self.__range_component)
            if data_range is None:
                return False

            _v = 0
            if self.__compute == "mean":
                _v = (data_range[0] + data_range[1]) * 0.5
            elif self.__compute == "min":
                _v = data_range[0]
            elif self.__compute == "max":
                _v = data_range[1]
            else:
                print(
                    f"Range domain can't compute {self.__compute}. Expect 'mean', 'min' or 'max' instead."
                )

            prop_size = self._proxy.definition.get(self._property_name).get("size", 1)
            if prop_size == -1:
                self.value = [_v]
            elif prop_size > 1:
                if self.value and isinstance(self.value, list):
                    if len(self.value):
                        self.value[0] = _v
                    else:
                        self.value.append(_v)
                else:
                    self.value = [_v]
            else:
                self.value = _v

            self._should_compute_value = False
            return True
        return False

    def available(self):
        return self.get_range(self.__range_component)

    def valid(self, required_level=2):
        if self._level < required_level:
            return True

        _v = self.value
        if _v is None:
            self._message = (
                f"Undefined value can not be evaluated in {self.available()}"
            )
            return False

        _range = self.available()
        self._message = f"Value outside of {_range}"
        if isinstance(_v, list):
            _valid = True
            for __v in _v:
                if __v is None:
                    continue
                if _range[0] is not None and __v < _range[0]:
                    _valid = False
                if _range[1] is not None and __v > _range[1]:
                    _valid = False
            return _valid

        lower = _range[0] is None or _v >= _range[0]
        upper = _range[1] is None or _v <= _range[1]
        return lower and upper

    def get_range(self, component=-1):
        if self.__static_range:
            return self.__static_range

        return None


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
# Default Skip
# -----------------------------------------------------------------------------


SKIP_NAMES = [
    "PropertyList",
    "Boolean",
    "UI",
]
for name in SKIP_NAMES:
    register_property_domain(name, False)


# -----------------------------------------------------------------------------
# Default initialization
# -----------------------------------------------------------------------------


register_property_domain("LabelList", LabelList)
register_property_domain("Range", Range)
