## Run GAWP from the Command Line

The `gawp` script installed by Python is designed for "batch processing" of several Imaris outputs.

In this tutorial we'll start out with a minimal configuration file and show how to execute the workflow it defines.
Then we'll add more plugins to illustrate additional features of the command line application.

### Sample Data and Project Directory

An archive with sample data can be downloaded from GitHub.
To start this tutorial download and unzip the folder.
You should end up with a new folder named `gawp_demo` with the following items:

```
gawp_demo
├── data                    # a folder for the sample notebooks
│   ├── herm_5.xlsx         # three Imaris spreadsheets with sample data
│   ├── herm_7.xlsx
│   └── herm_9.xlsx
├── gawp.toml               # project configuration file
```

Throughout the rest of the tutorial we'll assume you will be running `gawp` from this folder.

