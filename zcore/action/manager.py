from zcore.action.generator_service import GeneratorActionService


def Factory(service_name):
    action_services = {
        "generator" : GeneratorActionService
    }

    return action_services[service_name]()