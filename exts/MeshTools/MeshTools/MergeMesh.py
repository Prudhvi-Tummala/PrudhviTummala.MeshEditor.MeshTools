import omni.ext
import omni.ui as ui
from pxr import Usd, UsdGeom, Gf
import numpy as np
import omni.kit.app
import omni.kit.commands
import os

class mergeMesh:
    def merge_mesh(self):
        stage = omni.usd.get_context().get_stage()
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        
        faceVertexCounts2 = np.array([])
        faceVertexIndices2 = np.array([])
        points2 =  np.array([])
        for prim_path in prim_paths:
            # Define a new Mesh primitive

            prim_mesh = stage.GetPrimAtPath(prim_path)
            split_mesh =  UsdGeom.Mesh(prim_mesh)
            faceVertexIndices1 = np.array(split_mesh.GetFaceVertexIndicesAttr().Get())
            faceVertexCounts1 = np.array(split_mesh.GetFaceVertexCountsAttr().Get())
            points1 = np.array(split_mesh.GetPointsAttr().Get())
            if not len(faceVertexIndices2) == 0:
                faceVertexIndices1 =faceVertexIndices1 +np.max(faceVertexIndices2) +1

            faceVertexIndices2 = np.append(faceVertexIndices2,faceVertexIndices1)
            points2 = np.append(points2,points1)
            faceVertexCounts2 = np.append(faceVertexCounts2,faceVertexCounts1)
        
        combinedMesh = UsdGeom.Mesh.Define(stage,'/combinedMesh')
        combinedMesh.CreatePointsAttr(points2)
        combinedMesh.CreateFaceVertexIndicesAttr(faceVertexIndices2)
        combinedMesh.CreateFaceVertexCountsAttr(faceVertexCounts2)

        