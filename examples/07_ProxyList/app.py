from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout
from trame.widgets import vuetify2 as vuetify, simput, html

from trame_simput import get_simput_manager


# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

DEF_DIR = Path(__file__).with_name("definitions")

simput_manager = get_simput_manager()
simput_manager.load_model(yaml_file=DEF_DIR / "model.yaml")
simput_manager.load_ui(xml_file=DEF_DIR / "ui.xml")
simput_widget = simput.Simput(simput_manager, prefix="simput", trame_server=server)

address_book = simput_manager.proxymanager.create("AddressBook")


with SinglePageLayout(server) as layout:
    simput_widget.register_layout(layout)
    with layout.content:
        with vuetify.VContainer(fluid=True):
            simput.SimputItem(item_id=f"{address_book.id}")


if __name__ == "__main__":
    server.start()
