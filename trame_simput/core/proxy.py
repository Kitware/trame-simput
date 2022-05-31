import logging
import yaml
import json
from pathlib import Path
from . import mapping, domains, utils


logger = logging.getLogger("simput.core.proxy")
logger.setLevel(logging.WARN)

# -----------------------------------------------------------------------------
# Proxy
# -----------------------------------------------------------------------------


class Proxy:
    """
    A Proxy keep track of a set of a properties for an other object.
    Proxy can flush its local state to the object it controls by calling commit().
    To reset uncommitted changes, just call reset().
    Proxy properties can be access with the . and [] notation.
    Proxy have states that are easily serializable.
    """

    __id_generator = utils.create_id_generator()
    __api = set(
        [
            "definition",
            "id",
            "type",
            "object",
            "manager",
            "modified",
            "mtime",
            "edited_property_names",
            "tags",
            "own",
            "set_property",
            "get_property",
            "list_property_names",
            "commit",
            "reset",
            "on",
            "off",
            "state",
            "remap_ids",
        ]
    )

    def __init__(
        self,
        __proxy_manager,
        __type,
        __object=None,
        _name=None,
        _tags=[],
        _object_adapter=None,
        **kwargs,
    ):
        self._id = next(Proxy.__id_generator)
        self._name = _name or __type
        self._mtime = __proxy_manager.mtime
        self._proxy_manager = __proxy_manager
        self._type = __type
        self._pushed_properties = {}
        self._properties = {}
        self._dirty_properties = set()
        self._listeners = set()
        self._tags = set(_tags)
        self._tags.update(self.definition.get("_tags", []))
        self._object_adapter = _object_adapter
        self._domains = {}

        if self._object_adapter is None:
            self._object_adapter = mapping.get_default_object_adapter()

        # Proxy can be fully virtual (:None)
        self._object = __object

        # proxy id that we created and therefore that we should manage
        self._own = set()

        # Handle registration
        self._proxy_manager._id_map[self._id] = self
        for tag in self._tags:
            self._proxy_manager._tag_map.setdefault(tag, set()).add(self._id)

        # handle initial
        for _prop_name, _prop_def in self.definition.items():
            if _prop_name.startswith("_"):
                continue

            _init_def = _prop_def.get("initial", None)
            if _prop_name in kwargs:
                self.set_property(_prop_name, kwargs[_prop_name])
            elif isinstance(_init_def, dict):
                logger.error("Don't know how to deal with domain yet: %s", _init_def)
            elif _init_def:
                self.set_property(_prop_name, _init_def)
            else:
                self.set_property(_prop_name, None)

        # handle domains
        for _prop_name, _prop_def in self.definition.items():
            if _prop_name.startswith("_"):
                continue
            _prop_domains = self._domains.setdefault(_prop_name, {})
            for domain_def in _prop_def.get("domains", []):
                _type = domain_def.get("type")
                _name = domain_def.get("name", _type)
                _prop_domain = domains.create_property_domain(
                    self, _prop_name, **domain_def
                )

                if _prop_domain is None:
                    logger.warn("No matching domain for type(%s)", _type)
                    continue

                if not _prop_domain:
                    continue

                if _name not in _prop_domains:
                    _prop_domains[_name] = _prop_domain
                else:
                    # Name conflict on domain/prop
                    count = 1
                    while f"{_name}_{count}" in _prop_domains:
                        count += 1
                    _prop_domains[f"{_name}_{count}"] = _prop_domain

                # Try default set
                _prop_domain.set_value()

        # May need several pass
        while self.domains_apply():
            pass

    def __del__(self):
        if self._object_adapter:
            self._object_adapter.before_delete(self)
        logger.info("Proxy deleted %s[%s]", self.type, self.id)

    @property
    def definition(self):
        """Return Proxy definition"""
        return self._proxy_manager.get_definition(self._type)

    @property
    def id(self):
        """Return Proxy ID"""
        return self._id

    @property
    def type(self):
        """Return Proxy Type"""
        return self._type

    @property
    def object(self):
        """Return Proxy concrete object if any"""
        return self._object

    @property
    def manager(self):
        """Return ProxyManager that owns us"""
        return self._proxy_manager

    def modified(self):
        """Mark proxy modified"""
        self._mtime = self.manager.modified()

    @property
    def mtime(self):
        """Return proxy modified time"""
        return self._mtime

    @property
    def edited_property_names(self):
        """Return the list of properties that needs to be pushed"""
        return self._dirty_properties

    @property
    def tags(self):
        """Return the list of tags of that proxy"""
        return self._tags

    @tags.setter
    def tags(self, value):
        """Update proxy tag"""
        self._tags = set(value)

    @property
    def own(self):
        """List of proxy ids we created"""
        return self._own

    @own.setter
    def own(self, ids):
        """Update list of proxy we own"""
        if isinstance(ids, str):
            # single id
            self._own.add(ids)
        elif isinstance(ids, Proxy):
            self._own.add(ids.id)
        else:
            self._own.update(ids)

    def set_property(self, name, value):
        """Update a property on that proxy"""
        # convert any invalid indirect value (proxy)
        prop_type = self.definition.get(name).get("type", "string")
        safe_value = value
        if value is not None:
            if prop_type == "proxy" and not isinstance(value, str):
                safe_value = value.id

        # check if change
        change_detected = False
        prev_value = self._properties.get(name, None)
        saved_value = self._pushed_properties.get(name, None)
        if utils.is_equal(safe_value, saved_value):
            self._dirty_properties.discard(name)
        elif not utils.is_equal(safe_value, prev_value):
            self._dirty_properties.add(name)
            change_detected = True
        self._properties[name] = safe_value

        if change_detected:
            self._proxy_manager.dirty_proxy(self._id)

        if self._object:
            self._object_adapter.update(self, name)

        self._emit(
            "update",
            modified=change_detected,
            property_name=name,
            properties_dirty=list(self._dirty_properties),
        )

        return change_detected

    def get_property(self, name, default=None):
        """Return a property value"""
        value = self._properties.get(name, default)
        if "proxy" == self.definition.get(name).get("type"):
            return self._proxy_manager.get(self._properties.get(name))

        return value

    def list_property_names(self):
        """Return the list of property names"""
        return [name for name in self.definition if not name.startswith("_")]

    def commit(self):
        """Flush modified properties"""
        self._proxy_manager.clean_proxy_data(self._id)
        if self._dirty_properties:
            properties_dirty = list(self._dirty_properties)
            if self._object:
                self._object_adapter.commit(self)

            self._pushed_properties.update(self._properties)
            self._dirty_properties.clear()

            for _sub_id in self.own:
                self._proxy_manager.get(_sub_id).commit()

            self._emit("commit", properties_dirty=properties_dirty)
            return True
        return False

    def reset(self):
        """Undo any uncommitted properties"""
        self._proxy_manager.clean_proxy_data(self._id)
        if self._dirty_properties:
            properties_dirty = list(self._dirty_properties)
            self._dirty_properties.clear()
            self._properties.update(self._pushed_properties)

            if self._object:
                self._object_adapter.reset(self, properties_dirty)

            self._emit("reset", properties_dirty=properties_dirty)
            return True

    def fetch(self):
        self._object_adapter.fetch(self)

    def on(self, fn):
        """
        Register listener:
        fn(topic, **kwars)
        => topic='reset' | properties_dirty=[]
        => topic='commit' | properties_dirty=[]
        => topic='update' | modified=bool, properties_dirty=[], properties_change=[]
        """
        self._listeners.add(fn)

    def off(self, fn):
        """Unegister listener"""
        self._listeners.discard(fn)

    def _emit(self, topic, *args, **kwargs):
        for fn in self._listeners:
            try:
                fn(topic, *args, **kwargs)
            except Exception:
                print(f"Error calling {fn} for {topic}:{args}, {kwargs}")

    def __getitem__(self, name):
        """value = proxy[prop_name]"""

        if self._properties and name in self._properties:
            if "proxy" == self.definition.get(name).get("type"):
                return self._proxy_manager.get(self._properties.get(name))

            return self._properties[name]

        logger.error("Proxy[%s] not found", name)

        raise AttributeError()

    def __setitem__(self, name, value):
        """proxy[prop_name] = value"""
        if name in self._properties and self.set_property(name, value):
            self._emit(
                "update",
                modified=True,
                properties_dirty=list(self._dirty_properties),
                properties_change=[name],
            )
        else:
            logger.error("%s.%s is not defined", name, self._elem_name)

    def __getattr__(self, name: str):
        """value = proxy.prop_name"""
        if name.startswith("_"):
            return self.__dict__.get(name, None)

        if name in Proxy.__api:
            return self.__dict__.get(name, None)

        # Fallback to properties
        return self.__getitem__(name)

    def __setattr__(self, name: str, value):
        """proxy.prop_name = value"""
        if name.startswith("_"):
            super().__setattr__(name, value)

        if self._properties and name in self._properties:
            self.__setitem__(name, value)
        else:
            super().__setattr__(name, value)

    @property
    def state(self):
        """Return proxy state that is easily serializable"""
        _properties = {}
        _obj_def = self.definition

        for prop_name, prop_def in _obj_def.items():
            if prop_name.startswith("_"):
                continue

            _properties[prop_name] = self._properties.get(prop_name, None)

        return {
            "id": self._id,
            "type": self._type,
            "name": self._name,
            "tags": list(self._tags),
            "mtime": self._mtime,
            "own": list(self._own),
            "properties": _properties,
        }

    @state.setter
    def state(self, value):
        """Use to rebuild a proxy state from an exported state"""
        self._own = set(value.get("own", []))
        self._tags.update(value.get("tags", []))
        for prop_name, prop_value in value.get("properties", {}).items():
            self.set_property(prop_name, prop_value)

        for tag in self._tags:
            self._proxy_manager._tag_map.setdefault(tag, set()).add(self._id)

    def remap_ids(self, id_map):
        """Use to remap id when reloading an exported state"""
        # Update proxy dependency
        _new_own = set()
        for old_id in self._own:
            _new_own.add(id_map[old_id])
        self._own = _new_own

        # Update proxy props
        for prop_name, prop_def in self.definition.items():
            if prop_name.startswith("_"):
                continue
            if prop_def.get("type", "") == "proxy":
                self._properties[prop_name] = id_map[self._properties[prop_name]]

    # domain api --------------------------------------------------------------

    def get_property_domains(self, property_name):
        """Helper to get the map of domains linked to a property"""
        return self._domains.get(property_name, {})

    def domains_apply(self, *property_names):
        """
        Ask domains to set values or just for one property if property_name is provided.
        Return the number of properties that have been updated.
        """
        change_count = 0
        selection = self._domains

        # Filter execution scope
        if property_names:
            selection = {}
            for name in property_names:
                selection[name] = self._domains.get(name, {})

        # Evaluate domains on selection
        for prop_domains in selection.values():
            for domain in prop_domains.values():
                if domain.set_value():
                    change_count += 1

        return change_count

    @property
    def domains_state(self):
        """
        Return a serializable state of the domains associated to this proxy.
        This include for each property and each domain a `valid` and `available` property.
        Also at the property level a list of `hints`.

        ```
        state = {
            ContourBy: {
                FieldSelector: {
                    valid: True,
                    available: [
                        { text: "Temperature", value: "Point::Temperature", ... },
                        ...
                    ]
                },
                hints: [],
            },
            Scalar: {
                Range: {
                    valid: True,
                    available: [0.5, 123.5],
                },
                hints: [
                    { level: 0, message: "Outside of range (0.5, 123.5)" },
                ],
            },
        }
        ```
        """
        output = {}
        for prop_name, prop_domains in self._domains.items():
            prop_info = {}
            hints = []

            for domain_name, domain_inst in prop_domains.items():
                available = domain_inst.available()
                valid = domain_inst.valid()
                hints += domain_inst.hints()
                if available or not valid:
                    prop_info[domain_name] = {"available": available, "valid": valid}

            if prop_info or hints:
                prop_info["hints"] = hints
                output[prop_name] = prop_info

        return output


