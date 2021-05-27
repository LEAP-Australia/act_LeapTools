"""
main.py

Copyright 2021 LEAP Australia Pty Ltd

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author:
    Khesh Selvaganapathi

Discription:
    Change the analysis name according to the associated project schematic project name.
"""
# pylint: disable=invalid-name, unused-argument, undefined-variable

import os
import ansys

def ProjectSchematicNameToAnalysisName(arg):
    'Set system to project name'
    for analysis in ExtAPI.DataModel.Project.Model.Analyses:
        analysis.Name = analysis.SystemCaption


def rename():
    'Helper func to rename systems in a seprate thread'
    dirNames = []
    mynames = []
    for i in ExtAPI.DataModel.AnalysisList:
        dirNames.append(i.WorkingDir)
        mynames.append(i.Name)

    mysys = []
    for i in dirNames:
        a1 = os.path.split((os.path.split(i)[0]))[0]
        mydir = os.path.split(a1)[1]
        mysys.append(mydir.replace("-", " "))

    cmd = ''
    for i in range(0, len(mysys)):
        cmd += 'system = GetSystem(Name = "' + mysys[i] + '") \n'
        cmd += 'system.DisplayText = "' + mynames[i] + '"' + '\n'

    ExtAPI.Application.ScriptByName('journaling').ExecuteCommand(cmd)


def AnalysisNameToProjectSchematicName(arg):
    'Rename project based on Mechanical system name'
    thread = System.Threading.Thread(System.Threading.ThreadStart(rename))
    thread.Start()


def CreateDirectRemotePoint(analysis):
    'Create Direct RP parent and child objects'
    userObjects = ExtAPI.DataModel.GetUserObjects("LeapTools")
    parent = None
    for userObject in userObjects:
        if userObject.Name == "DirectRPContainer":
            parent = userObject
            break
    if not parent:
        parent = ExtAPI.DataModel.CreateObject("DirectRPContainer", "LeapTools")
    parent.CreateChild("DirectRP")


def DirectRpScopingIsValid(rpObj, prop):
    'Check if RP geom selection is valid'
    if prop.Value is not None:
        return prop.Value.Ids.Count == 1
    return False


def WriteRpInput(obj, solverData, stream):
    'Write Direct RP APDL commands'
    contactTypeId = solverData.GetNewElementType()
    targetTypeId = solverData.GetNewElementType()

    geoIds = obj.Properties["Geometry"].Value.Ids

    meshData = ExtAPI.DataModel.MeshDataByName("Global")
    nodeIds = set()
    for geoId in geoIds:
        geo_type = ExtAPI.DataModel.GeoData.GeoEntityById(geoId).Type
        for element in meshData.MeshRegionById(geoId).Elements:
            solverData.GetNewElementId()
        nodeIds.update(set(meshData.MeshRegionById(geoId).NodeIds))

    name = "directrp_{0}".format(obj.ObjectId)
    ansys.createNodeComponent(list(nodeIds), name, meshData, stream, False)
    stream.WriteLine("*set,tid,{0}".format(targetTypeId))
    stream.WriteLine("*set,cid,{0}".format(contactTypeId))
    if geo_type == GeoCellTypeEnum.GeoFace:
        stream.WriteLine("et,cid,174")
        stream.WriteLine("keyo,cid,12,5              ! Bonded Contact")
        if obj.Properties["DefPG/Behavior"].Value == "Rigid":
            pass
        stream.WriteLine("keyo,cid,4,1               ! Deformable RBE3 style load")
        stream.WriteLine("keyo,cid,2,2               ! MPC style contact")
    else:
        raise Exception("Not implemented for parent geo type")
    stream.WriteLine("et,tid,170")
    stream.WriteLine("keyo,tid,2,1               ! Don't fix the pilot node")
    dofs_sel = obj.Properties["DefPG/DOF Selection"].Value
    dofs = int('0b111111', 2)
    if dofs_sel == "All DoFs Active":
        dofs = dofs & int('0b111111', 2)
    else:
        if obj.Properties["DefPG/DOF Selection/X"].Value == "Inactive":
            dofs = dofs & int('0b111110', 2)
        elif obj.Properties["DefPG/DOF Selection/Y"].Value == "Inactive":
            dofs = dofs & int('0b111101', 2)
        elif obj.Properties["DefPG/DOF Selection/Z"].Value == "Inactive":
            dofs = dofs & int('0b111011', 2)
        elif obj.Properties["DefPG/DOF Selection/ROTX"].Value == "Inactive":
            dofs = dofs & int('0b110111', 2)
        elif obj.Properties["DefPG/DOF Selection/ROTY"].Value == "Inactive":
            dofs = dofs & int('0b101111', 2)
        elif obj.Properties["DefPG/DOF Selection/ROTZ"].Value == "Inactive":
            dofs = dofs & int('0b011111', 2)
    stream.WriteLine("keyo,tid,4,{0}".format(bin(dofs)[2:]))

    stream.WriteLine("type, cid")
    stream.WriteLine("mat, cid")
    stream.WriteLine("real, cid")
    stream.WriteLine("csys, 0")
    stream.WriteLine("CMSEL, S, {0}".format(name))
    stream.WriteLine("esurf")
    stream.WriteLine("allsel, all")

    if obj.Properties["Pilot"].Value.SelectionType == SelectionTypeEnum.GeometryEntities:
        geoIds = obj.Properties["Pilot"].Value.Ids
        for geoId in geoIds:
            pilotId = meshData.MeshRegionById(geoId).NodeIds[0]
            break
    else:
        pilotId = obj.Properties["Pilot"].Value.Ids[0]

    stream.WriteLine("*set,_npilot,{0}".format(pilotId))
    stream.WriteLine("type,tid")
    stream.WriteLine("mat ,cid")
    stream.WriteLine("real,cid")
    stream.WriteLine("tshape,pilo")
    stream.WriteLine("en,{0},_npilot".format(solverData.GetNewElementId()))
    stream.WriteLine("tshape")
