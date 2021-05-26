from autocore import data_mapper

def process_common_logic(category, data):
    data = process_datatype_logic(category, data)


    return data


def process_datatype_logic(category, data):
    type_based_solutions = [
        'postgresql',
        'sqlserver',
        'dotnet-webapi',
        'fastapi'
    ]

    if category in type_based_solutions:
        for db in data['databases']:
            for table in db['tables']:
                for column in table['columns']:
                    column['type'] = map_data_type(
                        column['type'],
                        category
                    )
    return data


def map_data_type(generic_type, target_category):
    datatypes = data_mapper.datatypes
    revised_data_type = datatypes[generic_type][target_category]
    return revised_data_type


    

