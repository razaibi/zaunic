import os
import jinja2
from jinja2 import Template
import yaml
import errno
from template_logic import common
from zcore.logic_mapper import logic_map
from progress.bar import ChargingBar
import CONFIGS


def read_template(template_type, template_name, params):
    _search_path = os.path.join(
        CONFIGS.TEMPLATES_FOLDER,
        '{}'.format(template_type)
    )
    template_loader = jinja2.FileSystemLoader(searchpath=_search_path)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "{}.j2".format(template_name)
    template = template_env.get_template(TEMPLATE_FILE)
    outputText = template.render(params)
    return outputText

def read_short_template(template_type, nested_file_name, template_name, params):
    """
    Construct path template path.
    """
    template_path = os.path.join(
        CONFIGS.TEMPLATES_FOLDER,
        template_type,
        ".".join([
            nested_file_name,
            CONFIGS.SHORT_TEMPLATE_FORMAT
        ])        
    )

    """
    Extract specific template.
    """
    template_collection = read_yaml(template_path)
    template_raw = Template(template_collection[template_name])
    """
    Render template.
    """
    outputText = template_raw.render(params)
    return outputText


def read_yaml(file_path):
    documents=None
    with open(file_path) as file:
        documents = yaml.load(file, Loader=yaml.FullLoader)
    return documents

def write_to_file(filename, content):
    file_path = filename
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
        with open(file_path, "w+") as f:
            f.write(content)
    else:
        with open(file_path, "a") as f:
            f.write(content)
        


def process_template(
        **task
    ):
    #Get raw data from "source_data" folder to inject in the template.
    data_injector = read_yaml(
        os.path.join(
            CONFIGS.SOURCE_DATA_FOLDER,
            "{}.yml".format( task['source_data'])
        )
    )

    #Invoke common logic applicable to all templates.
    data_injector['data'] = common.process_common_logic(
        task['category'],
        data_injector['data']
    )

    #Apply logic specified in the source data file.
    #data_injector['data'] = process_custom_logic(data_injector['data'])

    #Render template by injecting data.
    ## Check if Template is individual or nested.
    if CONFIGS.NESTED_TEMPLATE_SEPARATOR in task['template']:
        _template_file_parts = task["template"].split(
            CONFIGS.NESTED_TEMPLATE_SEPARATOR
        )
        _nested_file = _template_file_parts[0]
        _jinja_template_name = _template_file_parts[1]
        _rendered_template = read_short_template(
            task['category'],
            _nested_file,
            _jinja_template_name,
            data_injector['data']
        )
    else:
        _rendered_template = read_template(
                task['category'],
                 task['template'],
                data_injector['data']
        )

    #Prepare output
    output_file = os.path.join(
        CONFIGS.OUTPUT_FOLDER,
        '{}'.format(task['output'].replace(
            CONFIGS.OUTPUT_FOLDER_SEPARATOR,
            os.sep
            )
        )
    )

    write_to_file(
        output_file,
        _rendered_template
    )

#def process_custom_logic(data):
#    #Loop through solutions (databases)
#    for solution in data[CONFIGS.SOLUTIONS_TERM]:
#        if 'logic' in solution:
#            for logic_item in solution['logic']:
#                data = logic_map[logic_item](data)
#    return data

def process_playbook(playbook_name):
    playbook_data = read_yaml(
        os.path.join(
            CONFIGS.PLAYBOOKS_FOLDER,
            '{}.yml'.format(playbook_name)
        )
    )
    bar = ChargingBar(
        'Processing {}'.format(playbook_name), 
        max=len(playbook_data)
    )
    for task in playbook_data['tasks']:
        process_template(
            **task
        )
        bar.next()
    bar.finish()

def autocode():
    playbook_list = read_yaml(
        os.path.join(
            CONFIGS.RUNNER_FOLDER,
            '{}.yml'.format('running_list')
        )
    )
    for playbook in playbook_list['playbooks']:
        process_playbook(playbook)


