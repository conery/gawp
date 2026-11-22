## Output Files

The steps we've worked through so far in this tutorial follow a process we recommend each time you need to create a new GAWP workflow:

- start with a minimal configuration

- run `gawp` in with the `--preview` option on one or two data files to make sure you're getting the columns you expect

- add new stages one at a time and test the results on the same data files

In previous sections we assembled a workflow that does the linearization steps and adds columns from other sheets, and configured the workflow to apply these steps to every spreadsheet in a folder.

The last step is to save the results to output files.
For this, all we need to do is add a couple of new lines to the configuration section for the IO plugin:

- we need to tell GAWP where to put the output files

- we also want to tell it how to create the output file names

Open your configuration and edit the section labeled `[io]` so it looks like the code below.
You should already have the first line in the section, you want to add the next two.

```
[io]
spreadsheets = 'data/herm*.xlsx'
output_dir = './output'
output_name = 'linearized_{fn.stem}'
```

The `output_dir` setting tells the script to create a new directory named `output` in the current folder.

The `output_name` is a **pattern** that means "the name of the output file should be the word 'linearized' in front of the name of the input file".

After you save the updated configuration you're ready to run the script.
If you type the same command that you have used in previous steps it will still have the `--preview` option, so it will look like nothing changed:  all the output will be printed on the console.

But when you remove the `--preview` the script will save the output files.
We suggest testing the command with a single data file to make sure you're getting the output you expect:

```
$ gawp run --file data/herm_5.xlsx
```

You should now have a new folder named `output`, and inside that folder a text file named `linearized_herm_5.csv`:

```
gawp_demo
├── data
│   ├── herm_5.xlsx
│   ├── herm_7.xlsx
│   └── herm_9.xlsx
├── gawp.toml
└── output
    └── linearized_herm_5.csv
```

### Safety Switch

When you're convinced things are working, run the command again, this time without `--file`, so the script will get the file names from the configuration file and run the pipeline on all the spreadsheets:

```
$ gawp run
ERROR    Output folder gawp_demo/output conflicts with existing folder.                                                                
ERROR    Choose a different output name or rename/delete the existing folder.  
```

An error message!
The script is warning us there is an existing folder with that name.
If that folder has data you want to save, either rename the folder or edit the configuration file so it has a different output folder name.

In this case we know the only file in that folder is the one we just made, and we don't care if the script overwrites it.
We can tell `gawp` to go ahead and use this folder by adding `--force` to the command:

```
$ gawp run --conf linearize.toml --file data/*.xlsx --force
INFO     config: added geometry
INFO     config: added 
INFO     config: added
INFO     output directory: gawp_demo/output                                                                                            
INFO     Linearizing herm_5
INFO       geometry.position_frame: 100 foci
INFO       geometry.measurements_frame: 17 points
...                                                                                                                           
INFO       writing output/linearized_herm_5.csv                                                                              
INFO     Linearizing herm_7
INFO       geometry.position_frame: 100 foci
INFO       geometry.measurements_frame: 9 points
...
INFO       writing output/linearized_herm_7.csv                                                                              
INFO     Linearizing herm_9
INFO       geometry.position_frame: 100 foci
INFO       geometry.measurements_frame: 10 points
...
INFO       writing output/linearized_herm_9.csv  
```


