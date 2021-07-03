#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
import logging.handlers

def parse_loglevel(log_level):
    dict_values = {'WARN': logging.WARN, 'INFO': logging.INFO, 'ERROR': logging.ERROR, 'DEBUG': logging.DEBUG,
                   'CRITICAL': logging.CRITICAL, 'NOTSET': logging.NOTSET}

    if log_level not in dict_values:
        raise KeyError("Log level doesn't exists in the dictionary")

    return dict_values[log_level]


def get_logger(level, job_id=None, path=None, rotate_when='midnight', name=None, backup_count=0):
    log_level = parse_loglevel(level)

    if job_id:
        log_format = '%(asctime)s - JOB ID: ' + job_id + ' - %(name)s:%(lineno)d - [%(levelname)s] : %(message)s'
    else:
        log_format = '%(asctime)s - %(name)s - [%(levelname)s] : %(message)s'

    if path:
        log_handler = logging.handlers.TimedRotatingFileHandler(path, when=rotate_when, backupCount=backup_count)
        log_handler.setFormatter(logging.Formatter(log_format))
        logger = logging.getLogger(name=name)
        logger.addHandler(log_handler)
        logger.setLevel(level)
        logger.propagate = False # To avoid a message goes backwards in the hierarchy and the parents are also logging the same thing
    else:
        logging.basicConfig(stream=sys.stdout, level=log_level, format=log_format)

    logger = logging.getLogger(name)

    return logger