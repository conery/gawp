## The Configuration File

GAWP configurations use a file format named TOML.
TOML files are plain text and can be opened with any text editor.
Go ahead and open `gawp.toml` now.

Our intial configuration file has just one line:

```
[geometry.foci]
```

That line is a **section header**.
It has the name of a plugin enclosed in square brackets.

The fact that there is only one plugin name in this configuration file means `gawp` will execute only this one step when we run it.
This plugin fetches the locations of foci from a Position sheet; a workflow that consists of just this step will simply read the positions and write them to the output file.

!!! info "Section Names Define Plugins"
    The important message to take away from this part of the tutorial is that `gawp` will run only the plugins that appear as section headers in the configuration file.

Let's add another step to the workflow.
Add the following lines:

```
[geometry.measurements]
sheet_name = 'Position'
category_column = 'Category'
category = 'MeasurementPoint'
```

The lines below the section heading specify options for the plugin.
Options are lines that look like Python assignment statements: they have a setting name, an equal sign, and a value.
In this example we're telling the Measurements plugin that measurements are found on a sheet named Position, and to look in the Category column for rows that have "MeasurementPoint" in that column.

The upated workflow has two steps:  read the foci and read the measurement points.
When measurement points are included `gawp` will make line segments from the points and run the linearization algorithm to map foci to line segments.

Save the modified configuration and run the script again:

```
$ gawp --log quiet run --preview --file data/herm_5.xlsx

Preview for herm_5:
        seg_name                   point                    head                   tail   distance ...
uid
pdk.123       AB  POINT (19.469 128.836)  POINT (38.501 141.542)  POINT (39.457 120.56)  19.590598 ...
pdk.174       AB   POINT (1.258 138.006)  POINT (38.501 141.542)  POINT (39.457 120.56)  37.365346 ...
...
```

The column named `point` was there in the previous output.
In the new output the Measurement plugin added `seg_name` and all the other columns that are the result of mapping the points to line segments.

### Default Settings

You probably noticed the original configuration file did not include options for the `[geometry.foci]` section.
That plugin also has several options, but since the configuration file did not include them the plugin used the default values.

All of the available plugins are shown in the Plugins section in the sidebar, and a complete list of options and their default values are included in the descriptions of the plugins.

