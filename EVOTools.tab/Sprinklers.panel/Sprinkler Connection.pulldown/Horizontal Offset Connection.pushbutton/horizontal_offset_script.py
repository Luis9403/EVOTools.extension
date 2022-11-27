import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *

def GetSprinklerConnectorPosition(document, sprinkler_id):
    sprinkler_element = document.GetElement(sprinkler_id)
    sprinklers_connector_set = sprinkler_element.MEPModel.ConnectorManager.Connectors
    connectors_list = list(sprinklers_connector_set)
    connector = connectors_list[0]
    connector_coord = connector.Origin
    print(connector_coord)
    return connector_coord

def GetPerpendicularVectorFromVectorToPoint(point, vector):
    perpendicular_vector = vector.Multiply(((point.DotProduct(vector))/(vector.GetLength())**2))
    return perpendicular_vector

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
selection = uidoc.Selection

sprinkler_ref = selection.PickObject(ObjectType.Element, "Pick Sprinkler Head")
pipe_ref = selection.PickObject(ObjectType.Element, "Pick Sprinkler Head")

sprinkler_id = sprinkler_ref.ElementId
pipe_el = doc.GetElement(pipe_ref.ElementId)

pipe_direction_vector = pipe_el.Location.Curve.Origin
print(pipe_direction_vector.GetLength())
sprinkler_con_coord = GetSprinklerConnectorPosition(doc, sprinkler_id)

perpendicular_vector = GetPerpendicularVectorFromVectorToPoint(sprinkler_con_coord, pipe_direction_vector)

print(perpendicular_vector)