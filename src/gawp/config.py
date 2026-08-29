#
# Configuration
#
# Read the configuration file, make it accessible as a global
# variable that can be imported by other modules.
#

from collections import namedtuple
from enum import Enum
import logging
import os
from pathlib import Path
from shutil import copy2
import tomllib

from .console import console

###
#
# This function is called to initialize a new project directory.  Copy
# the default config file to the directory, and if the --tutorial option
# was specified copy the tutorial data to the directory.

CONFIG_FILE_NAME = 'gawp.toml'

def setup(args):
    '''
    Initialize a new project directory.
    '''

    def copy_item(fn):
        dest = Path.cwd() / fn
        if dest.exists():
            raise FileExistsError(dest)
        src = Path(__file__).parent / fn
        copy2(src,dest)
        logging.info(f'{src} => {dest}')
        
    copy_item(CONFIG_FILE_NAME)
    # TBD -- copy additional items


###
# 
# The configuration is saved in a class named Config
#

class Config:

    class Position:
        sheet = 'Position'

        class Cell:
            id_col_1 = 'Surpass Object'
            id_col_2 = 'ID'                     
            category = 'Category'         
            x_coord = 'Position X'        
            y_coord = 'Position Y'       

        class Measurement:
            name = 'Name'           
            category = 'Category' 
            x_coord = 'Position X'
            y_coord = 'Position Y'
 

def initialize_config(fn = None):
    '''
    Initialize configuration settings.  Looks for a TOML file in
    the following places, in order:
    * the file specified with the --config command line option
    * an environment variable named GAWP_CONFIG
    * a file named gawp.toml in the current directory
    * a default file in the module's src folder

    After decoding the file save the settings in class variables.

    Arguments:
        fn:  config file name specified on the command line
    '''
    cpath = find_toml_file(fn)
    config = load_toml_file(cpath)

    if dct := config.get('position'):
        if sname := dct.get('sheet'):
            setattr(Config.Position, 'sheet', sname)
        if subd := dct.get('cell'):
            add_attributes(Config.Position.Cell, subd)
        if subd := dct.get('measurement'):
            add_attributes(Config.Position.Measurement, subd)  

###
#
# Helper functions for initialize_config
#

def find_toml_file(fn):
    '''
    Helper function for initialize_config.  Looks for the config file
    in known locations, raises an exception if no config file found.
    '''
    p = fn or os.getenv('GAWP_CONFIG')
    if p is not None:
        config_path = Path(p)
        if not config_path.is_file():
            raise FileNotFoundError(f'init_config: no such file: {config_path}')
        return config_path
    
    config_path = Path.cwd() / 'gawp.toml'
    if config_path.is_file():
        return config_path
    
    project_dir = Path(__file__).parent
    config_path = project_dir / 'gawp.toml'
    if not config_path.is_file():
        raise ModuleNotFoundError(f'no config file in distribution?')
    return config_path

def load_toml_file(fn):
    '''
    Helper function for initialize_config.  Reads the contents of the config
    file, returns a dict with config settings.
    '''
    logging.debug(f'config: reading configuration from {fn}')
    with open(fn, 'rb') as f:
        res = tomllib.load(f)
    return res

def add_attributes(cls, specs):
    '''
    Helper method for initialize_config.  Iterate over a section of the
    config file, save the settings in the Config subclass for that section.
    '''
    for name, val in specs.items():
        setattr(cls, name, val)    
        logging.debug(f'{cls.__name__}: {name} = {val} ({type(val).__name__})')

def print_config():
    '''
    Print the configuration settings on the console
    '''
    console.print('[blue]Configuration')
    console.print('Position.sheet', Config.Position.sheet)
    for attr in [v for v in vars(Config.Position.Cell) if not v.startswith('_')]:
        console.print(attr, getattr(Config.Position.Cell, attr))
    for attr in [v for v in vars(Config.Position.Measurement) if not v.startswith('_')]:
        console.print(attr, getattr(Config.Position.Measurement, attr))

# TODO: use table of subclass names
# TODO: print rich table
