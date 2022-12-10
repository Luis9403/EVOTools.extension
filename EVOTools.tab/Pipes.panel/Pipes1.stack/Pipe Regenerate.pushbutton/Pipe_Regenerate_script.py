import clr
import math

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Plumbing import *

# set active document and document UI
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

class PipeSelectionFilter(ISelectionFilter):
    def __init__(self):
        pass

    def AllowElement(self, element):
        if element.Cotegory.Name == "Pipes":
            return True
        else:
            return False
    
    def AllowReference(self, reference):
        return False


def PipeSelection(uidocument, selection_filter, string):
    try:
        ref = uidocument.Selection.PickObject(ObjectType.Element, selection_filter, string)
        return ref
    except OperationCanceledException:
        pass


pipe_selection_filter = PipeSelectionFilter()
trans = Transaction(doc, "Split Pipe by two points")

pipe_ref = PipeSelection(uidoc, pipe_selection_filter, "Select Pipe")

pipe = doc.GetElement(pipe_ref.ElementId)
pipe_reference_level = pipe.ReferenceLevel.Id
pipe_type = pipe.PipeType.Id
connectors = pipe.ConnectorManager.Connectors

linked_connectors = []
for connector in connectors:
    if connector.IsConnected():
        linked_connector = connector.GetMEPConnectorInfo().LinkedConnector
        linked_connectors.append(linked_connector)
    else:
        pass

new_pipe = Pipe.Create(doc, pipe_type, pipe_reference_level, linked_connectors[0], linked_connectors[1])