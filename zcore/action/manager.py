from zcore.action.executor_service import ExecutorActionService
from zcore.action.file_service import FileActionService
from zcore.action.generator_service import GeneratorActionService


def Factory(service_name):
    action_services = {
        "generator" : GeneratorActionService,
        "executor" : ExecutorActionService,
        "file" : FileActionService
    }

    return action_services[service_name]()