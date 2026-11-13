# Use pip to Install GAWP 

GAWP is a standard Python package that can be installed using `pip`.

!!! tip
    When pip installs GAWP it is most likely going to add a lot of new libraries to your system.
    Before you install you might want to consider creating a virtual environment.
    See [Do You Need a Virtual Environment?](#do-you-need-a-virtual-environment) below.

Simply open a new terminal window and type this shell command:

```
$ pip install git+https://github.com/conery/gawp.git
```

If all the installation steps succeed you will have a new command line application named `gawp`.
You can run it with the `--help` option to make sure everything was installed correctly:

```
$ gawp --help

usage: gawp [-h] [--log X] [--preview] [--config F] {run,review,status} ...
```

You will also have a new module that you can import into your notebooks or Python scripts.
For example, the IO plugin has a function that reads a sheet from an XLS file and converts it into a Pandas dataframe.
To use this function your code could include this line:
```
from gawp.io import open_spreadsheet
```

### Do You Need a Virtual Environment?

When `pip` installs GAWP it will check to make sure all of the libraries it depends on are also installed.
Mostly these are well-known data science libraries like Pandas that you probably already have.
But there are several that you might not have:

- Shapely, a geography library we use for computing distances between points and line segments

- GeoPandas, a library that allows us to put Shapely objects in Pandas dataframes

- Rich, an all-around useful library for creating interfaces for command line applications

We strongly recommend installing GAWP in its own **virtual environment**.
That will prevent several potential problems.
For example, if you have an older version of Pandas on your system, pip will want to upgrade it, and
that could break some other programs you have that depend on the older version.

If you have recent versions of Pandas and Numpy and are not concerned with installing these new libraries
(they're not likely to conflict with any libraries you have already) then go ahead and type the pip
command to install GAWP.

But if you're ready to take control of your Python data science environments the 
best approach is to use a package named [`pyenv`](https://github.com/pyenv/pyenv)
and a companion plugin named [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv).

After you create a clean new environment activate it and then type the pip command to install GAWP.
pip will do the rest by installing Pandas and the other modules used by GAWP.

