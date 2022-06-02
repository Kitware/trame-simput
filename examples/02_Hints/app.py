from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, simput

from trame_simput import get_simput_manager

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller


# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

YAML_MODEL = Path(__file__).with_name("model.yaml")

simput_manager = get_simput_manager()
simput_manager.load_model(yaml_file=YAML_MODEL)

# -----------------------------------------------------------------------------
# Generate Sample data
# -----------------------------------------------------------------------------

pxm = simput_manager.proxymanager
CHOICES = []
for obj_type in pxm.types():
    item = pxm.create(obj_type)
    CHOICES.append({"text": obj_type, "value": item.id})

# -----------------------------------------------------------------------------
# Simput container initialization
# -----------------------------------------------------------------------------

simput_widget = simput.Simput(simput_manager, prefix="simput", trame_server=server)
ctrl.simput_apply = simput_widget.apply
ctrl.simput_reset = simput_widget.reset

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.root = simput_widget

    with layout.toolbar as toolbar:
        layout.title.set_text("SimPut Widgets")
        toolbar.dense = True

        vuetify.VSpacer()

        vuetify.VSwitch(
            label="Apply",
            v_model=("simputAutoApply", False),
            classes="mx-2",
            dense=True,
            hide_details=True,
        )

        with vuetify.VBtn(
            classes="mx-2",
            small=True,
            outlined=True,
            icon=True,
            disabled=("!simputChangeSet",),
            click=ctrl.simput_apply,
        ):
            with vuetify.VBadge(
                content=("simputChangeSet", ""),
                offset_x=8,
                offset_y=8,
                value=("simputChangeSet", ""),
            ):
                vuetify.VIcon("mdi-database-import")

        with vuetify.VBtn(
            classes="mx-2",
            small=True,
            outlined=True,
            icon=True,
            disabled=("!simputChangeSet",),
            click=ctrl.simput_reset,
        ):
            vuetify.VIcon("mdi-undo-variant")

        vuetify.VSelect(
            v_model=("active", CHOICES[0].get("value")),
            items=("choices", CHOICES),
            dense=True,
            hide_details=True,
            style="max-width: 120px;",
        )

    with layout.content:
        with vuetify.VContainer(fluid=True, v_if="active"):
            simput.SimputItem(item_id="active")


# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
