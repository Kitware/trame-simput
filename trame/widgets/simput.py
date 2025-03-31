from trame_simput.widgets.simput import *  # noqa: F403


def initialize(server):
    from trame_simput import module

    server.enable_module(module)
