# API

Simput for trame rely on a global simput manager which will give you access
to all the pieces you may want to have access. Within an application,
you can ask for several simput manager to control various part of your
application state, but in general a single one is enough.

The first thing you will need to do is grab an instance of that simput
manager by using the `get_simput_manager(id=None, pxm=None, resolver=None, object_factory=None, object_adapter=None)` method.
And then from the instance you get, you will be able to create a container
widget or get your hand on its **proxymanager** to manage its proxies.

## Simput manager

The simput manager instance lets you do the following:
- Access its linked **proxymanager**
- Reset cached UI layout elements by calling **clear_ui()**
- Load definitions, language and UI by calling one of the following methods
  - **load_model(yaml_file=None, yaml_content=None)**
  - **load_language(yaml_file=None, yaml_content=None, clear_ui=False)**
  - **load_ui(xml_file=None, xml_content=None, clear_ui=False)**
- Subscribe or unsubscribe to event/lifecycle
  - **on(fn_callback)**
  - **off(fn_callback)**
- Retrieve proxy state using the **data(proxy_id)** method
- Retrieve proxy type layout using the **ui(proxy_type)** method

## ProxyManager

A proxy manager can let you create/edit/get/delete any proxy but also save or load the full state of a proxy manager in a way you can catch up where you left off in a previous session or execution.

__Proxy Management__

```python
def create(self, proxy_type, **initial_values):
    """
    Create a new instance of a proxy using an proxy_type along with
    maybe a set of property values that we want to pre-initialise using the
    **kwargs approach.
    """

def delete(self, proxy_id, trigger_modified=True):
    """
    Delete object along with its dependency that it is owner of
    """

def get(self, proxy_id: str) -> Proxy:
    """
    return proxy instance
    """

def update(self, change_set):
    """
    changeSet = [
        { id: 2143, name: 'Origin', value: [0, 1, 3] },
        ...
    ]
    """
```

__Import / Export__

```python
def save(self, file_output=None):
    """Export state (definition+data) into a file"""

def load(self, file_input=None, file_content=None):
    """
    Load previously exported state from a file.
    Return the proxy id remap which is a dict with proxy id's found in the provided state as keys and the corresponding freshly created proxy id's as values.
    """
```

__Commit / Reset__

```python
def commit_all(self):
    """Commit all dirty proxies"""

def reset_all(self):
    """Reset all dirty proxies"""
```

__Find / Query Proxy__

```python
def get_instances_of_type(self, proxy_type):
    """
    Return all the instances of the given type
    """

def tags(self, *args):
    """List all instances containing all the listed tags"""
```

### Proxy

__Core proxy properties__

```python
@property
def manager(self):
    """Return ProxyManager that owns us"""

@property
def definition(self):
    """Return Proxy definition"""

@property
def type(self):
    """Return Proxy Type"""

@property
def id(self):
    """Return Proxy ID"""

@property
def object(self):
    """Return Proxy concrete object if any"""
```

__Advanced Read/Write properties__

```python
@property
def tags(self):
    """Return the list of tags of that proxy"""

@property
def own(self):
    """List of proxy ids we created"""
```

__Property management__

```python
def set_property(self, name, value):
    """Update a property on that proxy"""

def get_property(self, name, default=None):
    """Return a property value"""

def list_property_names(self):
    """Return the list of property names"""

# ---------------------------------------------------------
# Attribute/Item usage
# ---------------------------------------------------------
# - Get property:
#     - print(proxy_inst.prop_name)
#     - print(proxy_inst["prop_name"])
# - Set property
#     -  proxy_inst.prop_name = 3
#     -  proxy_inst["prop_name"] = 3
# ---------------------------------------------------------
```

__Commit / Reset property edit__

```python
def commit(self):
    """Flush modified properties"""

def reset(self):
    """Undo any uncommitted properties"""
```

__State management for IO and import/export__

```python
@property
def state(self):
    """Return proxy state that is easily serializable"""

@state.setter
def state(self, value):
    """Use to rebuild a proxy state from an exported state"""

def remap_ids(self, id_map):
    """Use to remap id when reloading an exported state"""
```

### UIResolver

A **UIResolver** is responsible to process the XML from a `<ui/>` definition and convert it into another XML that can then be used by a UI backend (Vuetify, Qt, ...) without much processing logic.
The resolver has access to labels+helps from the language file along with the model definition that can include domains.

Below you can see how a `<ui/>` element will be transformed for the Vuetify target.

