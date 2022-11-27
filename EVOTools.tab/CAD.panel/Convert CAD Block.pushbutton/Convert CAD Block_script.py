import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Plumbing import *

# set active document and document UI
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

selection = uidoc.Selection
active_view = uidoc.ActiveView
active_view_id = active_view.Id
collector = FilteredElementCollector(doc, active_view_id)
trans = Transaction(doc)

def GetFamilyByName(document, built_in_category, name):
    el_type_ids = FilteredElementCollector(document).OfCategory(built_in_category).WhereElementIsElementType().ToElementIds()
    for el_id in el_type_ids:
        element = doc.GetElement(el_id)
        el_family_name = element.FamilyName
        el_type_name = Element.Name.__get__(element)
        family_type_name = el_family_name + ": " + el_type_name
        if family_type_name == name:
            return element

def GetGeometryInstances(document, active_view_id, name):
    geo_instances = []
    imp_instances = FilteredElementCollector(document, active_view_id).OfClass(ImportInstance).WhereElementIsNotElementType().ToElements()
    for imp_inst in imp_instances:
        if imp_inst.Category.Name == name:
            for geo_object in imp_inst.get_Geometry(Options()):
            	if isinstance(geo_object, GeometryInstance):
                    for ins in geo_object.SymbolGeometry:
                        if isinstance(ins, GeometryInstance):
                            geo_instances.append(ins)
    return geo_instances

def GetCADLinkNameFromReference(document, reference):
    cad_link = document.GetElement(reference.ElementId)
    cad_link_name = cad_link.Category.Name
    return cad_link_name

def GetFamilyAndTypeName(document, reference):
    element = document.GetElement(reference.ElementId)
    name = element.Symbol.FamilyName + ": " + element.Name
    return name


spk_ref = selection.PickObject(ObjectType.Element, "Pick Sprinkler Head")
ref = selection.PickObject(ObjectType.PointOnElement, "Pick reference in CAD block")
cad_link_name = GetCADLinkNameFromReference(doc, ref)
geo_instances = GetGeometryInstances(doc, active_view_id, cad_link_name)

picked_geo_inst = []
for inst in geo_instances:
	uid = Element.UniqueId.__get__(inst.Symbol)
	if uid == ref.ConvertToStableRepresentation(doc).split(":")[6]:
		picked_geo_inst.append(inst)
points_coord = []
for i in picked_geo_inst:
    points_coord.append(i.Transform.Origin)

built_in_category = BuiltInCategory.OST_Sprinklers
family_name = GetFamilyAndTypeName(doc, spk_ref)
family_symbol = GetFamilyByName(doc, built_in_category, family_name)

family_symbol.Activate()
current_level = active_view.GenLevel
trans.Start("Place Sprinkler heads")
for point in points_coord:
    new_family = doc.Create.NewFamilyInstance.Overloads[XYZ, FamilySymbol, Level, StructuralType](point, family_symbol, current_level, StructuralType.NonStructural)

trans.Commit()





