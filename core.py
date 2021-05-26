import os
import jinja2
import yaml


def read_template(template_type, template_name, params):
    _search_path = os.path.join('templates','{}'.format(template_type))
    template_loader = jinja2.FileSystemLoader(searchpath=_search_path)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "{}.j2".format(template_name)
    template = template_env.get_template(TEMPLATE_FILE)
    outputText = template.render(params)
    return outputText

def read_yaml(file_path):
    documents=None
    with open(file_path) as file:
        documents = yaml.full_load(file)
    return documents


def process_template(category, template_name, source_data):
    _injector = read_yaml(
        os.path.join(["artifacts",source_data])
    )
    _rendered_template = read_template(
            category,
            template_name,
            _injector['data']
    )
    return _rendered_template
