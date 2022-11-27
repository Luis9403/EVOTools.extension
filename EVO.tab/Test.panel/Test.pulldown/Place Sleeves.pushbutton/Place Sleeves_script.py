import clr
import math

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.Exceptions import OperationCanceledException
from Autodesk.Revit.Creation import Document

# set active document and document UI
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

selection = uidoc.Selection

# create a pipe_accesories collector
collector = FilteredElementCollector(doc)
pipe_accessories = collector.OfCategory(BuiltInCategory.OST_PipeAccessory).WhereElementIsElementType().ToElements()

pipe_sleeve_el = 0

# filter for pipe_sleeves familysymbol
for pipe_accessory in pipe_accessories:
	if pipe_accessory.FamilyName == "Pipe_Sleeve":
		pipe_sleeve_el = pipe_accessory
		break
	else:
		continue
		
selection = uidoc.Selection

# select pipe element by face
select_pipe = selection.PickObject(ObjectType.Face,"Select a Pipe")

# get point selected on pipe face and element pipe
selected_point = select_pipe.GlobalPoint
pipe = doc.GetElement(select_pipe)

# get pipe parameters
pipe_ND = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM).AsDouble()
pipe_OD = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_OUTER_DIAMETER).AsDouble()
pipe_reference_level = pipe.get_Parameter(BuiltInParameter.RBS_START_LEVEL_PARAM).AsElementId()

# get pipe direction vector and face reference object
direction_vector = pipe.Location.Curve.Direction
el_face = pipe.GetGeometryObjectFromReference(select_pipe).Reference

# create a transaction object
trans = Transaction(doc)

# start transaction
trans.Start("Place sleeve")

pipe_sleeve_el.Activate()
# create new family instance with sleeve family symbol on selected pipe
sleeve_instance = doc.Create.NewFamilyInstance.Overloads[Reference, XYZ, XYZ, FamilySymbol](select_pipe, selected_point, direction_vector, pipe_sleeve_el)
doc.Regenerate()

slv_pipe_od_param = sleeve_instance.GetParameters("Pipe_OD")
slv_pipe_level_param = sleeve_instance.GetParameters("Schedule Level")
slv_pipe_level_param[0].Set(pipe_reference_level)
slv_pipe_od_param[0].Set(pipe_OD)

slv_location = sleeve_instance.Location.Point
slv_orientation = sleeve_instance.FacingOrientation

axis_vector = direction_vector.CrossProduct(slv_orientation)
rotation_axis = Line.CreateBound(slv_location, axis_vector)
ang_bt_vectors = direction_vector.AngleTo(slv_orientation)

ElementTransformUtils.RotateElement(doc, sleeve_instance.Id, rotation_axis, ang_bt_vectors)


trans.Commit()

#TaskDialog.Show("R", transform.BasisX.ToString())