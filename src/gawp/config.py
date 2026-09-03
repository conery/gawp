#
# Configuration
#
# Read the configuration file, make it accessible as a global
# variable that can be imported by other modules.
#

from dataclasses import dataclass, asdict, field
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

    logging.warning('Deprecated -- have app create and print a default Config')
    copy_item(CONFIG_FILE_NAME)
    # TBD -- copy additional items


###
# 
# Configurations are saved in instances of a class named Config.  Each
# section of the config file is defined by its own subclass.
#

@dataclass
class Cell:
    id_col_1: str = 'Surpass Object'
    id_col_2: str = 'ID'                     
    x_coord: str = 'Position X'        
    y_coord: str = 'Position Y'       

@dataclass
class Measurement:
    name_col: str = 'Name'           
    x_coord: str = 'Position X'
    y_coord: str = 'Position Y'

@dataclass
class Position:
    sheet: str = 'Position'
    category_col: str = 'Category'
    cell_category: str = 'Surface'
    measurement_category: str = 'MeasurementPoint'
    cell: Cell = field(default_factory=Cell)
    measurement: Measurement = field(default_factory=Measurement)

@dataclass
class MeioticStage:
    id_col: str = 'GonadID'
    stage_names: list[str] = field(default_factory=lambda: ['TZ_start','TZ_end','Pachy_end'])

@dataclass
class Imaris:
    data: str = ''
    measurements: str = ''

@dataclass
class Output:
    data: str = ''
    log: str = ''

@dataclass
class Config:
    position: Position = field(default_factory=Position)
    meioticstage: MeioticStage = field(default_factory=MeioticStage)
    imaris: Imaris = field(default_factory=Imaris)
    output: Output = field(default_factory=Output)

    def update(self, dct):
        '''
        Perform a deep update, copying values from a dictionary (loaded from
        a TOML file) into this object).
        '''
        Config._dfs(self, asdict(self), dct)

    def _dfs(self, d1, d2):
        '''
        Helper function, does a depth-first traversal of the object's subclasses.
        '''
        for k1, v1 in d1.items():
            if k1 in d2.keys():
                v2 = d2[k1]
                if isinstance(v1,dict) and isinstance(v2,dict):
                    cls = getattr(self, k1)
                    Config._dfs(cls, v1, v2)
                else:
                    setattr(self, k1, v2)

def settings(cls):
    '''
    Return a dictionary containing all the settings of a configuration class
    '''
    return {k: v for k, v in asdict(cls).items() if not isinstance(v,dict)}

# Create the global configuration object:

config = Config()

# This function will look for user settings and use them to update an existing
# configuration

def initialize_config(text = None, fn = None):
    '''
    Update the global configuration object with settings from a string containing a 
    TOML format specification or from a TOML file.  If both arguments are None look 
    for a config file in the current directory.  

    Arguments:
        text: a string in TOML format
        fn:  the name of a TOML file
    '''

    # Reset the configuration to its default values (used by unit tests and notebooks)
    config.update(asdict(Config()))

    if text:
        logging.debug(f'config: initializing from text')
        dct = tomllib.loads(text)
    elif cpath := find_toml_file(fn):
        logging.debug(f'config: reading configuration from {cpath}')
        with open(cpath, 'rb') as f:
            dct = tomllib.load(f)
    else:
        dct = {}

    config.update(dct)

###
#
# Helper functions
#

def find_toml_file(fn):
    '''
    Helper function for initialize_config.  Looks for the config file
    in known locations.
    '''
    if fn:
        config_path = Path(fn).resolve()
        if not config_path.is_file():
            raise FileNotFoundError(f'init_config: no such file: {config_path}')
        return config_path
    
    config_path = Path.cwd() / CONFIG_FILE_NAME
    if config_path.is_file():
        return config_path
    
    return None


