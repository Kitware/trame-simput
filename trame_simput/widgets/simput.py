from trame_client.widgets.core import AbstractElement
from .. import module
from ..module.core import SimputController


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


class Simput(HtmlElement):
    """
    Simput data management component. This must be set as the root of a layout to provide children with Simput data. See simput docs |simput_link| for more info.

    .. |simput_link| raw:: html

        <a href="https://github.com/Kitware/py-simput" target="_blank">here</a>

    :param ui_manager: See simput docs |simput_link| for more info
    :param domains_manager: See simput docs |simput_link| for more info
    :param prefix: Constructing a Simput component will set several variables, optionally prefixed by a namespace
    :type prefix:  str | None
    :param query: String filtering
    :type query: str
    :param children: The children nested within this element
    :type children:  str | list[trame.html.*] | trame.html.* | None

    >>> layout.root = simput.Simput(ui_manager, prefix="myForm")
    """

    def __init__(self, ui_manager, prefix=None, children=None, **kwargs):
        super().__init__("Simput", children, **kwargs)
        ns = f"simput_{self._id}"
        if prefix:
            ns = prefix
        self._helper = SimputController(self._server, ui_manager, namespace=ns)
        self._attributes["namespace"] = f'namespace="{ns}"'
        self._attr_names += ["query"]

    @property
    def helper(self):
        """
        Simput helper object
        """
        return self._helper

    def apply(self, **kwargs):
        """
        Flush modified properties so they can be pushed to their concrete objects
        """
        self._helper.apply()

    def reset(self, **kwargs):
        """
        Unapply properties
        """

        self._helper.reset()

    def push(self, id=None, type=None, domains=None, proxy=None, **kwargs):
        """
        Ask server to push data, ui, or constraints
        """
        if proxy is not None:
            id = proxy
            domains = proxy
        self._helper.push(id=id, type=type, domains=domains)

    def update(self, change_set, **kwargs):
        """
        List of properties and value to update

        >>> change_set = [
        ... {"id":"12", "name":"Radius", "value": 0.75},
        ... {"id": "12", "name":"Resolution", "value": 24}
        ... ]

        """
        self._helper.update(change_set)

    def refresh(self, id=0, property="", **kwargs):
        self._helper.refresh(id, property)

    @property
    def changeset(self):
        """
        All unapplied changesets
        """
        return self._helper.changeset()

    @property
    def has_changes(self):
        """
        Does the changeset have content?
        """
        return self._helper.has_changes

    @property
    def auto_update(self):
        """
        Whether to automatically apply changes
        """
        return self._helper.auto_update

    @auto_update.setter
    def auto_update(self, value):
        self._helper.auto_update = value


class SimputItem(HtmlElement):
    """
    Simput data display component. This must be child of a Simput component to have access to Simput data. See simput docs |simput_link| for more info.

    :param item_id: The simput id of the data to display
    :type item_id: str
    :param extract: Columns to make available from this component to its children
    :type extract: list[str]
    :param no_ui: Whether to show simput template UI
    :type no_ui: bool
    :param v_slot: Fields to be pass to slot template (i.e.: data, ui, domain, properties, all...)
    :type v_slot: str
    :param children: The children nested within this element
    :type children:  str | list[trame.html.*] | trame.html.* | None

    Events

    :param dirty: Function to call when itemId is changed
    :type dirty: function
    """

    def __init__(self, children=None, extract=[], **kwargs):
        super().__init__("SimputItem", children, **kwargs)
        self._attr_names += [
            ("item_id", ":itemId"),
            "no_ui",
            ("v_slot", "v-slot"),
        ]
        self._event_names += [
            "dirty",
        ]

        if extract:
            self._attributes["prop_extract"] = f'#properties="{{{", ".join(extract)}}}"'


__all__ = [
    "Simput",
    "SimputItem",
]
