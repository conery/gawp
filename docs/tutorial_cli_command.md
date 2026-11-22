## The `gawp` Command

Like most shell commands we run `gawp` by typing its name followed by various options and arguments.

Type this to see the "usage" message:

```
$ gawp --help
usage: gawp [-h] [--log X] {run,review,status} ...

options:
  -h, --help           show this help message and exit
  --log X
...
```

The output shows that `gawp` has **subcommands** named `run`, `review`, and `status`.
We'll focus on the first one in this tutorial since it's the command that runs a workflow.

So now we can see that to run `gawp`, we type `gawp`, then the name of the subcommand, and then any options or arguments for that subcommand.
To see the full list of options for the `run` subcommand type this:

```
$ gawp run --help
usage: gawp run [-h] [--config F] [--file F [F ...]] [--output D] [--preview] [--force]
  ...
```

Two options to learn first are `--file`, and `--preview`.

<!-- - `--config` tells `gawp` where to find the specification of which plugins to use in the workflow.
The default is `gawp.toml` in the current directory. -->

- `--file` is the name of the input file (Imaris spreadsheet) that has the data to analyze

- `--preview` tells the script to print the first few lines of the output on terminal (instead of saving the output in a file)

We'll introduce the remaining options as we progress through the tutorial.

Go ahead and type the command shown below.
It will run the sample workflow on a single spreadsheet named `herm_5.xlsx`:

```
$ gawp run --preview --file data/herm_5.xlsx 
...                                                                                                                                       
Preview for herm_5:
                          point                               
pdk.123  POINT (19.469 128.836)
pdk.174   POINT (1.258 138.006)
pdk.293  POINT (21.258 112.538)
...
```

!!! note "Reduce the Noise Level"
    `gawp` printed a lot of messages to the terminal along with that output.  If you want to turn off these messages type `--log quiet` after `gawp` and before `run`:

    `$ gawp --log quiet run --preview ...`

    At the other extreme, if you want more information, use `--log debug`.
    Debug messages are mainly for developers but they might have some useful information if `gawp` is not doing what you expect it to.

    **Important:**  if you use `--log` notice where it goes on the command line, after `gawp` but before `run`.

