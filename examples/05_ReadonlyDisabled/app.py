from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import simput
from trame_simput import get_simput_manager

server = get_server()
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Simput initialization
# -----------------------------------------------------------------------------

simput_manager = get_simput_manager()
simput_manager.load_model(yaml_file=Path(__file__).with_name("model.yaml"))
simput_manager.load_ui(xml_file=Path(__file__).with_name("ui.xml"))

simput_widget = simput.Simput(simput_manager, prefix="simput", trame_server=server)
item = simput_manager.proxymanager.create("ExampleModel")

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    simput_widget.register_layout(layout)

    with layout.toolbar as toolbar:
        layout.title.set_text("Simput readonly and disabled example")
        toolbar.dense = True

    with layout.content:
        simput.SimputItem(
            item_id=f"{item.id}",
        )

# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
