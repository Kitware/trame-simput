import os
import json
from pathlib import Path

from wslink import register as exportRpc
from wslink.websocket import LinkProtocol

serve_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "serve"))

# -----------------------------------------------------------------------------
# Basic application setup
# -----------------------------------------------------------------------------

serve = {"__simput": serve_path}
# scripts = ["/__simput/vue-simput.umd.js"]
scripts = ["/__simput/vue-simput.umd.min.js"]
vue_use = ["VueSimput"]

# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------

MANAGERS = {}


def get_manager(_id, _type):
    handler = MANAGERS.get(_id, None)
    if handler is None:
        print(f"No manager found for id {_id}")
        return

    return handler.get(_type)


def get_ui_manager(_id):
    return get_manager(_id, "ui_manager")


def get_domains_manager(_id):
    return get_manager(_id, "domains_manager")


# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------


class SimputProtocol(LinkProtocol):
    def __init__(self, log_dir=None):
        super().__init__()
        self._log_directory = log_dir if log_dir else os.environ.get("SIMPUT_LOG_DIR")
        self.reset_cache()

        if self._log_directory:
            os.makedirs(self._log_directory, exist_ok=True)

    def _log(self, id, name, content):
        if self._log_directory:
            full_path = Path(self._log_directory) / f"{id}_{name}.json"
            with open(full_path, "w") as file:
                file.write(json.dumps(content, indent=2))

    @exportRpc("simput.reset.cache")
    def reset_cache(self):
        self.net_cache_domains = {}

    @exportRpc("simput.push")
    def push(self, manager_id, id=None, type=None):
        uim = get_ui_manager(manager_id)
        message = {"id": id, "type": type}
        if id is not None:
            _data = uim.data(id)
            self._log(id, "data", _data)
            message.update({"data": _data})

        if type is not None:
            message.update({"ui": uim.ui(type)})

        self.publish("simput.push", message)

    @exportRpc("simput.data.get")
    def get_data(self, manager_id, id):
        uim = get_ui_manager(manager_id)
        _data = uim.data(id)
        self._log(id, "data", _data)
        msg = {"id": id, "data": _data}
        self.send_message(msg)
        return msg

    @exportRpc("simput.ui.get")
    def get_ui(self, manager_id, type):
        uim = get_ui_manager(manager_id)
        msg = {"type": type, "ui": uim.ui(type)}
        self.send_message(msg)
        return msg

    @exportRpc("simput.domains.get")
    def get_domains(self, manager_id, id):
        msg = {"id": id, "domains": {}}

        domains_manager = get_domains_manager(manager_id)
        if domains_manager:
            domains_manager.clean(id)
            _domain = domains_manager.get(id).state
            self._log(id, "domain", _domain)
            msg["domains"] = _domain

        self.send_message(msg)
        return msg

    @exportRpc("simput.message.push")
    def send_message(self, message):
        # Cache domain to prevent network call
        # when not needed. (optional)
        if "domains" in message:
            _id = message.get("id")
            content = self.net_cache_domains.get(_id)
            to_send = json.dumps(message)
            if content == to_send:
                return
            self.net_cache_domains[_id] = to_send
        # - end
        self.publish("simput.push", message)

    @exportRpc("simput.push.event")
    def emit(self, topic, **kwargs):
        event = {"topic": topic, **kwargs}
        self.publish("simput.event", event)


# -----------------------------------------------------------------------------
# Module advanced initialization
# -----------------------------------------------------------------------------
APP = None


def configure_protocol(root_protocol):
    root_protocol.registerLinkProtocol(SimputProtocol())


def setup(app, **kwargs):
    global APP
    APP = app
    app.add_protocol_to_configure(configure_protocol)


# -----------------------------------------------------------------------------


def register_manager(ui_manager, domains_manager=None):
    global MANAGERS
    MANAGERS[ui_manager.id] = {
        "ui_manager": ui_manager,
        "domains_manager": domains_manager,
    }


def create_helper(
    ui_manager,
    domains_manager=None,
    namespace="simput",
):
    register_manager(ui_manager, domains_manager)
    return SimputHelper(
        APP, ui_manager, namespace=namespace, domains_manager=domains_manager
    )
