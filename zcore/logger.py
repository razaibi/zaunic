import logging
from colorama import init, Fore, Back, Style
init(autoreset=True)

logging.basicConfig(level=logging.INFO)

class LogMachine():
    def __init__(self):
        pass

    def log_info(self, message):
        logging.info(Fore.YELLOW + "\t" + message)

    def log_error(self, message):
        logging.error(Fore.BLUE + "\t" + message)

    def log_success(self, message):
        logging.info(Fore.GREEN + "\t" + message)

