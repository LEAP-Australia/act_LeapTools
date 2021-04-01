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
import os

def ProjectSchematicNameToAnalysisName(arg):
    for analysis in ExtAPI.DataModel.Project.Model.Analyses:
        analysis.Name = analysis.SystemCaption
    
def rename():
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
    thread = System.Threading.Thread(System.Threading.ThreadStart(rename))
    thread.Start()

