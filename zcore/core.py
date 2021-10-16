import os
from zcore.processor.manager import Factory as ProcessorFactory

def run():
    playbook_processor_service = ProcessorFactory("playbook")
    playbook_list = playbook_processor_service.read_list()

    for playbook in playbook_list['playbooks']:
        playbook_processor_service.process_playbook(playbook)
