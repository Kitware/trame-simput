import os
import json
from pathlib import Path

from wslink import register as exportRpc
from wslink.websocket import LinkProtocol

from trame_simput.core.factory import get_simput_manager
import logging

logger = logging.getLogger("simput.core.protocol")
logger.setLevel(logging.ERROR)


class SimputProtocol(LinkProtocol):
    def __init__(self, log_dir=None):
        logger.info("Created")
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
        logger.info("reset_cache")
        self.net_cache_domains = {}

    @exportRpc("simput.push")
    def push(self, manager_id, id=None, type=None):
        logger.info("push")
        uim = get_simput_manager(manager_id)
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
        logger.info("get_data")
        uim = get_simput_manager(manager_id)
        _data = uim.data(id)
        self._log(id, "data", _data)
        msg = {"id": id, "data": _data}
        self.send_message(msg)
        return msg

    @exportRpc("simput.ui.get")
    def get_ui(self, manager_id, type):
        logger.info("get_ui")
        uim = get_simput_manager(manager_id)
        msg = {"type": type, "ui": uim.ui(type)}
        self.send_message(msg)
        return msg

    @exportRpc("simput.domains.get")
    def get_domains(self, manager_id, id):
        logger.info("get_domains")
        msg = {"id": id, "domains": {}}

        pxm = get_simput_manager(manager_id).proxymanager
        pxm.clean_proxy_domains(id)
        _domain = pxm.get(id).domains_state
        self._log(id, "domain", _domain)
        msg["domains"] = _domain

        self.send_message(msg)
        return msg

    @exportRpc("simput.message.push")
    def send_message(self, message):
        logger.info("send_message")
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
        logger.info("emit %s", topic)
        event = {"topic": topic, **kwargs}
        self.publish("simput.event", event)
