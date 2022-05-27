from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, simput, html, trame, vtk

from trame_simput import get_simput_manager

from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkSphereSource,
    vtkCylinderSource,
)
from vtkHelper import View, Representation

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

DEF_DIR = Path(__file__).with_name("definitions")

simput_manager = get_simput_manager()
simput_manager.load_model(yaml_file=DEF_DIR / "model.yaml")
simput_manager.load_ui(xml_file=DEF_DIR / "ui.xml")

TYPES = simput_manager.proxymanager.types()

# -----------------------------------------------------------------------------
# Old code base
# -----------------------------------------------------------------------------
# app.state = {
#     # UI toggle for drawer
#     "showMenu": True,
#     # Data handling
#     "activeId": None,
#     "sourceIds": [],
#     # Object creation
#     "objName": "",
#     "objType": "",
#     "obj_types": [],
#     # 3D view
#     "view": None,
#     # Import/Export
#     "importFile": None,
#     "exportContent": None,
# }
# -----------------------------------------------------------------------------
# For VTK object creation
# vtk_factory = ObjectFactory()
# vtk_factory.register("Cone", vtkConeSource)
# vtk_factory.register("Sphere", vtkSphereSource)
# vtk_factory.register("Cylinder", vtkCylinderSource)

# -----------------------------------------------------------------------------
# VTK management
# -----------------------------------------------------------------------------

allow_reset_camera_on_ready = True
view = View()

# -----------------------------------------------------------------------------
# Data management
# -----------------------------------------------------------------------------


# def update_sources(*args, **kwargs):
#     ids = list(map(lambda p: p.id, pxm.tags("Source")))
#     app.set("sourceIds", ids)


# # -----------------------------------------------------------------------------


# def update_view(*args, **kwargs):
#     ic("update_view")
#     app.set("view", VTK.scene(view.render_window))
#     app.set("exportContent", None)


# # -----------------------------------------------------------------------------


# @app.trigger("create")
# def create_object(name, type):
#     obj = pxm.create(type, _name=name)
#     print(obj.list_property_names())
#     fetch(obj, obj.list_property_names())
#     app.set("activeId", obj.id)


# # -----------------------------------------------------------------------------


# @app.trigger("delete")
# def delete_object(obj_id):
#     active_id = app.get("activeId")
#     pxm.delete(obj_id)
#     if active_id == obj_id:
#         app.set("activeId", None)


# # -----------------------------------------------------------------------------


# @app.trigger("viewReady")
# def on_ready():
#     global allow_reset_camera_on_ready
#     if allow_reset_camera_on_ready:
#         allow_reset_camera_on_ready = False
#         app.update(ref="view", method="resetCamera")


# # -----------------------------------------------------------------------------


# def on_change(topic, ids=None, **kwargs):
#     if topic == "deleted":
#         update_sources()

#     if topic == "created":
#         for obj_id in ids:
#             obj_vtk = pxm.get(obj_id).object
#             rep = Representation()
#             rep.SetView(view)
#             rep.SetInput(obj_vtk)
#         update_sources()

#     update_view()


# pxm.on(on_change)

# # -----------------------------------------------------------------------------
# # Import / Export
# # -----------------------------------------------------------------------------


# @app.change("importFile")
# def import_file():
#     file_data = app.get("importFile")
#     if file_data:
#         json_content = file_data.get("content").decode("utf-8")
#         pxm.load(file_content=json_content)

#     # reset current import
#     app.set("importFile", None)


# # -----------------------------------------------------------------------------


# @app.trigger("export")
# def export_state():
#     app.set("exportContent", pxm.save())


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
    layout.root = simput_widget

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
                            "Create", click=(ctrl.create, "[obj_name, obj_type]")
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
                    v_bind="attrs", v_on="on", icon=True, click=ctrl.export
                ):
                    vuetify.VIcon("mdi-database-export-outline")
                    trame.ClientStateChange(
                        value="exportContent",
                        change="exportContent && utils.download('VTKState.json', exportContent)",
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
        with vuetify.VContainer(fluid=True, v_if="active"):
            html_view = vtk.VtkLocalView(view.render_window)
            ctrl.view_update = html_view.update
            ctrl.view_reset_camera = html_view.reset_camera

# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
