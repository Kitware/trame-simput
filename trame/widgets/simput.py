from trame_simput.widgets.simput import *


def initialize(server):
    from trame_simput import module

    server.enable_module(module)
