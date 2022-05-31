from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkSphereSource,
    vtkCylinderSource,
)
from trame_simput.core.mapping import ProxyObjectAdapter, ObjectFactory
from trame_simput.core.proxy import Proxy

import logging

logger = logging.getLogger("vtk.adapter")
logger.setLevel(logging.ERROR)


class VTKAdapter(ProxyObjectAdapter):
    @staticmethod
    def commit(proxy):
        logger.info("Commit:")
        vtk_obj = proxy.object
        mt_start = vtk_obj.GetMTime()

        for name in proxy.edited_property_names:
            value = proxy[name]
            logger.info(f" - {name}: {value}")
            if isinstance(value, Proxy):
                value = value.object if value else None
            elif value is None:
                continue

            method_name = f"Set{name}"
            method = getattr(vtk_obj, method_name)
            method(value)

        return vtk_obj.GetMTime() - mt_start

    @staticmethod
    def reset(proxy, props_to_reset=[]):
        logger.info("Reset:")
        vtk_obj = proxy.object
        for name in props_to_reset:
            value = proxy[name]
            logger.info(f" - {name}: {value}")
            method_name = f"Set{name}"
            method = getattr(vtk_obj, method_name)
            method(value)

    @staticmethod
    def fetch(proxy):
        logger.info("Fetch:")
        vtk_obj = proxy.object
        change_set = {}
        for name in proxy.list_property_names():
            method_name = f"Get{name}"
            method = getattr(vtk_obj, method_name)

            if method is None:
                logger.error(f"No property {name} for proxy {proxy.type}")
                continue

            value = method()
            logger.info(f" - {name}: {value}")
            change_set[name] = value

        proxy.state = {"properties": change_set}
        proxy.commit()

    @staticmethod
    def update(proxy, *property_names):
        logger.info("Update:")
        vtk_obj = proxy.object
        for name in property_names:
            value = proxy[name]
            if isinstance(value, Proxy):
                value = value.object if value else None
            elif value is None:
                continue

            logger.info(f" - {name}: {value}")

            method_name = f"Set{name}"
            method = getattr(vtk_obj, method_name)
            method(value)

    @staticmethod
    def before_delete(proxy):
        pass


class VTKFactory(ObjectFactory):
    def __init__(self):
        super().__init__()
        self.register("Cone", vtkConeSource)
        self.register("Sphere", vtkSphereSource)
        self.register("Cylinder", vtkCylinderSource)
