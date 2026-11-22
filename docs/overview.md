# Define a Workflow with Plugins

GAWP is organized as a set of **plugin modules** that carry out individual steps of the full linearization workflow.

| Plugin Name | Module Name | Resonsibilities |
| -- | -- | -- |
| IO | `gawp.io` | Opens spreadsheets, extracts data from sheets |
| Geometry | `gawp.geometry` | Computes distances between points and line segments |
| Foci | `gawp.geometry.foci` | Reads positions of foci |
| Measurements | `gawp.geometry.measurements` | Reads measurement points, uses them to create line segments |
| Join | `gawp.join` | Copies data from Volume, Sphericity, and other sheets |
| Group | `gawp.group` | Summarizes Intensity data to create counts |
| Stages | `gawp.stages` | Assigns meiotic stage names to foci |

Each application decides which of these plugins to install.
A minimal workflow might use only Geometry, Foci, and Join in order to create a table that has positions of foci and their attributes, skipping the linearization step.
At the other extreme, a project can use all of the plugins to implement the full linearization pipeline.

The sections below have short descriptions of each plugin.
Complete details are in the Plugins section (linked in the menu bar on the left).

### IO

Jupyter notebooks and command line applications all need to open XLS files exported from Imaris, read data from different sheets inside those spreadsheets, and save results.
But notebooks and scripts have different requirements.

- Someone using a notebook can focus in a single data set, often to explore how different steps of the workflow apply to that data. They can tell GAWP which spreadsheet they want to open and tell it exactly what they want it to do with that notebook.  The results of different steps are displayed in the notebook, and that may be all the user needs to see -- there is no need to write the results to a file.

- A user running GAWP from the command line has different goals.  They know exactly what the steps are, and they want GAWP to apply those steps to several different spreadsheets, maybe even every spreadsheet in a folder exported by Imaris.  They also want the results of running the pipeline saved in a new directory, where output file names are derived from the input file names.  They also might want to have GAWP generate a log file so there is a record of what it did.

GAWP's `io` module supports both of these use cases. The **plugin named IO** is used by command line applications to manage interactions with multiple spreadsheets. The module also defines **standalone functions**, such as `parse_spreadsheet`, that can be called from notebooks.
Not surprisingly, the plugin calls the standalone functions -- it's goal is to automate the workflow by calling these functions automatically for every spreadsheet the user wants to analyze.

### Geometry, Foci, and Measurements

The locations of foci, measurements, and other items are typically saved on the "Positions" sheet of spreadsheets exported by Imaris.
GAWP's Geometry plugin reads and organizes this data.

To use some terminology from object-oriented programming, Geometry is the **base** class, and Foci and Measurements are **derived** classes.
The Geometry plugin has operations common to all items on the "Positions" sheet: the name of the sheet, the name of the column used to distinguish foci from the other items, and the $x$ and $y$ locations of the data.

Foci and Measurements have operations specific to those types of data:

- foci are saved an initial data frame that will be used as input to the linearization algorithm

- measurement points are saved in a data frame, and then another frame, holding line segments, is built by connecting adjacent measurements

If a project works with foci the configuruation needs to include both the Geometry and Foci plugins.
If Measurements plugin is included in the configuration the linearization algorithm will be called.

The final result computed by the Geometry plugins will be a data frame that is indexed by the names of foci and with columns for the $x$ and $y$ locations and other attributes of the foci.

As the remaining plugins are executed they will columns to the table.

### Join

If an Imaris spreadhseet has additional data besides positions of foci this other data can be copied to the output with a Join plugin.

A project might want to copy several different types of data, which means the configuration can have several different `join` sections.

A key point is the other sheets must have the same columns used to create IDs for the foci.
The Join plugin will read another sheet, find the column requested in the configuration, and adds it to the output frame.

### Group

The Group plugin is similar to Join, but it has a twist.
After reading the data from the specified sheet, the rows are grouped and then an "aggregation function" is applied to each group.
The result of the aggregation is added as a new column in the output frame.

### Stages

If a project has a spreadsheet that defines meiotic stages the Stages plugin will use that spreadsheet to add a new column to the output frame.

