import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *

class CategorySelectionFilter(ISelectionFilter):
    def __init__(self, category_name):
        self.category_name = category_name

    def AllowElement(self, element):
        if element.Category.Name == self.category_name:
            return True
        else:
            return False

    def AllowReference(self, reference):
        return False
