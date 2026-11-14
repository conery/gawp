"""
gawp.workflow

Functions for running the linearization algorithm:

  * autorun runs the pipeline on all spreadsheets in a file and writes
    results to CSV files

  * run_workflow is a helper function that runs the algorithm on a single
    data set and returns the results in a DataFrame; can be called from a
    Jupyter notebook after it initializes plugins

"""

import argparse
from pathlib import Path
import logging

from .console import console
from .io import open_spreadsheet
from .plugin import plugins

##########################
#
# Top level function called by the command line script.  Open the output
# folder, run the workflow on each spreadsheet, saving outputs for each
#

def autorun(args: argparse.Namespace):
    '''
    Top level function of the command line script, runs the linearization 
    pipeline on all data files.
    
    Arguments:
        args:  command line arguments
    '''

    # A command line script needs the IO plugin, make sure it was installed
    if plugins.io is None:
        raise ModuleNotFoundError('Configuration does not include [io] plugin')
    
    plugins.io.make_output_dir(args)
    if plugins.stages:
        plugins.stages.read_stage_boundaries()

    for fn in plugins.io.get_spreadsheet_names(args):
        res = run_workflow(fn)
        p = plugins.io.make_output_path(fn)
        if args.preview:
            console.print(f'[bold green]Preview of {p.stem}:')
            console.print(res.head())
        else:
            logging.info(f'  writing {p}')
            res.to_csv(p)

def run_workflow(fn):
    '''
    Run the complete linearization pipeline on one spreadsheet

    Arguments:
        fn:  the name of the XLS file containing Imaris outputs

    Returns:
        a Pandas data frame with the linearized germline
    '''
    logging.info(f'[bold blue]Linearizing {fn.stem}')
    xls_file = open_spreadsheet(fn)
    plugins.io.reset_output()
    if plugins.geometry:
        plugins.geometry.apply(xls_file)
        cols = plugins.geometry.linearize()
        plugins.io.add_columns(cols)
    for p in [plugins.join, plugins.group]:
        if p is not None:
            cols = p.apply(xls_file)
            plugins.io.add_columns(cols)
    if plugins.stages:
        cols = plugins.stages.apply(fn, plugins.geometry.linearized_frame[['seg_name']])
        if cols is not None:
            plugins.io.add_columns(cols)
        else:
            logging.warning(f'  no meiotic stage assignments for {fn}')
    return plugins.io.output_frame
