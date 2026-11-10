#
# Configuration
#
# Read the configuration file and instantiate plugins
#

import logging
from pathlib import Path
import tomllib

from .plugin import plugins
from .io import IO
from .stages import Stages
from .geometry import Geometry
from .foci import Foci
from .measurements import Measurements
from .join import Join, Sheet

# Constants imported by other modules

DEFAULT_CONFIG_FILE_NAME = 'gawp.toml'

def initialize_config(text = None, fn = None):
    '''
    Configure the plugins usings TOML formatted specs, either from
    text (e.g. when called from a notebook) or from a file (when
    called from a command line app).)  

    Arguments:
        text: a string in TOML format
        fn:  the name of a TOML file
    '''

    def create_geometry_plugins(dct):
        '''
        Pull out the subsections for foci and measurements, instantiate those two
        subclasses, and then save them as members of a Geometry object.  The foci
        section is required, but measurements can be set to None if it's not in 
        the configuration.
        '''
        foci_opts = dct.pop('foci', None)
        meas_opts = dct.pop('measurements', None)
        if foci_opts is None:
            raise ValueError("configuration: missing [geometry.foci]")
        fp = Foci(**(dct|foci_opts))
        if meas_opts is None:
            mp = None
        else:
            mp = Measurements(**(dct|meas_opts))
        if bogus := [k for (k,v) in dct.items() if isinstance(v,dict)]:
            raise ValueError(f'unknown geometry sections: {bogus}')
        return Geometry(fp, mp)

    def create_join_plugins(dct):
        sheets = []
        for name, params in dct.items():
            sheets.append(Sheet(**params))
        return Join(sheets)

    if text is not None:
        logging.debug(f'config: initializing from text')
        dct = tomllib.loads(text)
    elif cpath := find_toml_file(fn):
        logging.debug(f'config: reading configuration from {cpath}')
        try:
            with open(cpath, 'rb') as f:
                dct = tomllib.load(f)
        except tomllib.TOMLDecodeError as err:
            logging.error(err)
            raise ValueError(f'Error while parsing {cpath}')
    else:
        raise ValueError(f'initialize_config: specify text or file name')

    err_count = 0
    for name, fields in dct.items():
        match name:
            case 'io': obj = IO(**fields)
            case 'stages': obj = Stages(**fields)
            case 'geometry': obj = create_geometry_plugins(fields)
            case 'join': obj = create_join_plugins(fields)
            case _: 
                logging.error(f'no class for {name}')
                err_count += 1
                continue
        plugins.add_plugin(name, obj)
        logging.info(f'config: added {name}')
        logging.debug(f'  {fields}')

    if err_count:
        raise ModuleNotFoundError(f'config file has {err_count} unknown plugin names')

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
    
    config_path = Path.cwd() / DEFAULT_CONFIG_FILE_NAME
    if config_path.is_file():
        return config_path
    
    return None


