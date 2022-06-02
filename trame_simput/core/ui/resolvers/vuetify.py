import xml.etree.ElementTree as ET

VUETIFY_MAP = {
    "ui": "div",
    "row": "v-row",
    "col": "v-col",
    "spacer": "v-spacer",
    "divider": "v-divider",
    "show": "sw-show",
    "hide": "sw-hide",
    "text": "sw-text",
}

WIDGET_MAP = {
    "input": "sw-text-field",
    "textarea": "sw-text-area",
}

WIDGET_KNOWN = {
    "div",
    "v-row",
    "v-col",
    "v-spacer",
    "v-divider",
    "sw-show",
    "sw-hide",
    "sw-text",
    "sw-text-field",
    "sw-text-area",
    "sw-slider",
    "sw-group",
}


class VuetifyResolver:
    def __init__(self):
        self._model = None
        self._labels = None

    def get_widget(self, elem):
        attributes = {}
        if elem.tag in VUETIFY_MAP:
            return VUETIFY_MAP[elem.tag], attributes
        elif elem.tag == "input":
            domains = self._model.get(elem.get("name"), {}).get("domains", [])
            widget = "sw-text-field"
            for domain in domains:
                ctype = domain.get("type")
                level = domain.get("level", 0)
                widget = domain.get("widget", widget)
                attributes.update(domain.get("ui_attributes", {}))
                if ctype in ["LabelList", "HasTags"]:
                    values = domain.get("values", [])
                    prop_name = domain.get("property", None)
                    if len(values) and ctype not in ["HasTags", "ProxyBuilder"]:
                        attributes[":items"] = values

                    if prop_name and ctype != "FieldSelector":
                        attributes["itemsProperty"] = prop_name
                    widget = "sw-select"
                if ctype == "Boolean":
                    widget = "sw-switch"
                if ctype == "Range" and level == 2:
                    value_range = domain.get("value_range", None)
                    if value_range:
                        attributes[":min"] = str(value_range[0])
                        attributes[":max"] = str(value_range[1])
                    widget = "sw-slider"

                if ctype == "UI":
                    attributes.update(domain.get("properties", {}))
                    custom_widget = domain.get("widget", None)
                    if custom_widget and custom_widget in WIDGET_MAP:
                        widget = WIDGET_MAP[custom_widget]

            if widget is None:
                widget = "sw-text-field"

            if self._model.get(elem.get("name"), {}).get("type", "string") == "bool":
                widget = "sw-switch"

            return widget, attributes
        elif elem.tag == "proxy":
            return "sw-proxy", attributes

        if not (elem.tag in WIDGET_KNOWN or elem.tag.startswith("sw-")):
            print(f"Unknown widget element {elem.tag}")
        return elem.tag, attributes

    def process_node(self, in_elem):
        # xml mapping
        key = in_elem.get("name")
        elem_lan = None
        elem_label = key
        elem_help = None
        if key:
            elem_lan = self._labels.get(key)

        if elem_lan:
            elem_label = elem_lan.get("_label", key)
            elem_help = elem_lan.get("_help", None)

        widget, add_on_attrs = self.get_widget(in_elem)
        if not widget:
            return None

        # Add name, label, help, size
        out_elem = ET.Element(widget)
        out_elem.set(":mtime", "data.mtime")

        if key is not None and key in self._model:
            size = self._model.get(key).get("size", 1)
            ptype = self._model.get(key).get("type", "string")
            out_elem.set("name", key)
            out_elem.set("size", f"{size}")
            out_elem.set("type", ptype)
            out_elem.set(":initial", f"data.original['{key}']")
        if elem_label:
            out_elem.set("label", elem_label)
        if elem_help:
            out_elem.set("help", elem_help)

        # Add-on attributes
        for key in add_on_attrs:
            if isinstance(add_on_attrs[key], (bool, int)):
                prefix = ""
                if key[0] != ":":
                    prefix = ":"
                out_elem.set(f"{prefix}{key}", f"{add_on_attrs[key]}".lower())
            else:
                out_elem.set(key, add_on_attrs[key])

        # ui(attr) => html(attr)
        for key in in_elem.attrib:
            if key != "name":
                out_elem.set(key, in_elem.attrib[key])

        # process hierarchy
        for child in in_elem:
            out_child = self.process_node(child)
            if out_child is not None:
                out_elem.append(out_child)

        return out_elem

    def resolve(self, model, labels, ui):
        self._model = model
        self._labels = labels
        in_root = ET.fromstringlist(ui)
        out_root = self.process_node(in_root)
        self._model = None
        self._labels = None
        # print(ET.tostring(out_root, encoding="UTF-8"))
        return ET.tostring(out_root, encoding="utf-8").decode("utf-8")
