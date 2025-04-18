from pathlib import Path
from trame.app import get_server
from trame.widgets import simput, html

from trame_simput import get_simput_manager

client_type = "vue3"
use_client2 = client_type == "vue2"

if use_client2:
    from trame.ui.vuetify2 import SinglePageLayout
    from trame.widgets import vuetify2 as vuetify
else:
    from trame.ui.vuetify3 import SinglePageLayout
    from trame.widgets import vuetify3 as vuetify

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type=client_type)
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

DEF_DIR = Path(__file__).with_name("definitions")

simput_manager = get_simput_manager()

# -----------------------------------------------------------------------------
# Application state
# -----------------------------------------------------------------------------

pxm = simput_manager.proxymanager


def load_model():
    if use_client2:
        simput_manager.load_model(yaml_file=DEF_DIR / "model_vue2.yaml")
    else:
        simput_manager.load_model(yaml_file=DEF_DIR / "model_vue3.yaml")


load_model()

CHOICES = []
for obj_type in pxm.types():
    item = pxm.create(obj_type)
    if use_client2:
        CHOICES.append({"text": obj_type, "value": item.id})
    else:
        CHOICES.append({"title": obj_type, "value": item.id})

# -----------------------------------------------------------------------------


@state.change("use_xml_ui")
def update_ui(use_xml_ui, **kwargs):
    if use_xml_ui:
        simput_manager.load_ui(xml_file=DEF_DIR / "ui.xml")
    else:
        simput_manager.clear_ui()
        load_model()  # Needed to generate UI


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
    simput_widget.register_layout(layout)

    with layout.toolbar as toolbar:
        layout.title.set_text("SimPut Widgets")
        toolbar.dense = True
        vuetify.VSpacer()
        vuetify.VSwitch(
            label="UI",
            v_model=("use_xml_ui", False),
            classes="mx-2",
            dense=True,
            hide_details=True,
        )
        vuetify.VCheckbox(
            v_model=("showChangeSet", False),
            on_icon="mdi-bug",
            off_icon="mdi-shield-bug-outline",
            classes="mx-1",
            hide_details=True,
            dense=True,
        )
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
            variant="underlined",
            hide_details=True,
            style="max-width: 120px;",
        )

    with layout.content:
        with vuetify.VContainer(fluid=True, v_if="active"):
            html.Pre("{{ simputChangeSetContent }}", v_if="showChangeSet")
            simput.SimputItem(
                item_id="active",
            )

# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
