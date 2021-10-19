import os
from zcore.processor.manager import Factory as ProcessorFactory

def run():
    taskflow_processor_service = ProcessorFactory("taskflow")
    taskflow_list = taskflow_processor_service.read_list()

    for taskflow in taskflow_list['taskflows']:
        taskflow_processor_service.process_taskflow(taskflow)
