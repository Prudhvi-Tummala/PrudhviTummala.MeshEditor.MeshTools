import omni.ext
import omni.ui as ui
from pxr import Usd, UsdGeom, Gf
import numpy as np
import omni.kit.app
import os
ext_path = os.path.dirname(os.path.realpath(__file__))



from .SplitTool import Split_Tools
from .SliceTool import Slice_Tools
from .MergeMesh import mergeMesh

Split_Tools = Split_Tools()
Slice_Tools = Slice_Tools()
mergeMesh = mergeMesh()

class MeshToolsWindow:
    def on_startup(self,ext_id):
        def button1_clicked():
            Split_Tools.splitMesh()
        def button2_clicked():
            plane = sliderInt.model.as_int
            planeValue = fieldFloat.model.as_int
            Slice_Tools.sliceMesh(plane,planeValue)
            Slice_Tools.delPlane()
        def button_merge():
            mergeMesh.merge_mesh()
        def button3_clicked():
            minBBox, maxBBox = Slice_Tools.boundingbox()
            plane = sliderInt.model.as_int
            sliderFloat.min = minBBox[plane]
            sliderFloat.max = maxBBox[plane]
            planeValue = fieldFloat.model.as_int
            Slice_Tools.createplane(plane,planeValue,minBBox,maxBBox)
        def planechange():
            plane = sliderInt.model.as_int
            planeValue = fieldFloat.model.as_int
            Slice_Tools.modifyplane(plane,planeValue)
        def deleteplane():
            Slice_Tools.delPlane()

        self._window = ui.Window("My Window", width=300, height=500)
        with self._window.frame:
            with ui.VStack(height = 0):
                with ui.CollapsableFrame("split and merge mesh"):
                    with ui.HStack():
                        ui.Button("Split Mesh",image_url =f'{ext_path}/Imgs/Split_Meshes.PNG',  image_height = 140 ,width = 140, clicked_fn = button1_clicked)
                        ui.Button("Merge Mesh",image_url =f'{ext_path}/Imgs/Merge.PNG',  image_height = 140 ,width = 140 , clicked_fn = button_merge)
                with ui.CollapsableFrame("Slice mesh with plane"):
                    with ui.VStack(height = 0):
                        ui.Label("| YZ : 0 | ZX : 1 | XY : 2 |")
                        with ui.HStack():
                            sliderInt = ui.IntSlider(min=0,max = 2)
                            ui.Button("Start",width = 80, height = 30 , clicked_fn = button3_clicked )
                        sliderInt.tooltip = "For slicing plane give 0 for YZ plane, 1 for ZX, 2 for XY"
                        with ui.HStack():
                            fieldFloat = ui.StringField(width = 50)
                            sliderFloat = ui.FloatSlider(min=0,max=50)
                        sliderFloat.model = fieldFloat.model
                        sliderFloat.model.add_value_changed_fn(lambda m:planechange())
                        with ui.HStack():
                            ui.Button("Slice Mesh",image_url =f'{ext_path}/Imgs/Slicing_Mesh.PNG',  image_height = 140 ,width = 140,clicked_fn = button2_clicked)
                            ui.Button('Delete Plane',image_url =f'{ext_path}/Imgs/Delete.PNG',  image_height = 140 ,width = 140,clicked_fn = deleteplane) 
    
