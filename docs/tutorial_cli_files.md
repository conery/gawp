## Input Files

The `--file` argument on the command line can contain wildcards.
This example tells `gawp` to run the pipeline on all the files in the `data` directory:

```
$ gawp --log quiet run --preview --file data/* 

Preview for herm_5:
        seg_name                   point                    head                   tail   distance ...
uid
pdk.123       AB  POINT (19.469 128.836)  POINT (38.501 141.542)  POINT (39.457 120.56)  19.590598 ...
pdk.174       AB   POINT (1.258 138.006)  POINT (38.501 141.542)  POINT (39.457 120.56)  37.365346 ...
...

Preview for herm_7:
        seg_name                   point                    head                   tail   distance ...
uid
pep.217       FG  POINT (120.258 57.426)  POINT (123.785 59.548)  POINT (99.631 51.754)   0.936370 ...
pep.263       FG  POINT (115.396 57.698)  POINT (123.785 59.548)  POINT (99.631 51.754)   0.815551 ...
...

Preview for herm_9:
        seg_name                   point                    head                   tail   distance  ...
uid
pdk.148       IJ     POINT (54.723 37.05)    POINT (63.489 49.701)    POINT (49.47 41.754)   6.682733 ...
pdk.149       IJ    POINT (58.296 33.857)    POINT (63.489 49.701)    POINT (49.47 41.754)  11.222490 ...
...
```

Another way to tell `gawp` where to find the input files is to add an IO plugin to the configuration file and to define the file names in the `spreadsheet` option.

Open `gawp.config` with your editor and add this section:

```
[io]
spreadsheets = 'data/*.xlsx'
```

Now that the file names are defined in the configuration file we don't need the `--file` option on the command line.
This "minimal" command will get the input file names from `gawp.toml` and run the pipeline in preview mode:

```
$ gawp run --preview
```

### Command Line Takes Precedence

If a configuration file defines spreadsheet names in an IO plugin and there is a `--file` option in the command the name(s) on the command line are used.

On a related note, if there is no IO plugin and the command does not have a `--file` option the script will print an error message since it doesn't know where to find input files.
