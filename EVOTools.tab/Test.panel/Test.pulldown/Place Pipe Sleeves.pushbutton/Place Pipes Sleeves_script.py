import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Structure import *
from Autodesk.Revit.Exceptions import *

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

selection = uidoc.Selection
trans = Transaction(doc)
active_view = uidoc.ActiveView

def GetElementFromReference(document, reference):
	element = document.GetElement(reference.ElementId)
	return element

def GetFamilyByName(document, built_in_category, name):
    el_type_ids = FilteredElementCollector(document).OfCategory(built_in_category).WhereElementIsElementType().ToElementIds()
    for el_id in el_type_ids:
        element = doc.GetElement(el_id)
        el_family_name = element.FamilyName
        el_type_name = Element.Name.__get__(element)
        family_type_name = el_family_name + ": " + el_type_name
        if family_type_name == name:
            return element

def SetParameterValueByName(family_instance, name, value):
    parameters = family_instance.GetParameters(name)
    if len(parameters) > 1:
        return TaskDialog.Show("Warning","The element contains more that one parameter with same name")
    else:
        set_value = parameters[0].Set(value)
        return set_value

def ProjectPickedReferenceOnPipeCenter(pipe, point):
    pipe_line = pipe.Location.Curve
    intersection_point = pipe_line.Project(point).XYZPoint
    return intersection_point
    
def AlignSleeveWithPipe(document, pipe, sleeve):
    direction = pipe.Location.Curve.Direction
    norm_direction = direction.Normalize()

    orientation = sleeve.HandOrientation
    norm_orientation = orientation.Normalize()
    origin = sleeve.Location.Point
    
    rotation_angle = norm_direction.AngleTo(norm_orientation)
    rotation_vector = norm_direction.CrossProduct(norm_orientation)
    try:
        rotation_axis = Line.CreateBound(origin, origin.Add(rotation_vector*10))
        ElementTransformUtils.RotateElement(document, sleeve.Id, rotation_axis, -rotation_angle)
        return rotation_axis
    except ArgumentsInconsistentException:
        pass

def GetPipeCenterLineReference(view, pipe):
    options = Options()
    options.ComputeReferences = True
    options.View = view
    options.IncludeNonVisibleObjects = True

    pipe_geo_elements = pipe.get_Geometry(options)
    for geo_element in pipe_geo_elements:
        if isinstance(geo_element, Line):
            line_ref = geo_element.Reference
            return line_ref

def GetViewsByViewType(document, view_type):
    filtered_views = []
    views = FilteredElementCollector(document).OfClass(View).WhereElementIsNotElementType().ToElements()
    for view in views:
        if view.ViewType == view_type:
            filtered_views.append(view)
    return filtered_views
# select pipe
ref = selection.PickObject(ObjectType.Edge,"Pick Pipe")

# get insertion point
picked_point = ref.GlobalPoint

# get pipe element
pipe_el = GetElementFromReference(doc, ref)
ins_point = ProjectPickedReferenceOnPipeCenter(pipe_el, picked_point)

nominal_diameter = pipe_el.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
outside_diameter = pipe_el.get_Parameter(BuiltInParameter.RBS_PIPE_OUTER_DIAMETER)
system_type = pipe_el.get_Parameter(BuiltInParameter.RBS_PIPING_SYSTEM_TYPE_PARAM)
pipe_ref_level = pipe_el.ReferenceLevel


mech_equip_category = BuiltInCategory.OST_MechanicalEquipment
family_name = "EVO_Pipe_Sleeve: Pipe_Sleeve"
sleeve_family = GetFamilyByName(doc, mech_equip_category, family_name)
sleeve_family.Activate()

trans.Start("Create pipe sleeve")
sleeve_inst = doc.Create.NewFamilyInstance.Overloads[XYZ, FamilySymbol, Level, StructuralType](ins_point, sleeve_family, pipe_ref_level, StructuralType.NonStructural)
doc.Regenerate()
AlignSleeveWithPipe(doc, pipe_el, sleeve_inst)

sleeve_centerfrontback_ref = sleeve_inst.GetReferences(FamilyInstanceReferenceType.CenterFrontBack)
sleeve_centerelevation_ref = sleeve_inst.GetReferences(FamilyInstanceReferenceType.CenterElevation)

pipe_ref = GetPipeCenterLineReference(active_view, pipe_el)

plan_view_type = ViewType.FloorPlan
plan_view = GetViewsByViewType(doc, plan_view_type)
plan_alignment = doc.Create.NewAlignment(plan_view[0], pipe_ref, sleeve_centerfrontback_ref[0])

elevation_view_type = ViewType.Elevation
elevation_view = GetViewsByViewType(doc, elevation_view_type)
elevation_alignment = doc.Create.NewAlignment(elevation_view[1], pipe_ref, sleeve_centerelevation_ref[0])

sleeve_inside_diameter = SetParameterValueByName(sleeve_inst, "Pipe_Sleeve_InsideDiameter", 0.8)
pipe_sleeve_nd = SetParameterValueByName(sleeve_inst, "Pipe_NominalDiameter", nominal_diameter.AsDouble())
pipe_sleeve_od = SetParameterValueByName(sleeve_inst, "Pipe_OutsideDiameter", outside_diameter.AsDouble())
trans.Commit()

