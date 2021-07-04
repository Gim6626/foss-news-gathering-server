import os
import yaml


SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

keywords = ''
with open(os.path.join(SCRIPT_DIRECTORY, 'keywords.yaml'), 'r') as fin:
    keywords = yaml.safe_load(fin)
