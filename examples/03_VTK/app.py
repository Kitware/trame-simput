from pathlib import Path

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, simput, html, trame, vtk

from trame_simput import get_simput_manager

from vtk_adaper import VTKAdapter, VTKFactory
from vtk_helpers import View, Representation

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

state.import_file = None
state.export_content = None

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

DEF_DIR = Path(__file__).with_name("definitions")

simput_manager = get_simput_manager(
    object_factory=VTKFactory(),
    object_adapter=VTKAdapter(),
)
simput_manager.load_model(yaml_file=DEF_DIR / "model.yaml")
simput_manager.load_ui(xml_file=DEF_DIR / "ui.xml")

PXM = simput_manager.proxymanager
TYPES = PXM.types()

# -----------------------------------------------------------------------------
# VTK management
# -----------------------------------------------------------------------------

view = View()


def on_change(topic, ids=None, **kwargs):
    if topic == "deleted":
        update_sources()

    if topic == "created":
        for obj_id in ids:
            obj_vtk = PXM.get(obj_id).object
            rep = Representation()
            rep.SetView(view)
            rep.SetInput(obj_vtk)
        update_sources()

    ctrl.view_update()


PXM.on(on_change)

# -----------------------------------------------------------------------------
# Data management
# -----------------------------------------------------------------------------


def update_sources(*args, **kwargs):
    ids = list(map(lambda p: p.id, PXM.tags("Source")))
    state.source_ids = ids
    ctrl.view_update()


def create_object(name, type):
    obj = PXM.create(type, _name=name)
    obj.fetch()
    state.active_id = obj.id


# Init source_ids at startup
ctrl.on_server_ready.add(update_sources)

# -----------------------------------------------------------------------------
# Import / Export
# -----------------------------------------------------------------------------


def export_state():
    state.export_content = PXM.save()


@state.change("import_file")
def import_file(import_file, **kwargs):
    if import_file is None:
        return

    if import_file:
        json_content = import_file.get("content").decode("utf-8")
        PXM.load(file_content=json_content)

    # reset current import
    state.import_file = None


# -----------------------------------------------------------------------------
# Simput container initialization
# -----------------------------------------------------------------------------

simput_widget = simput.Simput(simput_manager, prefix="simput", trame_server=server)
ctrl.simput_apply = simput_widget.apply
ctrl.simput_reset = simput_widget.reset

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

ICONS = [
    "mdi-format-list-bulleted-type",
    "mdi-plus",
    "mdi-pencil-outline",
]

with SinglePageWithDrawerLayout(server) as layout:
    simput_widget.register_layout(layout)

    with layout.drawer as drawer:
        with vuetify.VTabs(
            v_model=("drawer_mode", 0),
            dense=True,
            center_active=True,
        ):
            for icon in ICONS:
                with vuetify.VTab():
                    vuetify.VIcon(icon)
        with vuetify.VTabsItems(v_model=("drawer_mode", 0)):
            with vuetify.VTabItem():
                with vuetify.VList(dense=True):
                    with vuetify.VListItemGroup(
                        v_model=("active_id", 0), color="primary"
                    ):
                        with vuetify.VListItem(
                            v_for="(id, i) in source_ids",
                            key="i",
                            value=("id",),
                        ):
                            with vuetify.VListItemContent():
                                with vuetify.VListItemTitle():
                                    simput.SimputItem(
                                        "{{ data.name }}",
                                        item_id="id",
                                        no_ui=True,
                                        v_slot="{ data }",
                                    )

            with vuetify.VTabItem():
                with vuetify.VCard():
                    with vuetify.VCardText():
                        with vuetify.VRow():
                            with vuetify.VCol():
                                vuetify.VSelect(
                                    v_model=("obj_type", ""),
                                    items=("obj_types", TYPES),
                                    dense=True,
                                    hide_details=True,
                                    change="obj_name = $event",
                                )
                            with vuetify.VCol():
                                vuetify.VTextField(
                                    v_model=("obj_name", ""),
                                    clearable=True,
                                    dense=True,
                                    hide_details=True,
                                )
                    with vuetify.VCardActions():
                        vuetify.VSpacer()
                        vuetify.VBtn(
                            "Create", click=(create_object, "[obj_name, obj_type]")
                        )

            with vuetify.VTabItem():
                simput.SimputItem(item_id="active_id")

    with layout.toolbar as toolbar:
        layout.title.set_text("VTK")
        toolbar.dense = True
        vuetify.VSpacer()

        vuetify.VDivider(vertical=True, classes="mx-1")

        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                with vuetify.VBtn(
                    v_bind="attrs",
                    v_on="on",
                    icon=True,
                    click="document.getElementById('importFile').click();",
                ):
                    vuetify.VIcon("mdi-database-import-outline")
                    html.Input(
                        id="importFile",
                        type="file",
                        style="display: none",
                        change="import_file=$event.target.files[0]",
                        __events=["change"],
                    )

            html.Span("Import State")

        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                with vuetify.VBtn(
                    v_bind="attrs",
                    v_on="on",
                    icon=True,
                    click=export_state,
                ):
                    vuetify.VIcon("mdi-database-export-outline")
                    trame.ClientStateChange(
                        value="export_content",
                        change="export_content && utils.download('VTKState.json', export_content)",
                    )
            html.Span("Export State")

        vuetify.VDivider(vertical=True, classes="mx-1")

        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                with vuetify.VBtn(
                    v_bind="attrs",
                    v_on="on",
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

            html.Span("Apply Changes")

        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                with vuetify.VBtn(
                    v_bind="attrs",
                    v_on="on",
                    classes="mx-2",
                    small=True,
                    outlined=True,
                    icon=True,
                    disabled=("!simputChangeSet",),
                    click=ctrl.simput_reset,
                ):
                    vuetify.VIcon("mdi-undo-variant")
            html.Span("Reset Changes")

        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                with vuetify.VBtn(
                    v_bind="attrs",
                    v_on="on",
                    icon=True,
                    click=ctrl.view_reset_camera,
                ):
                    vuetify.VIcon("mdi-crop-free")

            html.Span("Reset Camera")

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="fill-height pa-0"):
            html_view = vtk.VtkLocalView(
                view.render_window,
                on_ready=ctrl.view_reset_camera,
            )
            ctrl.view_update = html_view.update
            ctrl.view_reset_camera = html_view.reset_camera

# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
