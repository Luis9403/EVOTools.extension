import clr
import math

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("System.Windows.Forms")
clr.AddReference("IronPython.Wpf")

import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Plumbing import *
from Autodesk.Revit.Exceptions import *

from pyrevit import script
xamlfile = script.get_bundle_file('ui.xaml')

import wpf
from System import Windows

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
uiapp = __revit__.Application

def GetClosestConnector(pipe1, pipe2):
    con_set1 = pipe1.ConnectorManager.Connectors
    con_set2 = pipe2.ConnectorManager.Connectors
    min_distance = 10000
    for con1 in con_set1:
        for con2 in con_set2:
            distance = con1.Origin.DistanceTo(con2.Origin)
            if min_distance > distance:
                min_distance = distance
                connectors = (con1, con2)
            else:
                continue
    return connectors

def BreakPipeInTwoPoints(uidocument):
    document = uidocument.Document
    break_points = []
    pipes = []
    sel_1 = uidocument.Selection.PickObject(ObjectType.Edge, "Select First Pipe Point")
    sel_2 = uidocument.Selection.PickObject(ObjectType.Edge, "Select Second Pipe Point")
    pipe_id = doc.GetElement(sel_1).Id
    break_points.append(sel_1.GlobalPoint)
    break_points.append(sel_2.GlobalPoint)
    for point in points:
        try:
            break_pipe = PlumbingUtils.BreakCurve(document, pipe_id, point)
            pipes.append(document.GetElement(break_pipe))
        except ArgumentException:        
                break_pipe = PlumbingUtils.BreakCurve(doc, break_pipe, point)
                pipes.insert(-1,document.GetElement(break_pipe))
    pipes.append(doc.GetElement(pipe_id))
    return pipes

def ConnectTwoPipes(document, pipe1, pipe2):
    connector_set = GetClosestConnector(pipe1, pipe2)
    new_pipe = Pipe.Create(document, pipe1.PipeType.Id, pipe1.ReferenceLevel.Id, connector_set[0], connector_set[1])
    connector_set1 = GetClosestConnector(pipe1, new_pipe)
    connector_set2 = GetClosestConnector(new_pipe, pipe2)
    document.Create.NewElbowFitting(connector_set1[0], connector_set1[1])
    document.Create.NewElbowFitting(connector_set2[0], connector_set2[1])

    return new_pipe

def PipeOffset(uidocument, offset):
    trans = Transaction(uidocument.Document)
    trans_group = TransactionGroup(uidocument.Document)

    trans_group.Start("Offset pipe vertically")
    # break the pipe on specified points
    trans.Start("Break selected pipe")
    new_pipes = BreakPipeInTwoPoints(uidocument)
    trans.Commit()

    # move pipe
    trans.Start("Move Pipe")
    new_pipes[1].Location.Move(XYZ(0, 0, offset))
    trans.Commit()

    # create new pipes and connect then
    trans.Start("Create New Pipes")
    for i in range(len(new_pipes)-1):
        ConnectTwoPipes(uidocument.Document, new_pipes[i], new_pipes[i+1])
    trans.Commit()
    trans_group.Assimilate()

class PipeOffsetEventHandler(IExternalEventHandler):
    def __init__(self, pipe_offset):
        self.pipe_offset = pipe_offset

    def Execute(self, uiapp):
        try:
            self.pipe_offset()
        except InvalidOperationException:
            TaskDialog.Show("Error Handler", "Exception Taken")

    def GetName(self):
        return "Make an offset in a pipe"

class MyWindows(Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self,xamlfile)

    def offset_pipe(self, sender, args):
        offset = self.textbox.Text
        offset_pipe_event_handler = PipeOffsetEventHandler(PipeOffset(uidoc, offset))
        external_event = ExternalEvent.Create(offset_pipe_event_handler)

        external_event.Raise()

MyWindows().ShowDialog()

# set active document and document UI







