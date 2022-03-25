import ast
import sys
import logging
import re
import random
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("magicgenerator.log")
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
    
def is_list(object):
    try:
        return isinstance(ast.literal_eval(object), list)
    except:
        return False

def check_rand_from_to(type_value):
    if type_value == "str" or type_value == "timestamp":
        logger.error("rand(from, to) possible to use only with 'int' type.")
        sys.exit(1)

def check_list(type_value, values_list):
    for value in ast.literal_eval(values_list):
        if type(value).__name__ != type_value:
            logger.error(f"{value} is not {type_value} type.")
            sys.exit(1)

def check_stand_alone_value(type_value, value):
    if not re.fullmatch(r'\d+', value) and type_value == "int":
        logger.error(f"{value} does not have an int type.")
        sys.exit(1)

def generate_data_for_rand(type_value):
    if type_value == "int":
        return random.randint(0, 10000)
    elif type_value == "str":
        return str(uuid.uuid4())

def generate_data_for_empty(type_value):
    if type_value == "int":
        return None
    elif type_value == "str":
        return ""

def generate_data_for_standalone(type_value, what_to_generate):
    if type_value == "int":
        return int(what_to_generate)
    elif type_value == "str":
        return what_to_generate