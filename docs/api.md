# API

SimPut relies on 3 types of managers that build on top of each other and are responsible for handling Proxy, UI and Domains.

- **ProxyManager**:

  - Loads proxy definitions
  - Creates/Deletes proxies
  - Finds/Gets proxies
  - Updates proxies from a changeset
  - Commits/Resets all modified proxies
  - Imports/Exports state of all created proxies
  - (optional) Maps proxy state to concrete object

- **UIManager**:

  - Requires **ProxyManager** and **UI resolver**
  - Loads language/layout definitions
  - Gets proxy state for UI
  - Gets proxy form for UI (include language + layout)

- **ProxyDomainManager**:

  - Attaches to **ProxyManager** to add behavior to proxy initialization and update.
  - Creates a **ProxyDomain** for each newly created proxy.
  - Monitors dirty proxies during an update, so modified domains can be applied in one sweep.
  - Gets **ProxyDomain** from proxy id.

## ProxyManager

**Definition handling**

```python
def load_model(self, yaml_file=None, yaml_content=None):
    """Load Data Model from YAML definition"""

def get_definition(self, proxy_type):
    """Return a loaded definition for a given object_type"""

def types(self, *with_tags):
    """List proxy_types from definition that has the set of provided tags"""
```

**Proxy Management**

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

**Import / Export**

```python
def save(self, file_output=None):
    """Export state (definition+data) into a file"""

def load(self, file_input=None, file_content=None):
    """Load previously exported state from a file"""
```

**Commit / Reset**

```python
def commit_all(self):
    """Commit all dirty proxies"""

def reset_all(self):
    """Reset all dirty proxies"""
```

**Find / Query Proxy**

```python
def get_instances_of_type(self, proxy_type):
    """
    Return all the instances of the given type
    """

def tags(self, *args):
    """List all instances containing all the listed tags"""
```

### Proxy

Core proxy properties

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

Advanced Read/Write properties

```python
@property
def tags(self):
    """Return the list of tags of that proxy"""

@property
def own(self):
    """List of proxy ids we created"""
```

Property management

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

Commit / Reset property edit

```python
def commit(self):
    """Flush modified properties"""

def reset(self):
    """Undo any uncommited properties"""
```

State management for IO and import/export

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

### ObjectValue

Base class for objects that can be used as a value for properties.
They can be passed around by copy instead of reference. A proxy still provides the same reference, on which you can interact with method calls, but when the value needs to be shared to another location or service, the object gets serialized and re-created on the other side in a transparent manner.

The expected API is as follow:

```python
    @property
    def state(self):
        """
        Return a serialized version of its state.
        The type of ObjectValue is not included in the state and
        therefore the initial instantiation is left to the proxy.
        """

    @state.setter
    def state(self, value):
        """Update internal data from provided serialized state"""
```

## UIManager

The **UIManager** needs a **ProxyManager** and a **UIResolver** at construction time.

**Load language/layout definitions**

```python
def load_language(self, yaml_file=None, yaml_content=None, clear_ui=False):
    """Load langage for the objects form"""

def load_ui(self, xml_file=None, xml_content=None, clear_ui=False):
    """Load layout for the objects form"""

def clear_ui(self):
    """
    Clear any loaded UI definition
    => This will force auto-generation if nothing new gets loaded
    """
```

**Data exchange for UI handling**

```python
def data(self, proxy_id):
    """Return proxy state to fill UI with"""

def ui(self, _type):
    """Return resolved layout (xml string with resolved elements+attributes)"""
```

### UIResolver

A **UIResolver** is responsible to process the XML from a `<ui/>` definition and convert it into another XML that can then be used by a UI backend (Vuetify, Qt, ...) without much processing logic.
The resolver has access to labels and helps from the language file along with the model definition that can include domains.

Below you can see how a `<ui/>` element will be transformed for the Vuetify target.

**Input**

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

**Output**

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

## ProxyDomainManager

A **ProxyDomainManager** is responsible to add behavior on a **ProxyManager** by listening to proxy creation and update. For that it needs to be registered to the **ProxyManager** by calling `pxm.add_life_cycle_listener(pdm)`.

Once registered, it will track **ProxyDomain** for each created proxy. Also, whenever proxy updates happen, it will keep track of the modified one to only re-execute any domain that needs to be updated.
Users just need to call `apply_all()` after any batch update to flush the domain and set any missing property initialization.

### ProxyDomain

```python
def apply(self, *property_names):
    """
    Ask domains to set values or just for one property if property_name is provided.
    Return the number of properties that have been updated.
    """

def get_property_domains(self, prop_name):
    """Helper to get the map of domains linked to a property"""

@property
def state(self):
    """
    Return a serializable state of the domains linked to a proxy.
    This include for each property and each domain a `valid` and `available` property.
    Also at the property level a list of `hints`.

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
    """
```

### PropertyDomain

```python
def enable_set_value(self):
    """Reset domain set so it can re-compute a default value"""

def set_value(self):
    """
    Ask domain to compute and set a value to a property.
    return True if the action was succesful.
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

## Domains

Concrete implementation of domains.

### ProxyBuilder

```
  initial: xyz              | set name=xyz proxy to the property as default
  values:                   | list all possible proxy that can be set
    - name: xyz             | proxy entry: - name
      type: Representation  |              - proxy type
  bind: Input               | set self to SubProxy.Input property (optional)
```

### IsEqual

```
  name: Scalars          | (optional) provide another name than its type
  available: {type/name} | Which domain available list on prop to use
  value: Scalar          | Value that our prop needs to match to be "valid"
```

### FieldSelector

```
  name: List           | (optional) provide another name than its type
  input: Input         | Specify property on which field inspection happen
  location: Point      | Filtering arrays to be only on [Point/Cell/Field]
  size: 1              | Number of components for available arrays
  initial: first       | (optional) if provided, domain will set array to prop
  isA:                 | (optional) filter arrays by their type
    - vtkDataArray     |   => Only numerical arrays
```

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

### ResetOnChange \*\*

```
  name: xxxx                | (optional) provide another name than its type
 -----------------------------------------------------------------------------
  property: Property name   | When current property change reset domain on
  domain: Domain name/type  | property so default values could be regenerated
```

### BoundsCenter

```
  name: xxxx                | (optional) provide another name than its type
 -----------------------------------------------------------------------------
  proxy: Property name containing data object proxy
  property: Property on Proxy that is the data object
```

### LabelList

```
  name: xxxx                | (optional) provide another name than its type
 -----------------------------------------------------------------------------
  values: [{ text, value}, ...]
```

## ObjectValue

Concrete implementation of object values

### Array

Capture Array name and location (point/cell/field)
