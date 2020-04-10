# -*- coding: utf-8 -*-
"""
logger.py -- wrapper around logging module with file and console
Author Paul L. D. Roberts
Copyright 2020  Scripps Institution of Oceanography
Distributed under MIT license. See license.txt for more information.
"""

import os
import time
import logging

LOG_FILE_HANDLER = None
LOG_CONSOLE_HANDLER = None

def get_logger(filepath,file_level=logging.DEBUG, console_level=logging.WARN,logger_name=''):
    """Get a logger object initialized with console and file output

    Parameters:
    -----------
    filepath : str
        The absolue path to the file for the FileHandler
    log_level : {'DEBUG', 'INFO', 'WARNING','ERROR','CRITICAL'}
        The log level for the logger,
    logger_name : str, optional
        A string prepended to each log message

    Returns:
    --------
    lgr: logger
        An initialized logger object

    """
    # create logger
    lgr = logging.getLogger(logger_name)
    lgr.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    fh = logging.FileHandler(filepath)
    fh.setLevel(file_level)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch to lgr
    lgr.addHandler(ch)
    lgr.addHandler(fh)

    global LOG_CONSOLE_HANDLER
    LOG_CONSOLE_HANDLER = ch

    global LOG_FILE_HANDLER
    LOG_FILE_HANDLER = fh


    return lgr

# create a logs dir if it does not exist
if not os.path.exists('logs'):
    os.makedirs('logs')

LOG = get_logger(os.path.join('logs', str(int(time.time())) + '.log'),
                 file_level=logging.DEBUG,
                 console_level=logging.WARN,
                 logger_name='BUMP Image')
