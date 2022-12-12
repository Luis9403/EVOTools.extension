import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import Document, Transaction
from Autodesk.Revit.UI import UIDocument
from Autodesk.Revit.UI.Selection import Selection, ISelectionFilter, ObjectType
from Autodesk.Revit.Exceptions import OperationCanceledException
from EVO.Selection.selection import CategorySelectionFilter
from EVO.parameters import ElementParameters

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
trans = Transaction(doc)
selection = uidoc.Selection


def PipeSelection(uidocument, selection_filter, string):
    try:
        ref = uidocument.Selection.PickObject(ObjectType.Element, selection_filter, string)
        return ref
    except OperationCanceledException:
        pass

pipe_selection_filter = CategorySelectionFilter("Pipes")

ref_1 = PipeSelection(uidoc, pipe_selection_filter, "Pick Reference Pipe")
ref_2 = PipeSelection(uidoc, pipe_selection_filter, "Pick Pipe to Change Height")


element_parameters = ElementParameters(doc.GetElement(ref_1.ElementId))
trans.Start("Change Pipe Height")
para_value = element_parameters.TransferParameterValue(doc.GetElement(ref_2.ElementId), "Middle Elevation")
trans.Commit()