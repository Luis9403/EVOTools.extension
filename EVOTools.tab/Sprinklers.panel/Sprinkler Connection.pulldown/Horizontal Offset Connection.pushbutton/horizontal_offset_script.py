import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Plumbing import *

def GetSprinklerConnectorPosition(document, sprinkler_id):
    sprinkler_element = document.GetElement(sprinkler_id)
    sprinklers_connector_set = sprinkler_element.MEPModel.ConnectorManager.Connectors
    connectors_list = list(sprinklers_connector_set)
    connector = connectors_list[0]
    connector_coord = connector.Origin
    return connector_coord

def GetOrtogonalProjectionOfVector(vector_1, vector_2):
    ortogonal_vector = vector_2.Multiply(((vector_1.DotProduct(vector_2))/(vector_2.GetLength())**2))
    return ortogonal_vector

def GetProjectionOfVector(vector_1, vector_2):
    projection_vector = vector_1 - vector_2.Multiply(((vector_1.DotProduct(vector_2))/(vector_2.GetLength())**2))
    return projection_vector

def GetPipeDirectionVector(pipe):
    loc_line = pipe.Location.Curve
    start_point = loc_line.GetEndPoint(0)
    end_point = loc_line.GetEndPoint(1)
    direction_vector = start_point.Subtract(end_point)
    return direction_vector


uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
selection = uidoc.Selection
trans = Transaction(doc)

sprinkler_ref = selection.PickObject(ObjectType.Element, "Pick Sprinkler Head")
pipe_ref = selection.PickObject(ObjectType.Element, "Pick Sprinkler Head")

sprinkler_id = sprinkler_ref.ElementId
pipe_el = doc.GetElement(pipe_ref.ElementId)

pipe_direction_vector = GetPipeDirectionVector(pipe_el)
sprinkler_con_coord = GetSprinklerConnectorPosition(doc, sprinkler_id)

ortogonal_vector = GetOrtogonalProjectionOfVector(sprinkler_con_coord, pipe_direction_vector)
projection_vector = GetProjectionOfVector(sprinkler_con_coord, pipe_direction_vector)
point_on_pipe = pipe_ref.GlobalPoint

offset_vector = GetProjectionOfVector(ortogonal_vector,point_on_pipe).Normalize().Multiply(0.5)
point_on_pipe = projection_vector.Add(offset_vector)
ortogonal_point = point_on_pipe.Add(ortogonal_vector)
point_above_head = ortogonal_point.Add(offset_vector.Multiply(-1))

pipe_system_type_id = pipe_el.MEPSystem.GetTypeId()
pipe_type_id = pipe_el.PipeType.Id
pipe_level = pipe_el.ReferenceLevel.Id

trans.Start("Create pipe")
pipe_1 = Pipe.Create(doc,pipe_system_type_id,pipe_type_id,pipe_level, point_on_pipe, ortogonal_point)
pipe_2 = Pipe.Create(doc,pipe_system_type_id,pipe_type_id,pipe_level, ortogonal_point, point_above_head)
trans.Commit()