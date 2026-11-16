# Configuring Plugins

At the beginning of each session, either in one of the first few code cells in a notebook or when initializing a command line script, GAWP will read a **configuration** that specifies which plugins to use.

## TOML

Configurations are written in a simple language named [TOML](https://toml.io).
A configuration is divided into **sections**.
A section begins with a header that has the section name enclosed in brackets.
Below that are the specifications, which look like Python assignment statements: an option name, an equal sign, and the value for that option.
Values can be integers, strings, or lists.

In a GAWP configuration **section headers are plugin names**.

- to include a plugin in your workflow, add a section with that name to your configuration

- some plugins have required settings, and these need to be included in that section

- other settings are optional; if you leave them out GAWP will use the default value for that setting.

An important point to remember:  **if you want to use a plugin it must appear in the configuration**.
You might be happy to use the default value for all the options, in which case there will be no settings in that section, but you still need to include the section header.

Here is a simple example of a GAWP configuration written in TOML.
This workflow will use Geometry and both of its submodules, Foci and Measurements, to linearize a germline.

```
[geometry]
sheet_name = 'Position'
category_column = 'Category'
x_coord = 'Position X'
y_coord = 'Position Y'

[geometry.foci]
index = ['Surpass Object','ID']

[geometry.measurements]
```

The `geometry` section tells GAWP which sheet has position data and which columns on that sheet have the coordinates of foci and other objects.
The `geometry.foci` and `geometry.measurements` sections tell GAWP to install these plugins and use the default settings for Measurements.

### Configuring Join and Group Plugins

Because a project might want to copy or group data from several different sheets the syntax for the section header is slightly different and there can be multiple sections in the configuration.

To add a Join or Group plugin to a project, write the word `join` or `group`, a period, and then a name.
The name of the sheet and the name of the column on that sheet must be specified.
By default the Join and Group plugins expect to see the same ID columns that were used for Geometry, but it they are different the names to use instead can be specified as well.

In this example a project wants to copy volume and sphericity data to the output.

```
[join.volume]
sheet = 'Volume'
column = 'Volume'

[join.sphericity]
sheet = 'Sphericity'
column = 'Sphericity'
```

## Configuration Cells in Jupyter Notebooks

To run GAWP from a Jupyter notebook:

- import the GAWP modules that implement the plugins
- create a piece of text that has the TOML specification
- pass that specification to the GAWP function that installs the plugins

Here are some examples from a workflow that will use the Geometry plugin.

##### Imports

The first statement imports the GAWP function that installs plugins.
Below that are statements that import the plugins themselves.

```
from gawp.config import initialize_config
from gawp.geometry import Geometry
from gawp.foci import Foci
...
```

##### TOML String

This statement defines a string named `GAWP_CONFIG` using Python's "triple-quoted string" syntax, which lets us create strings that span multiple lines:

```
GAWP_CONFIG = '''
[geometry]
sheet_name = 'Position'
category_column = 'Category'
x_coord = 'Position X'
y_coord = 'Position Y'

[geometry.foci]
category = 'Surface'
index = ['Surpass Object','ID']
'''
```

##### Install the Plugins

Finally we pass `GAWP_CONFIG` to `initialize_config` to install the plugins:

```
initialize_config(text=GAWP_CONFIG)
```

## Configuration Files for the Command Line Script

Python scripts read configurations from files.
TOML files are plain text files that can be created with any text editor.
The filename extension is usually `.toml`.

`gawp`, the command line application installed by pip, looks for a file named `gawp.toml` in the directory where the script is started.
To tell it to read a different file, include the `--config` option on the command line, for example:

```
 $ gawp --config rad51.toml run
```

!!! summary "Summary: Define Plugins Using TOML"

    Call `initialize_config` at the beginning of a notebook or script.  Pass it a piece of text or the name of a file.
    The spec should have a section for each plugin to use in the workflow.