# -----------------------------------------------------------------------------
# ProxyManager
# -----------------------------------------------------------------------------
class ProxyManager:
    """
    A ProxyManager needs to load some definitions in order to be able to create
    proxies which will hold a set of values in their properties.
    A proxy state can then be used to control a concrete object that can be
    local or remote.
    Proxies provide a nice infrastructure to map a UI to their state with
    domains and more.
    The ProxyManager is responsible for keeping track of proxies lifecycle and
    finding them from their Id or Tags.
    """

    __id_generator = utils.create_id_generator("pxm_")

    def __init__(self, object_factory=None, object_adapter=None):
        self._id = next(ProxyManager.__id_generator)

        self._mtime = 1
        self._listeners = set()
        self._life_cycle_listeners = set()
        self._obj_factory = object_factory
        self._obj_adapter = object_adapter

        self._model_definition = {}
        self._id_map = {}
        self._tag_map = {}
        self.dirty_proxy_data = set()
        self.dirty_proxy_domains = set()

    @property
    def id(self):
        """Return manager id"""
        return self._id

    @property
    def mtime(self):
        """Return current global modified time"""
        return self._mtime

    def modified(self):
        """Create a modified event and bump global mtime"""
        self._life_cycle("before_modified", mtime=self._mtime)
        self._mtime += 1
        self._life_cycle("after_modified", mtime=self._mtime)
        return self._mtime

    def _apply_mixin(self, *names):
        """Internal helper to decorate definition using some composition logic"""
        if len(names) == 0:
            names = self._model_definition.keys()

        for name in names:
            if name.startswith("_"):
                continue
            object_definition = self._model_definition.get(name, {})
            mixins = object_definition.get("_mixins", [])
            for mixin_name in mixins:
                mixin = self._model_definition.get(mixin_name, {})
                object_definition.update(mixin)

    # -------------------------------------------------------------------------
    # Event handling
    # -------------------------------------------------------------------------

    def _life_cycle(self, cycle, **kwargs):
        """Call lyfe cycle listeners"""
        for listener in self._life_cycle_listeners:
            getattr(listener, cycle)(**kwargs)

    def add_life_cycle_listener(self, listener):
        """Register life cycle listener"""
        listener.set_proxymanager(self)
        self._life_cycle_listeners.add(listener)

    def remove_life_cycle_listener(self, listener):
        """Unregister life cycle listener"""
        listener.set_proxymanager(None)
        self._life_cycle_listeners.discard(listener)

    def _emit(self, topic, **kwargs):
        for listener in self._listeners:
            listener(topic, **kwargs)

    def on(self, fn_callback):
        """
        Register callback when something is changing in ProxyManager.

        fn(topic, **kwars)
        => topic='created' | ids=[]
        => topic='changed' | ids=[]
        => topic='deleted' | ids=[]
        => topic='commit' | ids=[]
        => topic='reset' | ids=[]
        """
        self._listeners.add(fn_callback)

    def off(self, fn_callback):
        """
        Unregister attached function/method
        """
        self._listeners.discard(fn_callback)

    # -------------------------------------------------------------------------
    # Definition handling
    # -------------------------------------------------------------------------

    def load_model(self, yaml_file=None, yaml_content=None):
        """Load Data Model from YAML definition"""
        if yaml_file:
            path = Path(yaml_file)
            if path.exists():
                yaml_content = path.read_text(encoding="UTF-8")

        if yaml_content:
            add_on_dict = yaml.safe_load(yaml_content)
            self._life_cycle("before_load_model", definition=add_on_dict)
            self._model_definition.update(add_on_dict)
            self._apply_mixin(*add_on_dict.keys())
            self._life_cycle("after_load_model", definition=yaml_content)
            return True

        return False

    def get_definition(self, obj_type):
        """Return a loaded definition for a given object_type"""
        return self._model_definition.get(obj_type)

    def types(self, *with_tags):
        """List proxy_types from definition that has the set of provided tags"""
        result = []
        tag_filter = set(with_tags)
        for type_name in self._model_definition.keys():
            has_tag = set(self._model_definition[type_name].get("_tags", []))
            if tag_filter.issubset(has_tag):
                result.append(type_name)

        return result

    # -------------------------------------------------------------------------
    # Proxy management
    # -------------------------------------------------------------------------

    def create(self, proxy_type, **initial_values):
        """
        Create a new instance of a proxy using an proxy_type along with
        maybe a set of property values that we want to pre-initialise using the
        **kwargs approach.
        """

        # Can't create object if no definition available
        if proxy_type not in self._model_definition:
            raise ValueError(
                f"Object of type: {proxy_type} was not found in our loaded model definitions"
            )

        self._life_cycle(
            "proxy_create_before", proxy_type=proxy_type, initial_values=initial_values
        )
        obj = self._obj_factory.create(proxy_type) if self._obj_factory else None
        proxy = Proxy(
            self,
            proxy_type,
            obj,
            **{"_object_adapter": self._obj_adapter, **initial_values},
        )
        self._life_cycle(
            "proxy_create_before_commit",
            proxy_type=proxy_type,
            initial_values=initial_values,
            proxy=proxy,
        )

        proxy.commit()
        self._life_cycle(
            "proxy_create_after_commit",
            proxy_type=proxy_type,
            initial_values=initial_values,
            proxy=proxy,
        )

        self._emit("created", ids=[proxy.id])

        return proxy

    def delete(self, proxy_id, trigger_modified=True):
        """
        Delete object along with its dependency that it is owner of
        """
        self._life_cycle(
            "proxy_delete_before", proxy_id=proxy_id, trigger_modified=trigger_modified
        )
        before_delete = set(self._id_map.keys())
        # Delete ourself
        proxy_to_delete: Proxy = self._id_map[proxy_id]
        del self._id_map[proxy_id]

        for tag in proxy_to_delete.tags:
            self._tag_map.get(tag).discard(proxy_id)

        self._life_cycle(
            "proxy_delete_after_self",
            proxy_id=proxy_id,
            trigger_modified=trigger_modified,
            proxy=proxy_to_delete,
        )

        # Delete objects that we own
        for _id in proxy_to_delete.own:
            self.delete(_id, False)

        self._life_cycle(
            "proxy_delete_after_own",
            proxy_id=proxy_id,
            trigger_modified=trigger_modified,
            proxy=proxy_to_delete,
        )

        if trigger_modified:
            after_delete = set(self._id_map.keys())
            self.modified()
            self._emit("deleted", ids=list(before_delete.difference(after_delete)))

    def get(self, proxy_id: str) -> Proxy:
        """
        return proxy instance
        """
        return self._id_map.get(proxy_id, None)

    def update(self, change_set):
        """
        changeSet = [
            { id: 2143, name: 'Origin', value: [0, 1, 3] },
            ...
        ]
        """
        self._life_cycle("proxy_update_before", change_set=change_set)
        dirty_ids = set()
        dirty_proxies_to_commit = set()
        for change in change_set:
            _id = change["id"]
            _name = change["name"]
            _value = change["value"]
            dirty_ids.add(_id)
            proxy: Proxy = self.get(_id)
            if "auto_commit" in proxy.tags:
                dirty_proxies_to_commit.add(proxy)
            proxy.set_property(_name, _value)

        # commit changes for proxy tagged as auto_commit
        for proxy in dirty_proxies_to_commit:
            proxy.commit()
            self._emit("commit", ids=[proxy.id])

        self._life_cycle(
            "proxy_update_after", change_set=change_set, dirty_ids=dirty_ids
        )
        self._emit("changed", ids=list(dirty_ids))

    def get_instances_of_type(self, proxy_type):
        """
        Return all the instances of the given type
        """
        result = []
        for proxy in self._id_map.values():
            if proxy.type == proxy_type:
                result.append(proxy)

        return result

    def tags(self, *args):
        """List all instances containing all the listed tags"""
        selected_ids = set(self._id_map.keys())
        for tag in args:
            if tag in self._tag_map:
                selected_ids &= self._tag_map[tag]
            else:
                return []

        result = []
        for obj_id in selected_ids:
            result.append(self._id_map[obj_id])

        return result

    # -------------------------------------------------------------------------
    # Import / Export
    # -------------------------------------------------------------------------

    def save(self, file_output=None):
        """Export state (definition+data) into a file"""
        self._life_cycle("export_before", file_output=file_output)
        data = {
            "model": self._model_definition,
            "proxies": [proxy.state for proxy in self._id_map.values()],
        }
        self._life_cycle("export_after", file_output=file_output, data=data)
        if file_output:
            with open(file_output, "w") as outfile:
                json.dump(data, outfile)
        else:
            return json.dumps(data)

    def load(self, file_input=None, file_content=None):
        """Load previously exported state from a file"""
        self._life_cycle(
            "import_before", file_input=file_input, file_content=file_content
        )
        if file_input:
            with open(file_input) as json_file:
                data = json.load(json_file)
        else:
            data = json.loads(file_content)

        self._life_cycle(
            "import_before_processing",
            file_input=file_input,
            file_content=file_content,
            data=data,
        )

        self._model_definition.update(data["model"])

        # Create proxies
        _id_remap = {}
        _new_ids = []
        for proxy_state in data["proxies"]:
            _id = proxy_state["id"]
            _type = proxy_state["type"]
            _proxy = self.create(_type)
            _id_remap[_id] = _proxy.id
            _proxy.state = proxy_state
            _new_ids.append(_proxy.id)

        # Remap ids
        for new_id in _new_ids:
            _proxy = self.get(new_id)
            _proxy.remap_ids(_id_remap)
            _proxy.commit()

        self._life_cycle(
            "import_after",
            file_input=file_input,
            file_content=file_content,
            data=data,
            new_ids=_new_ids,
            id_remap=_id_remap,
        )
        self._emit("created", ids=_new_ids)

    # -------------------------------------------------------------------------
    # Commit / Reset
    # -------------------------------------------------------------------------

    def commit_all(self):
        """Commit all dirty proxies"""
        proxy_ids = list(self.dirty_proxy_data)
        for _id in proxy_ids:
            proxy = self.get(_id)
            if proxy:
                proxy.commit()
        self._emit("commit", ids=proxy_ids)

    def reset_all(self):
        """Reset all dirty proxies"""
        proxy_ids = list(self.dirty_proxy_data)
        for _id in proxy_ids:
            proxy = self.get(_id)
            if proxy:
                proxy.reset()
        self._emit("reset", ids=proxy_ids)

    # -------------------------------------------------------------------------
    # Dirty / Clean management
    # -------------------------------------------------------------------------

    def dirty_proxy(self, id):
        self.dirty_proxy_data.add(id)
        self.dirty_proxy_domains.add(id)

    def clean_proxy_data(self, id=None):
        if id is None:
            self.dirty_proxy_data.clear()
        else:
            self.dirty_proxy_data.discard(id)

    def clean_proxy_domains(self, id):
        if id is None:
            self.dirty_proxy_domains.clear()
        else:
            self.dirty_proxy_domains.discard(id)

    def list_and_clean_proxy_data(self):
        ids = list(self.dirty_proxy_data)
        self.dirty_proxy_data.clear()
        return ids

    def list_and_clean_proxy_domains(self):
        ids = list(self.dirty_proxy_domains)
        self.dirty_proxy_domains.clear()
        return ids
