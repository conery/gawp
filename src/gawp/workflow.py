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
import logging

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
    
    output_dir = plugins.io.make_output_dir(args)
    if plugins.stages:
        plugins.stages.read_stage_boundaries()

    for fn in plugins.io.get_spreadsheet_names(args):
        res = run_workflow(fn)
        print(res.head())


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
    plugins.geometry.apply(xls_file)
    plugins.geometry.linearize()
    if plugins.join:
        cols = plugins.join.apply(xls_file)
        plugins.geometry.add_columns(cols)
    print(plugins.geometry.linearized_frame.head())
    if plugins.stages:
        cols = plugins.stages.apply(fn, plugins.geometry.linearized_frame[['seg_name']])
        if cols is not None:
            plugins.geometry.add_columns(cols)
        else:
            logging.error(f'  no meiotic stage assignments for {fn}')
    return plugins.geometry.linearized_frame
