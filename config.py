#-*- coding=utf-8 -*-

import ConfigParser
import io

def parse(rel_file_name):
    """
    Configuration file parser
    """
    dict1 = {}
    config = ConfigParser.ConfigParser()
    config.read(rel_file_name)

    print config.sections()

    options = config.options('default')
    for option in options:
        dict1[option] = config.get('default',option)
        #print config.get('default',option)

    return dict1            



if __name__ == '__main__':
    dict1 = {}
    dict1 = parse('config.ini')

    for k in dict1.keys():
        print dict1[k]
