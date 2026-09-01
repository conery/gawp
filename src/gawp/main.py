#! /usr/bin/env python3

# Top level application for gawp (Germline Analysis with Pandas)

import argparse
import logging
from pathlib import Path
import sys

from .config import Config, initialize_config, setup
from .console import console, setup_logging, print_config
from .io import parse_positions, read_stages, get_measurements, get_cell_positions
from .linearize import linearize

def init_cli():
    """
    Use argparse to create the command line API, then initialize the logger
    to print status messages on the console.

    Returns:
        a Namespace object with values of the command line arguments. 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', metavar='X', choices=['quiet','info','debug'], default='info')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--config', metavar='F', help='TOML file with configuration settings')
    
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    run_parser = subparsers.add_parser('run', help='linearize all Imaris files in the project')
    run_parser.set_defaults(dispatch=linearize)
    run_parser.add_argument('--file', metavar='F', nargs='+', type=Path, help='data file')
    run_parser.add_argument('--output', metavar='D', help='name of directory for output files')

    review_parser = subparsers.add_parser('review', help='review outputs for a single germline')
    review_parser.set_defaults(dispatch=review)
    review_parser.add_argument('--dir', metavar='D', type=Path, help='output directory')

    status_parser = subparsers.add_parser('status', help='print project status')
    status_parser.set_defaults(dispatch=print_status)

    setup_parser = subparsers.add_parser('setup', help='initialize a project')

    if len(sys.argv) == 1:
        parser.print_usage()
        exit(1)

    args = parser.parse_args()
    setup_logging(args.log)

    if args.command is None:
        print('command required')
        parser.print_usage()
        exit(1)

    if args.command == 'setup':
        try:
            setup(args)
        except FileExistsError as err:
            logging.error(f'File exists: {err}')
        exit(0)

    logging.debug('command line arguments:')
    for name, val in vars(args).items():
        if val is not None:
            logging.debug(f'  --{name} {val} {type(val)}')

    return args 

# Stubs for top level commands, will eventually be moved to their own source files

def review(args):
    logging.info('review')
    logging.info(str(vars(args)))

def print_status(args):
    print_config()

def main():
    """
    Top level entry point
    """
    args = init_cli()
    try:
        initialize_config(args.config)
        args.dispatch(args)
    except (ValueError, FileNotFoundError, ModuleNotFoundError) as err:
        logging.error(err)
    except Exception as err:
        console.print_exception(show_locals=True)
