import omni.ext
import omni.ui as ui
from pxr import Usd, UsdGeom, Gf
import numpy as np
import omni.kit.app
import os

class Split_Tools:
    def splitMesh(self):
        stage = omni.usd.get_context().get_stage()
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        for prim_path in prim_paths:
            # Define a new Mesh primitive
            prim_mesh = stage.GetPrimAtPath(prim_path)
            split_mesh =  UsdGeom.Mesh(prim_mesh)
            faceVertexIndices1 = split_mesh.GetFaceVertexIndicesAttr().Get()
            faceVertexCounts1 = split_mesh.GetFaceVertexCountsAttr().Get()

            points1 = split_mesh.GetPointsAttr().Get()
            meshshape  = np.unique(faceVertexCounts1,return_index= False)
            if len(meshshape) > 1:
                print('non-uniform mesh')
                return
                
            faceVertexIndices1 = np.array(faceVertexIndices1)
            faceVertexIndices1 = np.asarray(faceVertexIndices1.reshape(-1,meshshape[0]))
            
            def splitmeshes(groups):
                meshes = []
                sorted_ref = []

                flag = 0

                for group in groups:
                    if not meshes:
                        meshes.append(group)
                    else:
                        notinlist = True
                        for i in range(0,len(meshes)):
                            if len(np.intersect1d(group.reshape(1,-1),meshes[i].reshape(1,-1))) > 0:
                                meshes[i] = np.concatenate([meshes[i],group])
                                notinlist = False
                        if notinlist:
                            meshes.append(group)
                        
                if len(meshes) == len(groups):
                    return [meshes, sorted_ref]

                else:
                    
                    return(splitmeshes(meshes))

            meshsoutput , referceoutput = splitmeshes(faceVertexIndices1)

            if len(meshsoutput) == 1:
                print('Connex mesh: no actin taken')
                return
            i = 1 
            for meshoutput in meshsoutput:
                uniqIndi = np.unique(meshoutput.reshape(1,-1),return_index=False)
                uniqIndi = np.sort(uniqIndi)
                points1 = np.asarray(points1)
                meshpoints = np.array(points1[uniqIndi])
                connexMeshIndi_adjsuted = np.searchsorted(uniqIndi,meshoutput.reshape(1,-1))[0]
                counts = np.zeros(int(len(meshoutput)/3)) + meshshape
                mesh = UsdGeom.Mesh.Define(stage, f'/NewMesh_{i}')


                # Define the points of the mesh
                mesh.CreatePointsAttr(meshpoints)

                # Define the faces of the mesh
                mesh.CreateFaceVertexCountsAttr(counts)
                mesh.CreateFaceVertexIndicesAttr(connexMeshIndi_adjsuted)
                i = i+1
            next
