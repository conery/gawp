# Define a Workflow with Plugins

At the beginning of each session, either in one of the first few code cells in a notebook or when initializing a command line script, GAWP will read a **configuration** that specifies which plugins to use.

## Configuring Plugins

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
It tells GAWP to use the Geometry plugin, which does the calculations that linearize a germline.
The spec tells GAWP which sheet has position data and which columns on that sheet have the coordinates of foci and other objects.

```
[geometry]
sheet_name = 'Position'
category_column = 'Category'
x_coord = 'Position X'
y_coord = 'Position Y'
```
## Configuration Cells in Jupyter Notebooks

Notebooks:  include TOML in code cells; example

## Configuration Files for the Command Line Script

Scripts:  load complete workflow description from a file; examples

!!! summary

    all plugins must be included, even it they want default settings.
