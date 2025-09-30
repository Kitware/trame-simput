from pathlib import Path
from .. import utils
from .utils import extract_ui
import yaml
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger("simput.core.ui")
logger.setLevel(logging.ERROR)


class UIManager:
    """
    UI Manager provide UI information to edit and input object properties

    A UIManager is responsible to map a UI to proxy properties with the help
    of a resolver which is specialized to the target environment (Qt, Web)
    """

    id_generator = utils.create_id_generator()

    def __init__(self, proxymanager, ui_resolver):
        self._id = next(UIManager.id_generator)
        self._pxm = proxymanager
        self._ui_resolver = ui_resolver
        self._ui_xml = {}
        self._ui_lang = {}
        self._ui_resolved = {}
        # event handling
        self._listeners = set()

    @property
    def id(self):
        """Return Manager id"""
        return f"{self._pxm.id}:{self._id}"

    @property
    def proxymanager(self):
        """Return linked proxy manager"""
        return self._pxm

    def clear_ui(self):
        """Clear any loaded UI definition"""
        self._ui_xml = {}
        self._ui_resolved = {}

    # -------------------------------------------------------------------------
    # Definition handling
    # -------------------------------------------------------------------------

    def load_model(self, yaml_file=None, yaml_content=None):
        self.load_language(yaml_file=yaml_file, yaml_content=yaml_content)
        return self.proxymanager.load_model(yaml_file, yaml_content)

    def load_language(self, yaml_file=None, yaml_content=None, clear_ui=False):
        """Load language for the objects form"""
        if clear_ui:
            self.clear_ui()

        if yaml_file:
            path = Path(yaml_file)
            if path.exists():
                yaml_content = path.read_text(encoding="UTF-8")

        if yaml_content:
            self._ui_lang.update(yaml.safe_load(yaml_content))
            auto_ui = extract_ui(yaml_content)
            self._ui_resolved = {}
            ui_change_count = 0
            for ui_type in auto_ui:
                if ui_type not in self._ui_xml:
                    self._ui_xml[ui_type] = auto_ui[ui_type]
                    ui_change_count += 1

            if ui_change_count:
                self._emit("lang+ui")
            else:
                self._emit("lang")

            return True

        return False

    def load_ui(self, xml_file=None, xml_content=None, clear_ui=False):
        """Load layout for the objects form"""
        if clear_ui:
            self.clear_ui()

        if xml_file:
            path = Path(xml_file)
            if path.exists():
                xml_content = path.read_text(encoding="UTF-8")

        if xml_content:
            root = ET.fromstring(xml_content)
            for child in root:
                obj_type = child.attrib["id"]
                self._ui_xml[obj_type] = ET.tostring(child).decode("UTF-8").strip()

            self._ui_resolved = {}
            self._emit("ui")
            return True

        return False

    # -------------------------------------------------------------------------
    # Event handling
    # -------------------------------------------------------------------------

    def _emit(self, topic, **kwargs):
        for listener in self._listeners:
            listener(topic, **kwargs)

    def on(self, fn_callback):
        """
        Register callback when something is changing in ObjectManager.

        fn(topic, **kwars)
        => topic='ui'
        => topic='lang'
        => topic='lang+ui'
        """
        self._listeners.add(fn_callback)

    def off(self, fn_callback):
        """
        Unregister callback
        """
        self._listeners.discard(fn_callback)

    # -------------------------------------------------------------------------
    # UI handling
    # -------------------------------------------------------------------------

    def data(self, proxy_id):
        """Return proxy state to fill UI with"""
        _proxy = self._pxm.get(proxy_id)
        if _proxy:
            return _proxy.state

        logger.info("UIManager::data(%s) => No proxy", proxy_id)
        return None

    def ui(self, _type):
        """Return resolved layout"""
        if _type in self._ui_resolved:
            return self._ui_resolved[_type]

        model_def = self._pxm.get_definition(_type)
        lang_def = self._ui_lang[_type]
        ui_def = self._ui_xml[_type]
        resolved = self._ui_resolver.resolve(model_def, lang_def, ui_def)
        self._ui_resolved[_type] = resolved

        return resolved
