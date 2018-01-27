import logging
import logging.config
import json


# If applicable, delete the existing log file to generate a fresh log file during each execution
def config_logs():
    with open("log_config.json", 'r') as logging_configuration_file:
        config_dict = json.load(logging_configuration_file)
        logging.config.dictConfig(config_dict)
