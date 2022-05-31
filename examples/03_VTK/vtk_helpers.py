from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa


class View:
    def __init__(self):
        self._renderer = vtkRenderer()
        self._renderWindow = vtkRenderWindow()
        self._renderWindow.AddRenderer(self._renderer)
        self._renderWindowInteractor = vtkRenderWindowInteractor()
        self._renderWindowInteractor.SetRenderWindow(self._renderWindow)
        self._renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        self._renderWindowInteractor.EnableRenderOff()
        self._representations = []

    def SetRepresentations(self, reps):
        pass

    def GetRepresentations(self):
        return self._representations

    @property
    def render_window(self):
        return self._renderWindow

    @property
    def renderer(self):
        return self._renderer

    def ResetCamera(self):
        self._renderer.ResetCamera()


class Representation:
    def __init__(self):
        self.mapper = vtkPolyDataMapper()
        self.actor = vtkActor()
        self.actor.SetMapper(self.mapper)
        self._view = None
        self._input = None
        self.actor.SetVisibility(0)

    def SetView(self, view):
        if self._view and self._view != view:
            self._view.renderer.RemoveActor(self.actor)

        self._view = view
        if self._view:
            self._view.renderer.AddActor(self.actor)

    def GetView(self):
        return self._view

    def SetInput(self, algo):
        self.actor.SetVisibility(0)
        self._input = algo
        if self._input:
            self.actor.SetVisibility(1)
            self.mapper.SetInputConnection(self._input.GetOutputPort())

    def GetInput(self):
        return self._input
