import argparse
import sys
import logging
import re
import time
import json
import random
import uuid
import os
import configparser
import ast
import multiprocessing
from auxiliary_functions import is_list
from auxiliary_functions import check_list, check_rand_from_to, check_stand_alone_value
from auxiliary_functions import generate_data_for_empty, generate_data_for_rand, generate_data_for_standalone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("magicgenerator.log")
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

cfg = configparser.ConfigParser()
cfg.read('default.ini') 
section = cfg.sections()[0]

def add_arguments():
    """Creating ArgumentParser and adding argument to it."""
    example = r"""{\"date\":\"timestamp:\", \"name\": \"str:rand\", 
            \"type\":\"str:['client', 'partner','government']\", 
            \"age\": \"int:rand(1, 90)\"}"""
    parser = argparse.ArgumentParser(
            description="Creating a console utility (magicgenerator) for "
            "generating test data based on provided data schema (only in JSON "
            "format). Note that the data schema as well as keys and values must "
            "be in double quotes (JSON syntax). However string in list must be "
            f"in single quotes. Example of possible data schema: \"{example}\". " 
            "All values support notation \"type:what_to_generate\". Type "
            "could be: timestamp, str, int.", 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-schema", "--data_schema", 
                        help="Pattern for data. You can write path to json "
                        "file with schema or enter schema to command line. This "
                        "argument is required.")
    parser.add_argument("-clear", "--clear_path", 
                        help="If this flag is on, before the script starts "
                        "creating new data files, all files in "
                        "path_to_save_files that match file_name will be "
                        "deleted.", 
                        action="store_true")
    parser.add_argument("-lines", "--data_lines", type=int,
                        help="Count of lines for each file.", 
                        default=cfg.get(section, 'data_lines'))
    parser.add_argument("-count", "--files_count", type=int, 
                        help="How much json files to generate. If files_count "
                        "is 0, all output will be printed to console.",
                        default=cfg.get(section, "files_count"))
    parser.add_argument("-name", "--file_name", 
                        help="Base file_name. If no prefix, final file name "
                        "will be file_name.json. With prefix full file name "
                        "will be file_name_file_prefix.json.", 
                        default=cfg.get(section, "file_name"))
    parser.add_argument("-prefix", "--file_prefix", 
                        help="What prefix for file name to use if more than "
                        "1 file needs to be generated.",
                        choices=["count", "random", "uuid"], 
                        default=cfg.get(section, 'file_prefix'))
    parser.add_argument("-path", "--path_to_save_files", 
                        help="Where all files need to save. Path can be "
                        "defined in 2 ways: relatively from current working " 
                        "directory and absolute.", 
                        default=cfg.get(section, "path_to_save_files"))
    parser.add_argument("-mpro", "--multiprocessing", 
                        help="The number of process used to create files", 
                        type=int, default=cfg.get(section, 'multiprocessing'))
    args = parser.parse_args()
    return args

def load_schema(data_schema):
    """Loading data schema (which is in JSON format) to python in 2 ways: from
    command line or from file."""
    try:
        # Loading data schema with schema entered to command line.
        data = json.loads(data_schema)
    except (json.decoder.JSONDecodeError, TypeError):
        try:
            # Loading data schema with path to json file with schema.
            with open(data_schema) as f:
                data = json.load(f)
        except (FileNotFoundError, OSError, json.decoder.JSONDecodeError): 
            logger.error(f"Invalid data schema or invalid path to json file.")
            sys.exit(1)
    return data

def check_data_schema(data_schema):
    """ Checking correctness of data schema. """
    for value in data_schema.values():
        type_value, what_to_generate = value.strip().split(":")
        type_value, what_to_generate = (type_value.strip().lower(), 
                                        what_to_generate.strip())
        # Checking if type is timestamp, str or int.
        if type_value not in ["timestamp", "str", "int"]: 
            logger.error("Type could be: timestamp, str and int, not "
                        f"{type_value}.") 
            sys.exit(1)
        # Checking value after timestamp.
        elif type_value == "timestamp" and what_to_generate != "": 
            logger.warning("Timestamp does not support any values and it "
                            "will be ignored.")
        # Checking rand and empty value.            
        elif what_to_generate.lower() in ["rand", ""]: 
            continue
        # Checking rand(from, to).    
        elif re.fullmatch(r'rand\(\s*\d+\s*,\s*\d+\s*\)$', 
                        what_to_generate.lower()):
            check_rand_from_to(type_value)
        # Checking list with values.        
        elif is_list(what_to_generate): 
            check_list(type_value, what_to_generate)
        # Checking stand alone value.
        elif what_to_generate: 
            check_stand_alone_value(type_value, what_to_generate) 
        # If what_to_generate not in possible types.
        else: 
            logger.error("Right part of values with ':' notation should be "
                        "rand, list with values, rand(from, to), stand alone "
                        f"value or empty value, not {what_to_generate}.")
            sys.exit(1)

