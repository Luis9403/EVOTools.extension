import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *


class ElementParameters():
    def __init__(self, element):
        self.element = element

    def GetParameterByName(self, parameter_name):
        for parameter in self.element.Parameters:
            if parameter.Definition.Name == parameter_name:
                return parameter

    def GetParameterValue(self, parameter):
        if parameter.StorageType == None:
            pass
        elif parameter.StorageType == StorageType.Integer:
            return parameter.AsInteger()
        elif parameter.StorageType == StorageType.Double:
            return parameter.AsDouble()
        elif parameter.StorageType == StorageType.String:
            return parameter.AsString()
        elif parameter.StorageType == StorageType.ElementId:
            return parameter.AsElementId()

    def TransferParameterValue(self, element2, parameter_name):
        element1_parameter = self.GetParameterByName(parameter_name)

        for parameter in element2.Parameters:
            if parameter.Definition.Name == parameter_name:
                element2_parameter = parameter
                
        return element2_parameter.Set(self.GetParameterValue(element1_parameter))