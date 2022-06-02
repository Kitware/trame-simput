from pathlib import Path
from .protocol import SimputProtocol

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())

# Serve directory for JS/CSS files
serve = {"__trame_simput": serve_path}

# List of JS files to load (usually from the serve path above)
scripts = ["__trame_simput/vue-trame_simput.umd.min.js"]

# List of Vue plugins to install/load
vue_use = ["trame_simput"]


def setup(server, **kwargs):
    server.add_protocol_to_configure(
        lambda root_protocol: root_protocol.registerLinkProtocol(SimputProtocol())
    )
