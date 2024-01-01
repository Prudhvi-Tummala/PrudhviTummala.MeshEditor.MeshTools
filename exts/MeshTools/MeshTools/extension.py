import omni.ext
import omni.ui as ui
from pxr import Usd, UsdGeom, Gf
import numpy as np
import omni.kit.app
import os
from .MeshTools_Window import MeshToolsWindow
ext_path = os.path.dirname(os.path.realpath(__file__))
# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[MeshTools] some_public_function was called with x: ", x)
    return x ** x  

  
# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MeshtoolsExtension(omni.ext.IExt): 
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem. 
 
     
    def on_startup(self, ext_id):
        print("[MeshTools] MeshTools startup")
        self.MeshToolsWindow = MeshToolsWindow()
        self.MeshToolsWindow.on_startup(ext_id) 
 


            
 




    def on_shutdown(self):
        print("[MeshTools] MeshTools shutdown")



