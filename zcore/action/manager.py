from zcore.action.executor_service import ExecutorActionService
from zcore.action.file_service import FileActionService
from zcore.action.generator_service import GeneratorActionService
from zcore.action.rest_api_service import RestApiActionService


def Factory(service_name):
    action_services = {
        "generator" : GeneratorActionService,
        "executor" : ExecutorActionService,
        "file" : FileActionService,
        "rest_api_caller": RestApiActionService
    }

    return action_services[service_name]()