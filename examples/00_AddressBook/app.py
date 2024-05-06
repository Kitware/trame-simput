from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3 as vuetify, simput

from trame_simput import get_simput_manager

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type="vue3")
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

DEF_DIR = Path(__file__).with_name("definitions")

simput_manager = get_simput_manager()
simput_manager.load_model(yaml_file=DEF_DIR / "model.yaml")
simput_manager.load_ui(xml_file=DEF_DIR / "ui.xml")


@state.change("lang")
def update_lang(lang, **kwargs):
    simput_manager.load_language(yaml_file=DEF_DIR / f"lang_{lang}.yaml")


# -----------------------------------------------------------------------------
# Business logic
# -----------------------------------------------------------------------------


class AddressBook:
    MODEL_TYPE = "Person"

    def __init__(self, server, pxm):
        self._state = server.state
        self._pxm = pxm

        # state
        self.update_state()

        # ctrl
        ctrl = server.controller
        ctrl.address_book_add = self.create_entry
        ctrl.address_book_remove = self.delete_active

    def create_entry(self):
        person = self._pxm.create(AddressBook.MODEL_TYPE)
        self.update_state(person.id)

    def delete_active(self):
        if self.active_id:
            self._pxm.delete(self.active_id)
            self.update_state()

    def update_state(self, active_id=None):
        if active_id:
            self._state.active_ids = [active_id]
        else:
            self._state.active_ids = []
        self._state.person_ids = self.entry_ids

    @property
    def active_id(self):
        return self._state.active_ids[0] if len(self._state.active_ids) > 0 else None

    @property
    def entry_ids(self):
        return [p.id for p in self._pxm.get_instances_of_type(AddressBook.MODEL_TYPE)]


# -----------------------------------------------------------------------------
# Graphical Interface
# -----------------------------------------------------------------------------

btn_styles = {
    "classes": "mx-2",
    "size": "small",
    "variant": "outlined",
}

compact_styles = {
    "hide_details": True,
    "density": "compact",
}

# -----------------------------------------------------------------------------
# Simput container initialization
# -----------------------------------------------------------------------------

simput_widget = simput.Simput(simput_manager, prefix="ab", trame_server=server)
ctrl.simput_apply = simput_widget.apply
ctrl.simput_reset = simput_widget.reset

# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------

with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("SimPut Address Book")
    simput_widget.register_layout(layout)

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            v_model=("lang", "en"),
            items=(
                "options",
                [
                    {"title": "English", "value": "en"},
                    {"title": "Francais", "value": "fr"},
                ],
            ),
            **compact_styles,
        )
        vuetify.VSwitch(
            classes="mx-2",
            v_model="abAutoApply",
            color="primary",
            label="Auto apply",
            **compact_styles,
        )
        with vuetify.VBtn(
            **btn_styles,
            disabled=["!abChangeSet"],
            click=ctrl.simput_apply,
        ):
            with vuetify.VBadge(
                content=["abChangeSet"],
                model_value=["abChangeSet"],
            ):
                vuetify.VIcon("mdi-database-import", size="x-large")

        vuetify.VBtn(
            **btn_styles,
            disabled=["!abChangeSet"],
            click=ctrl.simput_reset,
            icon="mdi-undo-variant",
        )

        vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VBtn(
            **btn_styles,
            disabled=("active_ids.length === 0",),
            click=ctrl.address_book_remove,
            icon="mdi-minus",
        )

        vuetify.VBtn(click=ctrl.address_book_add, **btn_styles, icon="mdi-plus")

    with layout.drawer:
        with vuetify.VList(
            density="compact",
            select_strategy="single-leaf",
            selected=("active_ids",),
            update_selected="active_ids = $event",
            color="primary",
        ):
            with vuetify.VListItem(
                v_for="(id, i) in person_ids",
                key="i",
                value=("id",),
            ):
                with vuetify.VListItemTitle():
                    simput.SimputItem(
                        "{{FirstName}} {{LastName}}",
                        item_id="id",
                        no_ui=True,
                        extract=["FirstName", "LastName"],
                    )

    with layout.content:
        with vuetify.VContainer(fluid=True):
            simput.SimputItem(item_id=("active_ids[0]", None))


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    engine = AddressBook(server, simput_manager.proxymanager)
    server.start()
