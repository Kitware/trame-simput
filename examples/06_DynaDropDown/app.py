from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, simput, html
from trame.decorators import TrameApp

from trame_simput import get_simput_manager
from trame_simput.core.domains import PropertyDomain, register_property_domain

PROXY_FIELDS = {}


class ListDomain(PropertyDomain):
    def __init__(self, _proxy, _property, **kwargs):
        super().__init__(_proxy, _property, **kwargs)

    def available(self):
        return PROXY_FIELDS[self._proxy.id]


@TrameApp()
class App:
    def __init__(self, server=None):
        global PROXY_FIELDS
        self.server = get_server(server, client_type="vue2")
        register_property_domain("ListDomain", ListDomain)

        # Simput
        self.simput_manager = get_simput_manager()
        self.simput_manager.load_model(yaml_file=Path(__file__).with_name("model.yaml"))

        # Create some proxies
        self.state.available_proxies = []
        for name in ["Item A", "Item B", "Item C"]:
            proxy = self.simput_manager.proxymanager.create("Item")
            proxy.name = name
            proxy.commit()
            PROXY_FIELDS[proxy.id] = ["a", "b"]
            self.state.available_proxies.append(proxy.id)

        # Simput widget
        self.simput_widget = simput.Simput(
            self.simput_manager, trame_server=self.server
        )
        self.simput_widget.auto_update = True
        self.ctrl.simput_apply = self.simput_widget.apply
        self.ctrl.simput_reset = self.simput_widget.reset
        self.ctrl.simput_reload_domain = self.simput_widget.reload_domain
        # self.ctrl.simput_reload_data = self.simput_widget.reload_data

        # Build UI
        self.ui = self._build_ui()

    @property
    def ctrl(self):
        return self.server.controller

    @property
    def state(self):
        return self.server.state

    def _build_ui(self):
        with SinglePageLayout(self.server) as layout:
            self.simput_widget.register_layout(layout)

            layout.title.set_text("Simput")

            with layout.toolbar as toolbar:
                toolbar.dense = True
                vuetify.VSpacer()
                html.Span("{{ active_proxy }}")
                vuetify.VBtn("A", classes="ml-2", click=self.mode_a)
                vuetify.VBtn("B", classes="ml-2", click=self.mode_b)

            with layout.content:
                with vuetify.VContainer(fluid=True):
                    vuetify.VSelect(
                        label="Proxy Selector",
                        v_model=("active_proxy", None),
                        items=("available_proxies", []),
                    )
                    simput.SimputItem(item_id="active_proxy")

            return layout

    def mode_a(self):
        PROXY_FIELDS[self.state.active_proxy] = ["a", "b", "c"]
        self.ctrl.simput_reload_domain()
        # self.ctrl.simput_reload_data()

    def mode_b(self):
        PROXY_FIELDS[self.state.active_proxy] = ["a", "b", "c", "d", "e", "f"]
        self.ctrl.simput_reload_domain()
        # self.ctrl.simput_reload_data()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    App().server.start()
