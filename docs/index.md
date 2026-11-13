# GAWP:  Germline Analysis with Pandas

GAWP is a rewrite and extension of the original Germline Analysis Pipeline (GAP) from the Libuda Lab at the University of Oregon.[^1]

[^1]: Toraason, Erik, Victoria L. Adler, Nicole A. Kurhanewicz, et al. “Automated and Customizable Quantitative Image Analysis of Whole _Caenorhabditis Elegans_ Germlines.” Genetics 217, no. 3 (2021): iyab010. https://doi.org/10.1093/genetics/iyab010.

Our main goal for developing a new script was that we wanted a version that was written in Python and that allowed users to run the code either from the command line or a Jupyter notebook.
We also wanted to make it easier for users to adapt the script for new projects.

The result is a new organization based on **plugins**.
GAWP has a set of independent modules that perform individual steps of the analysis pipeline.
Before running GAWP, users create a **configuration file** that tells the system the plugins to use and thus which steps to run.

The configuration file specifies the sheets from the Imaris output that have the data to use, which columns on those sheets have the relevant data, and various other parameters.
The end result is that no settings are "hard wired" into the code -- everything is defined in the configuration file.
This should make it easier for new users in the future to run the code on their own data sets (and potentially make it easier to adapt to new data formats from different versions of Imaris).

### Road Map

The sidebar to the left shows the major sections of the documentation.

- **Installation** explains how to install GAWP using pip (Python's package installer)

- **Overview** has a high-level description of what each plugin does and how to configure a notebook or script to use plugins

- **Plugin Reference** has a detailed description of each plugin, along with a complete list of all the options

- **Developer** has documentation for people who want to dig in to the Python code
