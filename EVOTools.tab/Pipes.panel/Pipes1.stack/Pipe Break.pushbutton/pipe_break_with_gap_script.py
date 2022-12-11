import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import Document, Transaction
from Autodesk.Revit.DB.Plumbing import PlumbingUtils
from Autodesk.Revit.UI import UIDocument
from Autodesk.Revit.UI.Selection import Selection, ObjectType
from Autodesk.Revit.Exceptions import OperationCanceledException
from EVO.Selection import selection

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
trans = Transaction(doc)


pipe_selection_filter = selection.CategorySelectionFilter("Pipes")

def BreakPipeOnSelectedPoint(uidocument, SelectionFilter):
    try:
        selection = uidocument.Selection.PickObject(ObjectType.Element, SelectionFilter, "Pick Point on Pipe")
        break_pipe_id = PlumbingUtils.BreakCurve(uidocument.Document, selection.ElementId, selection.GlobalPoint)
        return break_pipe_id, True
    except OperationCanceledException:
        break_pipe_id = None
        return break_pipe_id, False

operation_canceled = True
while operation_canceled:
    trans.Start("Select Pipe")
    pipe_id, operation_canceled = BreakPipeOnSelectedPoint(uidoc, pipe_selection_filter)
    trans.Commit()
