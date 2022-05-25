import yaml
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from . import ui, utils

import logging

logger = logging.getLogger("simput.core")
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# ProxyDomain
# -----------------------------------------------------------------------------
class ProxyDomain:
    """
    A ProxyDomain is responsible for:
    - keeping track of all the domains attached to a given proxy
    """

    # __prop_domain_availables = {}

    # @staticmethod
    # def register_property_domain(name: str, constructor):
    #     ProxyDomain.__prop_domain_availables[name] = constructor

    # def __init__(self, _proxy, _domain_manager):
    #     self._proxy = _proxy
    #     self._domain_manager = _domain_manager
    #     self._domains = {}
    #     self._dirty_props = set()

    #     # Monitor proxy change
    #     _proxy.on(self._on_proxy_change)

    #     # Build domains for given proxy
    #     definition = _proxy.definition
    #     _domains = self._domains
    #     for name in definition:
    #         if name.startswith("_"):
    #             continue
    #         _prop_domains = _domains.setdefault(name, {})
    #         for domain_def in definition[name].get("domains", []):
    #             _type = domain_def.get("type")
    #             _name = domain_def.get("name", _type)
    #             if _type in ProxyDomain.__prop_domain_availables:
    #                 domain_inst = ProxyDomain.__prop_domain_availables[_type](
    #                     _proxy, name, self._domain_manager, **domain_def
    #                 )
    #                 if _name not in _prop_domains:
    #                     _prop_domains[_name] = domain_inst
    #                 else:
    #                     count = 1
    #                     while f"{_name}_{count}" in _prop_domains:
    #                         count += 1
    #                     _prop_domains[f"{_name}_{count}"] = domain_inst

    #                 # Try default set
    #                 domain_inst.set_value()
    #             else:
    #                 print(f"Could not find domain of type: {_type}")

    def __del__(self):
        logger.info("ProxyDomain::__del__", self._proxy.id, "::", self._proxy.type)

    def detatch(self):
        self._proxy.off(self._on_proxy_change)
        self._proxy = None

    def _on_proxy_change(
        self, topic, modified=False, properties_dirty=[], properties_change=[], **kwargs
    ):
        if topic == "update":
            self._dirty_props.update(properties_dirty)
            self._dirty_props.update(properties_change)
            self._domain_manager.dirty(self._proxy.id)

    # def apply(self, *property_names):
    #     """
    #     Ask domains to set values or just for one property if property_name is provided.
    #     Return the number of properties that have been updated.
    #     """
    #     change_count = 0
    #     selection = self._domains
    #     if property_names:
    #         selection = {}
    #         for name in property_names:
    #             selection[name] = self._domains.get(name, {})

    #     for prop_domains in selection.values():
    #         for domain in prop_domains.values():
    #             if domain.set_value():
    #                 change_count += 1

    #     return change_count

    # def get_property_domains(self, prop_name):
    #     """Helper to get the map of domains linked to a property"""
    #     return self._domains.get(prop_name, {})

    # @property
    # def state(self):
    #     """
    #     Return a serializable state of the domains linked to a proxy.
    #     This include for each property and each domain a `valid` and `available` property.
    #     Also at the property level a list of `hints`.

    #     ```
    #     state = {
    #         ContourBy: {
    #             FieldSelector: {
    #                 valid: True,
    #                 available: [
    #                     { text: "Temperature", value: "Point::Temperature", ... },
    #                     ...
    #                 ]
    #             },
    #             hints: [],
    #         },
    #         Scalar: {
    #             Range: {
    #                 valid: True,
    #                 available: [0.5, 123.5],
    #             },
    #             hints: [
    #                 { level: 0, message: "Outside of range (0.5, 123.5)" },
    #             ],
    #         },
    #     }
    #     ```
    #     """
    #     output = {}
    #     for prop_name, prop_domains in self._domains.items():
    #         prop_info = {}
    #         hints = []

    #         for domain_name, domain_inst in prop_domains.items():
    #             available = domain_inst.available()
    #             valid = domain_inst.valid()
    #             hints += domain_inst.hints()
    #             if available or not valid:
    #                 prop_info[domain_name] = {"available": available, "valid": valid}

    #         if prop_info or hints:
    #             prop_info["hints"] = hints
    #             output[prop_name] = prop_info

    #     return output


# -----------------------------------------------------------------------------
# DomainManager
# -----------------------------------------------------------------------------
class ProxyDomainManager(ProxyManagerLifeCycleListener):
    """
    A DomainManager can optionally be linked to a ProxyManager to handle
    Domains life cycle and provide validation and/or guidance on how to set values
    to the properties of a proxy.
    This enable domain to set initial values and let UIManager to provide
    additional informations to the client for error checking and listing
    available values for drop down and else.
    """

    def __init__(self):
        self._id_map = {}
        self._dirty_ids = set()

    # def is_dirty(self, _id):
    #     return _id in self._dirty_ids

    # def clean(self, *_ids):
    #     for _id in _ids:
    #         self._dirty_ids.discard(_id)

    # def dirty(self, *_ids):
    #     for _id in _ids:
    #         self._dirty_ids.add(_id)

    # def dirty_ids(self):
    #     return _DirtyDomainsResources(self, self._dirty_ids)

    # def get(self, _id):
    #     return self._id_map.get(_id)

    # def proxy_create_before_commit(self, proxy_type, initial_values, proxy, **kwargs):
    #     pd = ProxyDomain(proxy, self)
    #     self._id_map[proxy.id] = pd
    #     while pd.apply():
    #         pass
    #         # print("domain::apply(create)", proxy.id)

    # def proxy_delete_before(self, proxy_id, trigger_modified, **kwargs):
    #     self._id_map[proxy_id].detatch()
    #     del self._id_map[proxy_id]

    def apply_all(self):
        results = {}
        with self.dirty_ids() as ids:
            for id in ids:
                results[id] = self.get(id).apply()
        return results


# class _DirtyDomainsResources(set):
#     def __init__(self, pdm, dirty_set):
#         super().__init__(dirty_set)
#         self._pdm = pdm

#     def __enter__(self):
#         self._pdm._dirty_ids.clear()
#         return self

#     def __exit__(self, exc_type, exc_value, exc_traceback):
#         pass
