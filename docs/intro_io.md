## Input and Output

Jupyter notebooks and command line applications all need to open XLS files exported from Imaris, read data from different sheets inside those spreadsheets, and save results.
But notebooks and scripts have different requirements.

- Someone using a notebook can focus in a single data set, often to explore how different steps of the workflow apply to that data. They can tell GAWP which spreadsheet they want to open and tell it exactly what they want it to do with that notebook.  The results of different steps are displayed in the notebook, and that may be all the user needs to see -- there is no need to write the results to a file.

- A user running GAWP from the command line has different goals.  They know exactly what the steps are, and they want GAWP to apply those steps to several different spreadsheets, maybe even every spreadsheet in a folder exported by Imaris.  They also want the results of running the pipeline saved in a new directory, where output file names are derived from the input file names.  They also might want to have GAWP generate a log file so there is a record of what it did.

GAWP's `io` module supports both of these use cases. The **plugin named IO** is used by command line applications to manage interactions with multiple spreadsheets. The module also defines **standalone functions**, such as `parse_spreadsheet`, that can be called from notebooks.
Not surprisingly, the plugin calls the standalone functions -- it's goal is to automate the workflow by calling these functions automatically for every spreadsheet the user wants to analyze.

!!! summary "Summary:  IO in the Workflow"

    Every project starts by opening data exported from Imaris.

    - a notebook will import the standalone functions, then call them to open a spreadsheet file and extract data from one or more sheets

    - a command line script must use the IO plugin; the plugin will automate the opening of spreadsheets and extracting data

    **Note:** Although the IO plugin was designed for scripts, it can also be imported by a notebook if a user wants to work with more than one Imaris data set at a time.
