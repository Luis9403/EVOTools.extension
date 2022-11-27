import clr
import System

clr.AddReference("System")
from System.Collections.Generic import List

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

import Autodesk
from Autodesk.Revit.DB import Element, ElementId, FilteredElementCollector, BuiltInCategory
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.Exceptions import OperationCanceledException

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

class SelectionFilter(ISelectionFilter):
	def __init__(self):
		pass
	
	def AllowElement(self, element):
		if element.Category.Name == "Sprinklers":
			return True
		else:
			return False
			
	def AllowReference(self, reference):
		return False
			
selection_filter = SelectionFilter()
selection = uidoc.Selection
ids = []
selected_elements = selection.GetElementIds()

if selected_elements:
	sprinklers_selected = FilteredElementCollector(doc, selected_elements).OfCategory(BuiltInCategory.OST_Sprinklers).ToElementIds()
	selection.SetElementIds(sprinklers_selected)
	uidoc.RefreshActiveView()

else:
	try:
		select_sprinklers = selection.PickElementsByRectangle(selection_filter, "Pick Sprinklers")
		
		for i in select_sprinklers:
			ids.append(i.Id)

		sprinklers_collection = List[ElementId](ids)
		selection.SetElementIds(sprinklers_collection)
		uidoc.RefreshActiveView()

	except OperationCanceledException:
		pass


	