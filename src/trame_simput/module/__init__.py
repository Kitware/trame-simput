from pathlib import Path
from .protocol import SimputProtocol

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())

# Serve directory for JS/CSS files
serve = {"__trame_simput": serve_path}

# List of JS files to load (usually from the serve path above)
scripts = []

# List of Vue plugins to install/load
vue_use = ["trame_simput"]


def setup(server, **kargs):
    server.add_protocol_to_configure(
        lambda root_protocol: root_protocol.registerLinkProtocol(SimputProtocol())
    )

    client_type = "vue2"
    if hasattr(server, "client_type"):
        client_type = server.client_type

    global scripts

    if client_type == "vue2":
        scripts = ["__trame_simput/vue-trame_simput.umd.min.js"]
    elif client_type == "vue3":
        scripts = ["__trame_simput/vue3-trame_simput.umd.js"]
    else:
        raise TypeError(
            f"Trying to initialize trame_simput with unknown client_type={client_type}"
        )
