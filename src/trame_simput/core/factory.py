from .proxy import ProxyManager
from .ui import UIManager, resolvers

UI_MANAGERS = {}


def get_simput_manager(
    id=None, pxm=None, resolver=None, object_factory=None, object_adapter=None
):
    global UI_MANAGERS
    if id is not None and id in UI_MANAGERS:
        return UI_MANAGERS[id]

    if pxm is None:
        pxm = ProxyManager(object_factory=object_factory, object_adapter=object_adapter)

    if resolver is None:
        resolver = resolvers.VuetifyResolver()

    ui_manager = UIManager(pxm, resolver)
    UI_MANAGERS[ui_manager.id] = ui_manager

    if id is not None:
        UI_MANAGERS[id] = ui_manager

    return ui_manager
