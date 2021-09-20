from abc import ABC, abstractmethod

class TemplateService(ABC):
    @abstractmethod
    def render_template(task: dict, data_injector: dict): pass


class TemplateServiceBuilder:
    def __init__(self, template_service: TemplateService) -> None:
        self.template_service = template_service

    def render_template(self, task: dict, data_injector: dict):
        return self.template_service.render_template(
            task,
            data_injector
        )

