import clr
import math

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Plumbing import *

# set active document and document UI
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

selection = uidoc.Selection
trans = Transaction(doc, "Split Pipe by two points")

# select one point on a pipe
sel_1 = selection.PickObject(ObjectType.Edge, "Select Break Point")

# get pipe id and selected point coordinate
pipe_id = doc.GetElement(sel_1).Id
pt_1 = sel_1.GlobalPoint

trans_group = TransactionGroup(doc)
trans = Transaction(doc)

trans_group.Start("Change pipe height at point")
trans.Start("Break selected pipe")

break_pipe = PlumbingUtils.BreakCurve(doc, pipe_id, pt_1)

trans.Commit()

select_pipe = selection.PickObject(ObjectType.Element,"Select Pipe to Move")
pipe = doc.GetElement(select_pipe)

move_vector = XYZ(0,0,1)

trans.Start("Move Pipe")

move_pipe = pipe.Location.Move(move_vector)

trans.Commit()
trans_group.Assimilate()









