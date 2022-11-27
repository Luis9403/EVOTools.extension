import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import Document, Transaction
from Autodesk.Revit.DB.Plumbing import PlumbingUtils
from Autodesk.Revit.UI import UIDocument
from Autodesk.Revit.UI.Selection import Selection, ISelectionFilter, ObjectType
from Autodesk.Revit.Exceptions import OperationCanceledException


uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
trans = Transaction(doc)

class PipeSelectionFilter(ISelectionFilter):
    def __init__(self):
        pass
    
    def AllowElement(self, element):
        if element.Category.Name == "Pipes":
            return True
        else:
            return False

    def AllowReference(self, reference):
        return False

pipe_selection_filter = PipeSelectionFilter()

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
