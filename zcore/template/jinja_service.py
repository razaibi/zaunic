from zcore.template.service import TemplateService
import os
import jinja2
from zcore.common import FileManager
from jinja2 import Template
import CONFIGS

class JinjaTemplateService(TemplateService):

    def __init__(self) -> None:
        pass

    def read_template(
            self,
            template_type: str, 
            template_name: str, 
            params: dict
        ):
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

    def read_short_template(
            self,
            template_type: str, 
            nested_file_name: str, 
            template_name: str, 
            params: dict
        ):
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
        fm = FileManager()
        template_collection = fm.read_yaml(template_path)
        template_raw = Template(template_collection[template_name])
        """
        Render template.
        """
        outputText = template_raw.render(params)
        return outputText


    def render_template(
        self,
        task, 
        data_injector
        ):
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

        if 'secrets' in task:
            template_data['secrets'] = task['secrets']

        """
        Check if Template is individual or nested.
        """
        if CONFIGS.NESTED_TEMPLATE_SEPARATOR in task['template']:
            _rendered_template = self.render_short_template(
                task,
                template_data
            )
        else:
            _rendered_template = self.read_template(
                    task[
                        CONFIGS.CATEGORY_KEY
                    ],
                    task[
                        CONFIGS.TEMPLATE_KEY
                    ],
                    template_data
            )
        return _rendered_template

    def render_short_template(
        self,
        task: dict,
        template_data: dict
    ):
        _template_file_parts = task["template"].split(
            CONFIGS.NESTED_TEMPLATE_SEPARATOR
        )
        _nested_file = _template_file_parts[0]
        _jinja_template_name = _template_file_parts[1]
        _rendered_template = self.read_short_template(
            task[
                CONFIGS.CATEGORY_KEY
            ],
            _nested_file,
            _jinja_template_name,
            template_data
        )
        return _rendered_template
