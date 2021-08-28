import os
from posixpath import expanduser
import jinja2
from jinja2 import Template
import yaml
import errno
from template_logic import common
from zcore.common import FileManager
from zcore.logic_mapper import logic_map
from zcore.node import Manager as NodeManager
from progress.bar import ChargingBar
from pathlib import Path
import paramiko
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

def write_to_file(file_path, content):
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(os.path.expanduser(folder_path)):
        try:
            os.makedirs(os.path.expanduser(folder_path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    expanded_path=None
    if folder_path.startswith("~"):
        expanded_path = os.path.expanduser(file_path)
    else:
        expanded_path = os.path.join(
            os.getcwd(),
            file_path
        )
    with open(expanded_path, "w+") as f:
        f.write(content)

def write_to_remote_file(
        node_client,
        ftp_client,
        file_path, 
        content
    ):
    folder_path = os.path.dirname(file_path)        
    # Create temp folder.
    temp_folder = str(os.path.join(os.sep, "tmp","zaunic"))
    node_client.exec_command("sudo mkdir -p {0}".format(temp_folder))
    clean_file_path = file_path.replace(folder_path,'').replace(os.sep,'')
    #Upload to tmp folder
    file = ftp_client.file(os.path.join(temp_folder,clean_file_path), "w", -1)
    file.write(content)
    file.flush()
    # Move to designated folder
    node_client.exec_command("sudo mkdir -p {0}".format(folder_path))
    node_client.exec_command(
            "sudo mv {0}{1}* {2}{3}".format(
            temp_folder, 
            os.sep,
            folder_path, 
            os.sep
        )
    )

def process_task(
        **task
    ):
    """
    Get raw data from "source_data" folder to inject in the template.
    """
    data_injector = get_data_injector(task)

    data_injector = apply_data_sub_expression(
        task, data_injector
    )

    """
    Invoke common logic applicable to all templates.
    """
    ##To be Fixed
    ##data_injector['data'] = common.process_common_logic(
    ##    task,
    ##    data_injector
    ##)

    #Apply logic specified in the source data file.
    #data_injector['data'] = process_custom_logic(data_injector['data'])

    """
    Render Template
    """
    _rendered_template = render_template(task, data_injector)

    #Prepare output
    output_path = os.path.join(
        '{}'.format(task[
            CONFIGS.OUTPUT_KEY   
        ].replace(
            CONFIGS.OUTPUT_FOLDER_SEPARATOR,
            os.sep
            )
        )
    )
    
    write_to_file(
        output_path,
        _rendered_template
    )

#def process_custom_logic(data):
#    #Loop through solutions (databases)
#    for solution in data[CONFIGS.SOLUTIONS_TERM]:
#        if 'logic' in solution:
#            for logic_item in solution['logic']:
#                data = logic_map[logic_item](data)
#    return data

def generate_task_code(
        **task
    ):
    """
    Get raw data from "source_data" folder to inject in the template.
    """
    data_injector = get_data_injector(task)

    data_injector = apply_data_sub_expression(
        task, data_injector
    )    
    _rendered_template = render_template(task, data_injector)
    return _rendered_template

def build_output_file():
    pass
    
def render_template(task, data_injector):
    """
    Render template by injecting data.
    """
    """
    Check if the template is static or has data.
    """
    if CONFIGS.DATA_KEY in task:
        template_data = data_injector[CONFIGS.DATA_KEY]
    else:
        template_data = {}

    """
    Check if Template is individual or nested.
    """
    if CONFIGS.NESTED_TEMPLATE_SEPARATOR in task['template']:
        _template_file_parts = task["template"].split(
            CONFIGS.NESTED_TEMPLATE_SEPARATOR
        )
        _nested_file = _template_file_parts[0]
        _jinja_template_name = _template_file_parts[1]
        _rendered_template = read_short_template(
            task[
                CONFIGS.CATEGORY_KEY
            ],
            _nested_file,
            _jinja_template_name,
            template_data
        )
    else:
        _rendered_template = read_template(
                task[
                    CONFIGS.CATEGORY_KEY
                ],
                 task[
                    CONFIGS.TEMPLATE_KEY
                 ],
                template_data
        )
    return _rendered_template


def apply_data_sub_expression(task, data_injector):
    """
    Extract data from data levels
    """
    if CONFIGS.DATA_LEVEL_KEY in task:
        task_data_level = task[CONFIGS.DATA_LEVEL_KEY]
        task_data_level = \
            task_data_level.replace(" ","")
        sub_expression = process_data_level(
            task_data_level
        )

        """ 
        Apply sub expression to data.
        """
        data_injector[CONFIGS.DATA_KEY] = \
            eval(
                "".join(
                    [
                        "data_injector['{}']".format(
                            CONFIGS.DATA_KEY
                        ),
                        sub_expression
                    ]
                )
            )
    return data_injector

def get_data_injector(task):
    if CONFIGS.DATA_KEY in task:
        data_injector = read_yaml(
            os.path.join(
                CONFIGS.SOURCE_DATA_FOLDER,
                "{}.yml".format(
                    task['data'].replace(
                        CONFIGS.DATA_FOLDER_SEPARATOR,
                        os.sep
                    )
                )
            )
        )
        return data_injector
    else:
        return None
    

def fix_type(item):
    """
    Assign type as int or string to item.
    Quick hack.
    TODO: Refactor
    """
    try:
        int(item)
        return "[" + str(item) + "]"
    except:
        return "['" + str(item) + "']"

def process_data_level(level_expression):
    levels = level_expression.split(
        CONFIGS.DATA_LEVEL_SEPARATOR
    )
    level_list = list(map(fix_type, levels))
    refined_expression = "".join(level_list)
    return refined_expression

def get_output_path(task):
    ##Prepare output path
    output_file_path = os.path.join(
        '{}'.format(task[
            CONFIGS.OUTPUT_KEY   
        ].replace(
            CONFIGS.OUTPUT_FOLDER_SEPARATOR,
            os.sep
            )
        )
    )
    return output_file_path

def process_playbook(playbook_name):
    playbook_data = read_yaml(
        os.path.join(
            CONFIGS.PLAYBOOKS_FOLDER,
            '{}.yml'.format(playbook_name)
        )
    )

    node_manager = NodeManager()
    node_list = node_manager.read_node_list(
        playbook_data['nodes']
    )

    for node in node_list:
        node_connection = node_manager.connect_node_with_creds(
            node['hostname'],
            node['username'],
            node['password']
        )
        if node_connection['state']=="ok":
            node_client = node_connection["client"]
            ftp_client = node_client.open_sftp()
            bar = ChargingBar(
                'Processing {} on {}'.format(playbook_name, node["name"]), 
                max=len(playbook_data['tasks'])
            )
            for task in playbook_data['tasks']:
                task_template = generate_task_code(**task)
                write_to_remote_file(
                    node_client,
                    ftp_client,
                    get_output_path(task),
                    task_template
                )
                bar.next()
            ftp_client.close()
            node_client.close()
            bar.finish()

def run():
    playbook_list = read_yaml(
        os.path.join(
            CONFIGS.RUNNER_FOLDER,
            '{}.yml'.format('running_list')
        )
    )
    for playbook in playbook_list['playbooks']:
        process_playbook(playbook)
