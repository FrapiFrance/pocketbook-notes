#!/bin/python
# -*- coding: utf-8 -*-

import json

def print_json(json_data,quiet=False):
    """print and return a nice version of json_data

    Args:
        json_data (_type_): json/dict
        quiet (bool): do not print, only returns
    Returns:
        a string nicely formatted
    """
    nice_formatted_json_string = json.dumps(json_data, sort_keys=False, indent=4, ensure_ascii=False )
    if not quiet:
        print(nice_formatted_json_string)
    return nice_formatted_json_string