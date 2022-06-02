import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("simput.core.controller")
logger.setLevel(logging.ERROR)


class SimputController:
    def __init__(
        self,
        server,
        ui_manager,
        namespace="simput",
        log_dir=None,
    ):
        logger.info("created")
        self._server = server
        self._ui_manager = ui_manager
        self._namespace = namespace
        self._pending_changeset = {}
        self._auto_update = False
        self._log_directory = log_dir if log_dir else os.environ.get("SIMPUT_LOG_DIR")

        # init keys
        self.id_key = f"{namespace}Id"
        self.changecount_key = f"{namespace}ChangeSet"
        self.changeset_key = f"{namespace}ChangeSetContent"
        self.auto_key = f"{namespace}AutoApply"
        self.apply_key = f"{namespace}Apply"
        self.reset_key = f"{namespace}Reset"
        self.fetch_key = f"{namespace}Fetch"
        self.update_key = f"{namespace}Update"
        self.refresh_key = f"{namespace}Refresh"
        self.reset_cache_key = f"{namespace}ResetCache"

        # Attach annotations
        self._server.state[self.id_key] = self._ui_manager.id
        self._server.state[self.changecount_key] = len(self.changeset)
        self._server.state[self.changeset_key] = self.changeset
        self._server.state[self.auto_key] = self._auto_update
        self._server.change(self.auto_key)(self._update_auto)
        self._server.trigger(self.apply_key)(self.apply)
        self._server.trigger(self.reset_key)(self.reset)
        self._server.trigger(self.fetch_key)(self.push)
        self._server.trigger(self.update_key)(self.update)
        self._server.trigger(self.refresh_key)(self.refresh)
        self._server.trigger(self.reset_cache_key)(self.reset_cache)

        # Monitor ui change
        self._ui_manager.on(self._ui_change)
        self._ui_manager.proxymanager.on(self._data_change)

        # Debug
        if self._log_directory:
            os.makedirs(self._log_directory, exist_ok=True)

    def __del__(self):
        logger.info("deleted")
        self._ui_manager.off(self._ui_change)
        self._ui_manager.proxymanager.off(self._data_change)

    def _log(self, id, name, content):
        if self._log_directory:
            full_path = Path(self._log_directory) / f"{id}_{name}.json"
            with open(full_path, "w") as file:
                file.write(json.dumps(content, indent=2))

    @property
    def changeset(self):
        logger.info("changeset")
        change_set = []
        for obj_id in self._pending_changeset:
            for prop_name in self._pending_changeset[obj_id]:
                value = self._pending_changeset[obj_id][prop_name]
                change_set.append(
                    {
                        "id": obj_id,
                        "name": prop_name,
                        "value": value,
                    }
                )
        return change_set

    def apply(self):
        logger.info("apply")
        self._ui_manager.proxymanager.commit_all()

        # Make sure reset don't send things twice
        self._pending_changeset = {}
        self.reset()

    def reset(self):
        logger.info("reset")
        ids_to_update = list(self._pending_changeset.keys())
        self._pending_changeset = {}
        self._server.state[self.changecount_key] = 0
        self._server.state[self.changeset_key] = []

        self._ui_manager.proxymanager.reset_all()

        # Go ahead and push changes
        for _id in ids_to_update:
            self.push(id=_id, domains=_id)

    def refresh(self, id=0, property=""):
        logger.info("refresh")
        proxy = self._ui_manager.proxymanager.get(id)
        if not proxy:
            return

        prop_domains = proxy.get_property_domains(property).values()

        # Reset
        change_count = 0
        for domain in prop_domains:
            domain.enable_set_value()
            change_count += domain.set_value()

        if change_count:
            for _id in proxy.proxymanager.list_and_clean_proxy_domains():
                self.push(id=_id)

            if self._auto_update:
                self.apply()

    def reset_cache(self):
        logger.info("reset_cache")
        self._server.protocol_call("simput.reset.cache")

    def push(self, id=None, type=None, domains=None):
        logger.info("push id(%s) - type(%s) - domains(%s)", id, type, domains)
        if id:
            self._server.protocol_call("simput.data.get", self._ui_manager.id, id)
        if type:
            self._server.protocol_call("simput.ui.get", self._ui_manager.id, type)
        if domains:
            self._server.protocol_call(
                "simput.domains.get", self._ui_manager.id, domains
            )

    def emit(self, topic, **kwargs):
        logger.info("emit: %s", topic)
        self._server.protocol_call("simput.push.event", topic, **kwargs)

    def update(self, change_set):
        logger.info("update")
        pxm = self._ui_manager.proxymanager
        id_map = {}
        for change in change_set:
            _id = change.get("id")
            _name = change.get("name")
            _value = change.get("value")

            if _id not in self._pending_changeset:
                self._pending_changeset[_id] = {}
            _obj_change = self._pending_changeset[_id]

            _obj_change[_name] = _value

            # debug
            if self._log_directory:
                id_map.setdefault(_id, {})
                id_map[_id][_name] = _value

        if self._log_directory:
            for _id in id_map:
                self._log(_id, "change", id_map[_id])

        self._server.state[self.changecount_key] = len(self.changeset)
        self._server.state[self.changeset_key] = self.changeset

        # Update data
        pxm.update(change_set)

        # Run domains
        change_detected = 1
        all_ids = set()
        data_ids = set()

        # Execute domains
        while change_detected:
            change_detected = 0
            m_ids = pxm.list_and_clean_proxy_domains()
            all_ids.update(m_ids)
            for _id in m_ids:
                if pxm.get(_id).domains_apply():
                    data_ids.add(_id)
                    change_detected += 1

        # Push any changed state in domains
        for _id in all_ids:
            pxm.clean_proxy_domains(_id)
            proxy = pxm.get(_id)
            _domain = proxy.domains_state
            self._log(_id, "domain", _domain)
            self._server.protocol_call(
                "simput.message.push",
                {
                    "id": _id,
                    "domains": _domain,
                },
            )

        for _id in data_ids:
            _data = self._ui_manager.data(_id)
            self._log(_id, "data", _data)
            self._server.protocol_call(
                "simput.message.push",
                {
                    "id": _id,
                    "data": _data,
                },
            )

        if self._auto_update:
            self.apply()

    @property
    def has_changes(self):
        return len(self._pending_changeset) > 0

    @property
    def auto_update(self):
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value):
        logger.info("auto_update")
        self._auto_update = value
        self._server.state[self.auto_key] = value

    def _update_auto(self, **kwargs):
        if self.auto_update == self._server.state[self.auto_key]:
            return
        logger.info("_update_auto")
        value = self._server.state[self.auto_key]
        self.auto_update = value
        if value:
            self.apply()

    def _ui_change(self, *args, **kwargs):
        logger.info("_ui_change")
        self.emit("ui-change")

    def _data_change(self, action, **kwargs):
        logger.info("_data_change")
        self.emit("data-change", action=action, **kwargs)

        if action == "commit":
            _ids = kwargs.get("ids", [])
            for _id in _ids:
                self._pending_changeset.pop(_id)
            self._server.state[self.changecount_key] = len(self.changeset)
            self._server.state[self.changeset_key] = self.changeset
