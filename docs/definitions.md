# Data model definition

In order to describe the various **proxies** and **properties** we want to use, we rely on
a __YAML__ file like the one below.

```yaml
vtkSphereSource:       # `Type` of proxy
    _tags:               # (optional) metadata binding
        - Source           # tag name to be associated to this kind of proxy
    Radius:              # `Property name`
        size: 1            # how many values expected (default: 1)
        type: float64      # value type: (u)int(8,16,32,64), float(32,64), bool, proxy
        initial: 0.5       # initial value to set
    Center:              # Property `Center` contains 3 floats with an initial value of [0, 0, 0]
        size: 3
        type: float64
        initial: [0, 0, 0]
    ThetaResolution:     # Property `ThetaResolution` contains a single positive integer
        type: uint16
    PhiResolution:
        type: uint16
    StartTheta:
        type: float64
    EndTheta:
        type: float64
    StartPhi:
        type: float64
    EndPhi:
        type: float64
    LatLongTesselation:  # Property `LatLongTesselation` contains a single boolean value
        type: bool
    OuptuPointsPrecision:
        type: uint8
    GenerateNormal:
        type: bool

vtkConeSource:         # Another proxy `Type`
    _tags:
        - Source
    Height:
        type: float64
    # ...

# ...
```

The __YAML__ structure follow the given hierarchy:

1. Proxy type: Unique string representing the type of a given proxy.
   1. _tags: Internal key use to capture a list of `labels` for a given proxy so they can be found/filtered later on.
   2. Property name: Unique string within current proxy representing an entry in your data model.
      1. Property caracteristics:
         1. size: How many values should be stored for that property. Skipping size attribute will imply a size of 1.
            If size is superior to 1, or set to -1, the property will be interpreted as a list.
            If size is set to -1, the size is dynamic, otherwise it is fixed.
            For vue3, only lists of primitive types (uint, int, float, bool, string) are supported.
            For vue2, proxy lists are also supported. `proxyType` must then be set to define the type of proxy listed
         2. type: What kind of values that property is holding.
            1. uint(8,16,32,64): Unsigned integer encoded on 8, 16, 32, 64 bytes.
            2. int(8,16,32,64): Signed integer encoded on 8, 16, 32, 64 bytes.
            3. float(32,64): Floating point encoded on 32 or 64 bytes.
            4. bool: Boolean (true/false)
            5. proxy: Reference to another proxy inside our database.
      2. Optional internal hints:
         1. _label: Internal key for replacing the property name for a given **language** for the UI layer
         2. _help: Internal key for providing help on the property for a given **language** for the UI layer
         3. _ui: Internal key to help UI layer to dynamically build a corresponding **layout** definition when not provided.
            1. skip: will skip showing that entry in the layout
            2. proxy: will show the content of the linked proxy rather than (proxy selection + selected proxy content)
         4. _***: Internal key that will be skipped unless needed by some specific implementation
      3. Optional domain related:
         1. domains: Container for listing any domain that should be linked to a property.
            1. A domain entry should contains
               1. type: Name of the domain class
               2. name: (optional) identifier when we don't want to use its `type` as identifier.
               3. **: additional parameters specific to domain type expectation.

# Domain definitions

Domains help to compute initial values or constraint user input.

An example for **compute initial value** could be the following use case where we have a vtkAlgorithm
that will perform some operation on its input dataset using one of the input field. Such vtkAlgorithm
will need to select which `Field` should be use for the processing and which `Value` should be used as
a seed for the computation while the `Value` should be within range of the selectedd `Field`.

Currently the built-in set of domains are **LabelList** and **Range** but custom implementation can be used.

A property **domain** has the following set of reserved keys:
- type: Name of a registered domain class
- name: (optional) application identifier when its `type` is not sufficient. (i.e.: several domain with same type, used by another domain and need to meaningful name)
- initial: (optional) when provided, the domain will try to set an initial value to the property.
- level: (optional) How strict that domain should be.
  - 0: (default) information
  - 1: warning
  - 2: error
- message: (optional) Text that should be displayed if the domain is not valid so the user can understand what's wrong.
- **: Any other key required for a specific domain type.

