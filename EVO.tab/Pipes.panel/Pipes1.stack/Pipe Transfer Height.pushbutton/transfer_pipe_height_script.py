import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import Document, Transaction
from Autodesk.Revit.UI import UIDocument
from Autodesk.Revit.UI.Selection import Selection, ISelectionFilter, ObjectType
from Autodesk.Revit.Exceptions import OperationCanceledException

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
trans = Transaction(doc)
selection = uidoc.Selection

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

def GetParameterByName(element, parameter_name):
    for para in element.Parameters:
        if para.Definition.Name == parameter_name:
            return para
            break

def TransferParameterValue(element_1, element_2, parameter_name):
    para_1 = GetParameterByName(element_1, parameter_name)
    para_2 = GetParameterByName(element_2, parameter_name)

    para_value = para_2.Set(para_1.AsDouble())
    return para_value

def PipeSelection(uidocument, selection_filter, string):
    try:
        ref = uidocument.Selection.PickObject(ObjectType.Element, selection_filter, string)
        return ref
    except OperationCanceledException:
        pass

pipe_selection_filter = PipeSelectionFilter()

ref_1 = PipeSelection(uidoc, pipe_selection_filter, "Pick Reference Pipe")
ref_2 = PipeSelection(uidoc, pipe_selection_filter, "Pick Pipe to Change Height")

parameter_name = "Middle Elevation"

trans.Start("Change Pipe Height")
para_value = TransferParameterValue(doc.GetElement(ref_1.ElementId),doc.GetElement(ref_2.ElementId), parameter_name)
trans.Commit()