def generate_one_line(data_schema):
    """ Generate one line of output. """
    single_output = {}
    for key, value in data_schema.items():
        type_value, what_to_generate = value.strip().split(":")
        type_value, what_to_generate = (type_value.strip().lower(), 
                                        what_to_generate.strip())
        # Generating data for timestamp.
        if type_value == "timestamp": 
            single_output[key] = time.time()
        # Generating data for rand.
        elif what_to_generate.lower() == "rand": 
            single_output[key] = generate_data_for_rand(type_value)
        # Generating data for empty value. 
        elif what_to_generate == "": 
            single_output[key] = generate_data_for_empty(type_value)
        # Generating data for rand(from, to).    
        elif re.fullmatch(r'rand\(\s*\d+\s*,\s*\d+\s*\)$', 
                            what_to_generate.lower()): 
            limits = what_to_generate.lower().strip('rand(').strip(')').strip().split(',')
            single_output[key] = random.randint(int(limits[0]), int(limits[1]))
        # Generating data for list with values.
        elif is_list(what_to_generate):
            single_output[key] = random.choice(ast.literal_eval(what_to_generate))
        # Generating data for stand alone value.
        elif what_to_generate: 
            single_output[key] = generate_data_for_standalone(type_value, 
                                                            what_to_generate)
    return single_output

def generate_data(data_schema, data_lines):
    """ Generating data. """
    output = []
    for _ in range(data_lines):
        output.append(generate_one_line(data_schema))
    # Output is a list of dictionaries.
    return output 

def clear(path_to_save_files, file_name):
    """ Removing all files in path_to_save_files that match file_name. """
    for file_in_dir in os.listdir(path_to_save_files):
        if re.fullmatch(rf"{file_name}_.+\.json", file_in_dir): 
            file_path = os.path.join(path_to_save_files, file_in_dir)
            os.remove(file_path)

def create_full_file_name(file_name, file_prefix, counter):
    if file_prefix == "count": 
        part = str(counter)
    elif file_prefix == "random":
        part = str(random.randint(1,1000))
    elif file_prefix == "uuid":
        part = str(uuid.uuid4()) 
    full_file_name = file_name + "_" + part + ".json"
    return full_file_name

def writing_generated_output(generated_data, full_file_path):
    """Writing generated data to file (full_file_path)."""
    with open(full_file_path, 'w') as f: 
        for line in generated_data:
            json.dump(line, f)
            f.write('\n')

def safe_to_one_file(args_list):
    """Saving generated data to one file (to path_to_save/full_file_name)."""
    path_to_save, generated_data, full_file_name = args_list
    if os.path.exists(path_to_save): 
        if os.path.isdir(path_to_save):
            full_file_path = os.path.join(path_to_save, full_file_name)
            writing_generated_output(generated_data, full_file_path)
        else:
            logger.error("Path exist but it is not a directory.")
            sys.exit(1)
    else:
        logger.error(f"{path_to_save} Path does not exist.")
        sys.exit(1)

def safe_data(schema, file_name, path_to_save, file_prefix, files_count, 
            clear_path, data_lines, number_of_processes):
    """Saving generated data to file or printing it to console - depending on 
    files_count value."""
    if files_count < 0:
        logger.error(f"files_count must be >= 0, not {files_count}")
        sys.exit(1)
    # Printing all output to console.
    elif files_count == 0: 
        print('')
        for line in generate_data(schema, data_lines):
            print(line, '\n')
    # Printing output to a file/files.
    else: 
        if clear_path:
            clear(path_to_save, file_name)
        if number_of_processes > os.cpu_count():
            number_of_processes = os.cpu_count()
        if files_count >= number_of_processes:
            files_per_process = files_count//number_of_processes
        else:
            files_per_process = 1
        with multiprocessing.Pool(processes=number_of_processes) as pool:
            pool.map(func = safe_to_one_file, 
                    iterable = [(path_to_save, 
                    generate_data(schema, data_lines), 
                    create_full_file_name(file_name, 
                    file_prefix, i)) for i in range(files_count)], 
                    chunksize = files_per_process)

def magic_generator(data_schema, file_name, path_to_save, data_lines, file_prefix, 
            files_count, clear_path, number_of_processes):
    """Putting console utility for generating test data parts together
       and printing informations about what is currently being done."""
    logger.info("Start loading schema.")
    schema = load_schema(data_schema)
    logger.info("Finish loading schema.")
    logger.info("Start checking schema.")
    check_data_schema(schema)
    logger.info("Finish checking schema.")
    logger.info("Start printing/saving data.")
    safe_data(schema, file_name, path_to_save, file_prefix, files_count, 
            clear_path, data_lines, number_of_processes)
    logger.info("Finish printing/saving data.")

if __name__ == "__main__":
    args = add_arguments()
    magic_generator(args.data_schema, args.file_name, args.path_to_save_files, 
            args.data_lines, args.file_prefix, args.files_count, 
            args.clear_path, args.multiprocessing)
