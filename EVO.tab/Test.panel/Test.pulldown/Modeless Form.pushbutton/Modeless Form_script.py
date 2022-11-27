import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.Exceptions import *
from pyrevit import script

import wpf
from System import Windows

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
uiapp = __revit__.Application
xamlfile = script.get_bundle_file('ui.xaml')

def GetElementIdFromPick(uidocument):
    selection = uidocument.Selection
    pick_el = selection.PickObject(ObjectType.Element, "Pick some Element")
    el_id = pick_el.ElementId
    TaskDialog.Show("Element Id", el_id.ToString())


class PickEventHandler(IExternalEventHandler):
    def __init__(self, get_el_id):
        self.get_el_id = get_el_id

    def Execute(self, uiapp):
        try:
            self.get_el_id()
        except InvalidOperationException:
            TaskDialog.Show("Error dialog", "Exception Taken")

    def GetName(self):
        return "Get Object Id from pick operation"


pick_event_handler = PickEventHandler(GetElementIdFromPick(uidoc))
external_event = ExternalEvent.Create(pick_event_handler)

class MyWindows(Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self, xamlfile)

    def pick_object(self, sender, args):
        external_event.Raise()


MyWindows().Show()




