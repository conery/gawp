#
# Plugins
#
# A plugin object encapsulates all the information needs to run a step
# in the workflow.  This module defines a base class named Plugin, the
# actual plugins are defined in their own modules (e.g. the Geometry class
# is defined in geometry.py).
#
# The PluginManager class defines a global object that is accessible
# in all modules.  It provides information about the plugins installed for
# an application and controls the order in which plugins are called during
# the workflow.
#

import io

class Plugin:
    '''
    Base class for all Plugin modules.  The constructor initializes the
    configuration settings of the plugin using a dictionary of attribute
    names and default values and another dictionary of settings requested
    by the user.
    '''

    def __init__(self, slots: dict, args: dict):
        '''
        Save configuration settings for this object.

        Arguments:
            slots: names and default values of all settings for this class
            args: names and values of settings requested by the user
        '''
        for key, val in slots.items():
            x = args[key] if key in args else val
            setattr(self, key, x)

    @staticmethod
    def defaults(name, slots):
        '''
        Return a string containing the default settings for a class in TOML format.

        Arguments:
            name: the name of the class
            slots: a dictionary with names and values of default settings
        '''
        with io.StringIO() as f:
            print(f'[{name}]', file=f)
            for key, val in slots.items():
                print(f'{key} = "{val}"', file=f)
            res = f.getvalue()

        return res


class PluginManager:
    '''
    The Plugin Manager is a singleton object that keeps track of which plugins
    are used by a notebook or script.  When plugins are installed they are recorded
    here.  The manager constructs the list of plugins to call to carry out the
    workflow.
    '''

    def __init__(self):
        self.plugins = {}
        self.io = None
        self.stages = None
        self.geometry = None
        self.join = None
        self.group = None

    # def __getitem__(self, key):
    #     return self.plugins.get(key)

    def add_plugin(self, name, obj):
        self.plugins[name] = obj
        setattr(self, name, obj)

plugins = PluginManager()