# Language definition

Simput does not provide an API for switching languages but simply focus on
loading **labels** and **helps** from definition files. Within your
application you then have the opportunity to load different files based on
a selected language. And you have the choice to clear previous content or
simply override any definition read.

In order to support several languages easily we allow the user to separate
them from the core model definition and just writes what matters.
But as an initial pass, the core model definition can be used as language file
with or without `_label` and `_help` entries. Then a more light weight file
can be read with just the translation part. As you can see below the structure
remain similar to our core model definition but we only focus on `_label` and
`_help` for each section. Also it is possible to change the **order** in which
the properties should appear. This will take into account when a **layout**
file is not provided.

```yaml
# fr.yaml
vtkSphereSource:
    _label: Sphère
    _help: Génère un maillage représentant une sphère
    Radius:
        _label: Rayon
    Center:
        _label: Centre
    ThetaResolution:
        _label: Résolution autour de theta
    PhiResolution:
        _label: Résolution autour de phi
    StartTheta:
        _label: Angle initial pour theta
    EndTheta:
        _label: Angle final pour theta
    StartPhi:
        _label: Angle initial pour phi
    EndPhi:
         _label: Angle final pour phi
```

# Layout definition

The layout definition is mainly to control the flow of properties by being
explicit. By default if not provided, the property order defined in the
loaded **language** definition will be used in a vertical layout.
But if the user wants full control of it, an XML file can be provided.
The example below capture most of the syntax to illustrate its capabilities.

```xml
<layouts>
    <ui id="vtkSphereSource">
        <col>
            <input name="Radius" />
            <input name="Center" />
            <row>
                <input name="ThetaResolution" />
                <input name="StartTheta" />
                <input name="EndTheta" />
            </row>
            <row>
                <input name="PhiResolution" />
                <input name="StartPhi" />
                <input name="EndPhi" />
            </row>
        </col>
    </ui>
    <!-- ... -->
</layouts>
```

Each proxy UI is defined by an `<ui id="type" />` element which can be gathered
inside a single XML file by nesting them under a `<layouts />` container.
Each `<ui />` element must contains an `id=` attribute to bind such UI layout
to a proxy type definition.

Inside a `<ui>` element you can use `<col>` and `<row>` to control the direction
of the flow of properties. A `<spacer/>` and `<divider/>` is also available to
push properties to the end of the current flow or create a line separator between
them. When a simple text, annotation should be placed, the
`<text content="A message"/>` can be used.

A property get exposed by adding a `<input name="PropertyName" />` entry.

When a property is of `type: proxy`, the `<input />` will display a drop down
assuming a "ListDomain" is used to define the possible set of proxies that can
be set for that property while `<proxy name="PropertyName" />` will inline the
UI for the proxy that the property is referring to. By default, a generated layout
will add `<input/>` and `<proxy/>` one after the other unless an attribute
`_ui: skip` or `_ui: proxy` is defined on that property.
The **skip** option will skip both while the **proxy** will only show the
`<proxy/>` part.

On top of those core elements, we also have containers that can be use to
**show** or **hide** a set of properties. They work by using a domain to
perform their action `<show/>` or `<hide/>`.

```yaml
Clip:
    ClipFunction:
        type: proxy
        domains:
            - type: ProxyBuilder
              initial: Plane
              values:
                - name: Plane
                  type: ImplicitPlane
                - name: Box
                  type: ImplicitBox
                - name: Sphere
                  type: ImplicitSphere
                - name: Scalar
                  type: ImplicitPlaceHolder
            - name: Scalars
              type: IsEqual
              available: ProxyBuilder
              value: Scalar
    # ...
```

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
</ui>
```

Using the following set of elements you should be able to layout your various
properties. But depending on the UI resolver used in the processing of your
layout file, you can provide additional attributes that could control
components styles such as `class=""` or `layout="m3-half"` for lengthy
properties.

So far, the supported layout values for a property are:
- `vertical`, `l2`, `l3`, `l4`, `m3-half`.
- The `l{number}` are for grouping `number` entries per line.
- Skipping layout is the same as setting it to `horizontal`.