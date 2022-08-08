import openpyxl
from pathlib import Path

#Constant declarations
list_of_params = []
list_of_resources = []
list_of_connections = []

#Class declarations
class Connection:
    def __init__(self, alias, rrid):
        self.alias = alias
        self.rrid = rrid

class Resource:
    def __init__(self, RRID, vendor, version, parameter):
        self.RRID = RRID
        self.vendor = vendor
        self.version = version
        self.parameter = parameter

class Parameter:
    def __init__(self, alias):
        self.alias = alias

if __name__ == "__main__":
    resource_file = Path('SDS2.0Metadata','resources.xlsx')
    resource_obj = openpyxl.load_workbook(resource_file)

    param_file = Path('SDS2.0Metadata', 'code_parameters.xlsx' )
    param_obj = openpyxl.load_workbook(param_file)

    param_sheet = param_obj.active
    resource_sheet = resource_obj.active

    for i in range(resource_sheet.max_row):
        id = "A" + str(i+1)
        vendor = "C" + str(i+1)
        version = "D" + str(i+1)
        index = "F" + str(i+1)
        list_of_resources.append(Resource(resource_sheet[id].value, resource_sheet[vendor].value,
        resource_sheet[version].value,resource_sheet[index].value))

    for i in range(param_sheet.max_row):
        index = "B" + str(i+1)
        list_of_params.append(Parameter(param_sheet[index].value))

    list_of_resources.pop(0)
    list_of_params.pop(0)
    list_of_params.pop(0)

    for x in list_of_resources:
        for p in list_of_params:
            if (x.parameter == p.alias):
                list_of_connections.append(Connection(p.alias, x.RRID))
    
    for y in list_of_connections:
        print("Connection between " + str(y.alias) + " and " + str(y.rrid))