__Input__
```xml
<ui id="Clip">
    <input name="ClipFunction" />
    <proxy name="ClipFunction" />
    <show property="ClipFunction" domain="Scalars">
        <col>
            <row>
                <input name="Value" />
                <input name="Scalars" />
            </row>
        </col>
    </show>
    <input name="InsideOut" class="mx-2"/>
</ui>
```

__Output__
```xml
<div>
    <sw-select
        name="ClipFunction"
        size="1"
        type="proxy"
        :mtime="data.mtime"
        :initial="data.original['ClipFunction']"
        label="Clip Function"
        help="Function to use for clipping"
    />
    <sw-proxy name="ClipFunction" />
    <sw-show property="ClipFunction" domain="Scalars">
        <v-col>
            <sw-text-field
                name="Value"
                size="1"
                type="float64"
                :mtime="data.mtime"
                :initial="data.original['Value']"
                label="Value"
                help=""
            />
            <sw-select
                name="Scalars"
                size="1"
                type="value::Array"
                :mtime="data.mtime"
                :initial="data.original['Scalars']"
                label="Clip by Array"
                help="Which field to use for clipping dataset"
            />
        </v-col>
    </sw-show>

    <sw-switch
        class="mx-2"
        name="InsideOut"
        size="1"
        type="uint8"
        :mtime="data.mtime"
        :initial="data.original['InsideOut']"
        label="Inside Out"
        help="Toggle which side of the clip to keep"
    />
</div>
```

### PropertyDomain

If a custom domain is required, a class inheriting **PropertyDomain** will need to be creating while overriding some of its methods.

```python
def enable_set_value(self):
    """Reset domain set so it can re-compute a default value"""

def set_value(self):
    """
    Ask domain to compute and set a value to a property.
    return True if the action was successful.
    """

def available(self):
    """List the available options"""

@property
def value(self):
    """Return the current proxy property value on which the domain is bound"""

@value.setter
def value(self, v):
    """Set the proxy property value"""

def valid(self, required_level=2):
    """Return true if the current proxy property value is valid for the given level"""

@property
def level(self):
    """Return current domain level (0:info, 1:warn, 2:error)"""

@level.setter
def level(self, value):
    """Update domain level"""

@property
def message(self):
    """Associated domain message that is used for hints"""

@message.setter
def message(self, value):
    """Update domain message"""

def hints(self):
    """Return a set of (level, message) when running the validation for the info level"""
```

## UI Widgets

### Simput Widget

The `Simput` widget is a trame component that is used as the UI data management provider.
This component must be registered as the root of the layout with the `register_layout(layout)` method (preferred method) or by setting `layout.root = simput_widget`.

```python
@property
def helper(self):
    """Simput helper object"""

def apply(self, **kwargs):
    """Flush modified properties so they can be pushed to their concrete objects"""

def reset(self, **kwargs):
    """Unapply properties"""

def push(self, id=None, type=None, domains=None, proxy=None, **kwargs):
    """Ask server to push data, ui, or constraints"""

def update(self, change_set, **kwargs):
    """
    List of properties and value to update

    >>> change_set = [
    ... {"id":"12", "name":"Radius", "value": 0.75},
    ... {"id": "12", "name":"Resolution", "value": 24}
    ... ]
    """

def register_layout(self, layout):
    """
    Register self to the root of the layout and
    clear any previously registered elements (to support hot reloading)
    """

def refresh(self, id=0, property="", **kwargs):
    """Refresh the given id's property"""

def reload(self, name):
    """Reload the given name (data, ui, domain)"""

@property
def changeset(self):
    """All unapplied changesets"""

@property
def has_changes(self):
    """Does the changeset have content?"""

@property
def auto_update(self):
    """Whether to automatically apply changes"""
```

### SimputItem Widget

`SimputItem` is a trame component that is used to display a Simput item. This must be child of a Simput component to have access to Simput data.

```python
item_proxy = pxm.create("Item")
# Create a SimputItem widget to display the item
simput.SimputItem(item_id=f"{item_proxy.id}")
```

## Domains

### Range

```
  name: xxxx                | (optional) provide another name than its type
 -----------------------------------------------------------------------------
  value_range: [0, 1]       | Static range
 -----------------------------------------------------------------------------
  property: PropArray       | Specify property on which an array is defined
  initial: [mean, min, max] | Computation to use for setting the value
  component: -1 (mag)       | Component to use for range computation
```


### LabelList

```
  name: xxxx                | (optional) provide another name than its type
 -----------------------------------------------------------------------------
  values: [{ text, value}, ...]
```
