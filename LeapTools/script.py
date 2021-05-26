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
# pylint: disable=invalid-name, unused-argument
# pylint: good-names=ExtAPI

import os

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
        mysys.append(mydir.replace("-"," "))

    cmd = ''
    for i in range(0,len(mysys)):
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
        parent = ExtAPI.DataModel.CreateObject("DirectRPContainer","LeapTools")
    parent.CreateChild("DirectRP")


def DirectRpScopingIsValid(rpObj, prop):
    'Check if RP geom selection is valid'
    if prop.Value is not None:
        return prop.Value.Ids.Count == 1 
    else:
        return False


def WriteRpInput(obj, solverData, stream):
    'Write Direct RP APDL commands'
    ExtAPI.Log.WriteError('TESTTTTT')
