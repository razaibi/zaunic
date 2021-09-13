from zcore.template.jinja_service import JinjaTemplateService

def Factory(service_name):
    template_services = {
        "jinja" : JinjaTemplateService
    }

    return template_services[service_name]()