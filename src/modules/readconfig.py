#account and api key/secret parser
#   In future, It'll be changed to read informations from database

import yaml,json

def config_read(configpath):
    with open(configpath,'r') as config_file:
        return json.dumps(yaml.load(config_file),sort_keys=True)
