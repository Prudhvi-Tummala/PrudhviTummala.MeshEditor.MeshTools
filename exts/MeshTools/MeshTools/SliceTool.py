import omni.ext
import omni.ui as ui
from pxr import Usd, UsdGeom, Gf
import numpy as np
import omni.kit.app
import omni.kit.commands
import os



class Slice_Tools:
    def sliceMesh(self,PlaneAxis,Plane):
        stage = omni.usd.get_context().get_stage()
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        if len(prim_paths) > 1:
            return
        for prim_path in prim_paths:
            # Define a new Mesh primitive

            prim_mesh = stage.GetPrimAtPath(prim_path)
            split_mesh =  UsdGeom.Mesh(prim_mesh)
            faceVertexIndices1 = np.array(split_mesh.GetFaceVertexIndicesAttr().Get())
            faceVertexCounts1 = np.array(split_mesh.GetFaceVertexCountsAttr().Get())
            points1 = np.array(split_mesh.GetPointsAttr().Get())
            indiBfrPlane = np.where(points1[:,PlaneAxis]<=Plane)
            indiAftrPlane = np.where(points1[:,PlaneAxis]>=Plane)
            faceVertexIndices1 = faceVertexIndices1.reshape(-1,3)

            shape = np.unique(faceVertexCounts1)

            if len(shape) > 1 :
                print('non-uniform mesh')
                return
            if not shape[0] == 3:
                print('Only works for triangle mesh')
                return


            bfrPlane = []
            aftrPlane = []
            others = []

            pointsBfrPlane = np.array(points1[indiBfrPlane])
            pointsAftrPlane = np.array(points1[indiAftrPlane])

            for vertex in faceVertexIndices1:
                easy_split = False
                if len(np.intersect1d(vertex,indiBfrPlane)) == 3:
                    bfrPlane.append(vertex)
                    easy_split = True
                if len(np.intersect1d(vertex,indiAftrPlane)) == 3:
                    aftrPlane.append(vertex)
                    easy_split = True
                if not easy_split:
                    others.append(vertex)
            for vIndi in others:
                tri = points1[vIndi]
                bfr = np.where(tri[:,PlaneAxis]<Plane)
                aftr = np.where(tri[:,PlaneAxis]>Plane)
                solo_bfr = (len(bfr[0])== 1)
                if solo_bfr:
                    a = bfr[0][0]
                else:
                    a = aftr[0][0]
                b = (a+4)%3
                c = (a+5)%3
                dir_vector_d = tri[b]-tri[a]
                dir_vector_e = tri[c]-tri[a]
                cnst_d = (Plane - tri[a][PlaneAxis])/dir_vector_d[PlaneAxis]
                cnst_e = (Plane - tri[a][PlaneAxis])/dir_vector_e[PlaneAxis]
                point_d = tri[a] + (dir_vector_d*cnst_d)
                point_e = tri[a] + (dir_vector_e*cnst_e)
                pointsBfrPlane = np.append(pointsBfrPlane, [point_d])
                pointsBfrPlane = np.append(pointsBfrPlane, [point_e])
                pointsAftrPlane = np.append(pointsAftrPlane, [point_d])
                pointsAftrPlane = np.append(pointsAftrPlane, [point_e])
                max1 = np.max(np.array(bfrPlane).reshape(1,-1))
                max2 = np.max(np.array(aftrPlane).reshape(1,-1))
                if solo_bfr:
                    bfrPlane.append([vIndi[a],max1+1,max1+2])
                    aftrPlane.append([vIndi[b],vIndi[c],max2+1])
                    aftrPlane.append([vIndi[c],max2+2,max2+1])
                else:
                    bfrPlane.append([vIndi[b],vIndi[c],max1+1])
                    bfrPlane.append([vIndi[c],max1+2,max1+1])
                    aftrPlane.append([vIndi[a],max2+1,max2+2])
                
            uniq_bfr = np.sort(np.unique(np.array(bfrPlane).reshape(1,-1),return_index=False))
            uniq_aftr = np.sort(np.unique(np.array(aftrPlane).reshape(1,-1),return_index=False))
            nwIndiBfr = np.searchsorted(uniq_bfr,np.array(bfrPlane).reshape(1,-1))[0]
            nwIndiAftr = np.searchsorted(uniq_aftr,np.array(aftrPlane).reshape(1,-1))[0]
            mesh1 = UsdGeom.Mesh.Define(stage, '/Split_Mesh_1')
            pointsBfrPlane = np.array(pointsBfrPlane).reshape(-1,3)
            pointsAftrPlane = np.array(pointsAftrPlane).reshape(-1,3)
            mesh1.CreatePointsAttr(pointsBfrPlane)
            lnCntBfr = len(nwIndiBfr)/3
            triCntsBfr = np.zeros(int(lnCntBfr)) + 3
            print(len(pointsBfrPlane))
            print(np.max(nwIndiBfr))
            mesh1.CreateFaceVertexCountsAttr(triCntsBfr)
            mesh1.CreateFaceVertexIndicesAttr(nwIndiBfr)
            mesh2 = UsdGeom.Mesh.Define(stage, '/Split_Mesh_2')
            mesh2.CreatePointsAttr(pointsAftrPlane)
            lnCntAftr = len(nwIndiAftr)/3
            print(len(pointsAftrPlane))
            print(np.max(nwIndiAftr))
            triCntsAftr = np.zeros(int(lnCntAftr)) + 3
            mesh2.CreateFaceVertexCountsAttr(triCntsAftr)
            mesh2.CreateFaceVertexIndicesAttr(nwIndiAftr)

    def boundingbox(self):
        stage = omni.usd.get_context().get_stage()
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        if len(prim_paths) > 1:
            return
        if len(prim_paths) == 0:
            return
        print('fail')
        for prim_path in prim_paths:
            prim_mesh = stage.GetPrimAtPath(prim_path)
            split_mesh =  UsdGeom.Mesh(prim_mesh)
            UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"]).Clear()
            localBBox = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"]).ComputeWorldBound(prim_mesh)
            bbox = Gf.BBox3d(localBBox).GetBox()
            minbox = bbox.GetMin()
            maxbox = bbox.GetMax()
            return minbox, maxbox
        
    def createplane(self,plane,planeValue,minbox1,maxbox1):
        if plane == 0:
            point0 = [planeValue,minbox1[1]-5,minbox1[2]-5]
            point1 = [planeValue,minbox1[1]-5,maxbox1[2]+5]
            point2 = [planeValue,maxbox1[1]+5,maxbox1[2]+5]
            point3 = [planeValue,maxbox1[1]+5,minbox1[2]-5]
        elif plane == 1:
            point0 = [minbox1[0]-5,planeValue,minbox1[2]-5]
            point1 = [minbox1[0]-5,planeValue,maxbox1[2]+5]
            point2 = [maxbox1[0]+5,planeValue,maxbox1[2]+5]
            point3 = [maxbox1[0]+5,planeValue,minbox1[2]-5]
        else:
            point0 = [minbox1[0]-5,minbox1[1]-5,planeValue]
            point1 = [minbox1[0]-5,maxbox1[1]+5,planeValue]
            point2 = [maxbox1[0]+5,maxbox1[1]+5,planeValue]
            point3 = [maxbox1[0]+5,minbox1[1]-5,planeValue]
        points = [point0,point1,point2,point3]
        counts = [4]
        indicies = [0,1,2,3]
        stage = omni.usd.get_context().get_stage()
        mesh_plane = UsdGeom.Mesh.Define(stage, '/temp_plane')
        mesh_plane.CreatePointsAttr(points)
        mesh_plane.CreateFaceVertexCountsAttr(counts)
        mesh_plane.CreateFaceVertexIndicesAttr(indicies)
    
    def modifyplane(self,plane,planeValue):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath('/temp_plane')
        mesh_plane = UsdGeom.Mesh(prim )
        points = mesh_plane.GetPointsAttr().Get()
        points = np.array(points)
        changevalue = np.zeros(4) + planeValue
        points[:,plane] = changevalue
        counts = [4]
        indicies = [0,1,2,3]
        mesh_plane.CreatePointsAttr(points)
        mesh_plane.CreateFaceVertexCountsAttr(counts)
        mesh_plane.CreateFaceVertexIndicesAttr(indicies)

    def delPlane(self):
        omni.kit.commands.execute('DeletePrims',	paths=['/temp_plane'],destructive=False)

