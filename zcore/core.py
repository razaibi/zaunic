import os
from zcore.processor.manager import Factory as ProcessorFactory

#def process_custom_logic(data):
#    #Loop through solutions (databases)
#    for solution in data[CONFIGS.SOLUTIONS_TERM]:
#        if 'logic' in solution:
#            for logic_item in solution['logic']:
#                data = logic_map[logic_item](data)
#    return data

def run():
    playbook_processor_service = ProcessorFactory("playbook")
    playbook_list = playbook_processor_service.read_list()

    for playbook in playbook_list['playbooks']:
        playbook_processor_service.process_playbook(playbook)
