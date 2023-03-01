from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, simput

from trame_simput import get_simput_manager
from trame_simput.core.domains import PropertyDomain, register_property_domain

# -----------------------------------------------------------------------------
# Custom Simput domain
# -----------------------------------------------------------------------------


class TagDecoratorDomain(PropertyDomain):
    active_tags = set()

    def __init__(self, _proxy, _property, **kwargs):
        super().__init__(_proxy, _property, **kwargs)
        self.tags = kwargs.get("properties")["tags"]

    def available(self):
        return {
            "show": self._show(),
            "enable": True,
            "query": True,
        }

    def _show(self):
        for tag in self.tags:
            if tag in self.active_tags:
                return True
        return False


# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

register_property_domain("TagDecoratorDomain", TagDecoratorDomain)
simput_manager = get_simput_manager()
simput_manager.load_model(yaml_file=Path(__file__).with_name("model.yaml"))
item = simput_manager.proxymanager.create("AdvancedViewExample")

# -----------------------------------------------------------------------------
# Application state
# -----------------------------------------------------------------------------


@state.change("ui_advanced")
def update_advanced(ui_advanced, **kwargs):
    if ui_advanced:
        TagDecoratorDomain.active_tags.add("advanced")
    elif "advanced" in TagDecoratorDomain.active_tags:
        TagDecoratorDomain.active_tags.remove("advanced")
    ctrl.simput_reload_domain()


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    with server.ui.detached:  # prevent simput to be child of layout
        simput_widget = simput.Simput(simput_manager, prefix="simput")
        ctrl.simput_apply = simput_widget.apply
        ctrl.simput_reset = simput_widget.reset
        ctrl.simput_reload_domain = simput_widget.reload_domain
        simput_widget.register_layout(layout)

    with layout.toolbar as toolbar:
        layout.title.set_text("SimPut Advanced view")
        toolbar.dense = True
        vuetify.VSpacer()
        vuetify.VSwitch(
            label="Advanced",
            v_model=("ui_advanced", False),
            classes="mx-2",
            dense=True,
            hide_details=True,
        )

    with layout.content:
        simput.SimputItem(
            item_id=f"{item.id}",
        )

# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
