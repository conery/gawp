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
        category_col = 'Category'
        cell_category = 'Surface'
        measurement_category = 'MeasurementPoint'

        class Cell:
            id_col_1 = 'Surpass Object'
            id_col_2 = 'ID'                     
            x_coord = 'Position X'        
            y_coord = 'Position Y'       

        class Measurement:
            name_col = 'Name'           
            x_coord = 'Position X'
            y_coord = 'Position Y'

    class MeioticStage:
        id_col = 'GonadID'
        stage_names = ['TZ_start','TZ_end','Pachy_end']

    class Imaris:
        data = None
        measurements = None

    class Output:
        data = None
        log = None

def settings(cls):
    '''
    Return a dictionary containg the settings for a configuration section
    '''
    return { attr: val for (attr,val) in cls.__dict__.items() if not attr.startswith('_') } 

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
        for s in ['sheet','category_col','cell_category','measurement_category']:
            if val := dct.get(s):
                add_attributes(Config.Position, {s:val})
        if subd := dct.get('cell'):
            add_attributes(Config.Position.Cell, subd)
        if subd := dct.get('measurement'):
            add_attributes(Config.Position.Measurement, subd)

    specs = [
        ('meioticstage', Config.MeioticStage),
        ('imaris', Config.Imaris),
        ('output', Config.Output),
    ]

    for name, cls in specs:
        if dct := config.get(name):
            add_attributes(cls, dct)

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

# def print_config():
#     '''
#     Print the configuration settings on the console
#     '''
#     console.print('[blue]Position')
#     console.print('  sheet', Config.Position.sheet)
#     console.print('  category col', Config.Position.category_col)
#     console.print('  cell category', Config.Position.cell_category)
#     console.print('  meas category', Config.Position.measurement_category)
#     console.print('[blue]Position.Cell')
#     for attr in [v for v in vars(Config.Position.Cell) if not v.startswith('_')]:
#         console.print(' ',attr, getattr(Config.Position.Cell, attr))
#     console.print('[blue]Position.Measurement')
#     for attr in [v for v in vars(Config.Position.Measurement) if not v.startswith('_')]:
#         console.print(' ',attr, getattr(Config.Position.Measurement, attr))
#     console.print('[blue]MeioticStage')
#     for attr in [v for v in vars(Config.MeioticStage) if not v.startswith('_')]:
#         console.print(' ',attr, getattr(Config.MeioticStage, attr))

# TODO: print rich table
