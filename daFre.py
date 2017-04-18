#!/usr/bin/env python
#-*- coding:  utf-8 -*-
# daFre.py is a controlling script to generate a final xml for duDAT
# karaoke.

import shutil
import split
import io
import os
import logging
import ConfigParser
import sys
import glob

# Task required:
split_text = True
flag ='sync'  #sync to force align with aeneas. Any other value to force align

# logging.INFO WARNING ERROR CRITICAL
def mainLogging():
    logging.basicConfig(filename='daFre.log', filemode = 'w', \
                        format='%(levelname)s %(module)s: %(message)s', \
                        level = logging.DEBUG)    

def parse(rel_file_name):
    """
    Configuration file parser
    """
    dict1 = {}
    config = ConfigParser.ConfigParser()
    config.read(rel_file_name)

    options = config.options('default')
    for option in options:
        dict1[option] = config.get('default',option)

    # Check that the directory entries end with a slash:
    if not dict1['source_directory'].endswith('/'):
        sys.exit('Check end slash in source_directory')

    if not dict1['destination_directory'].endswith('/'):
        sys.exit('Check end slash in destination_directory')

    return dict1

def readUnits(config):
    """
    Input file must be in the following form:
    u#_word_p#.mp3

    u5_ancient_marinar.mp3
    u5
    ancient
    marinar
    p192
    (.)
    mp3

    NB: the audio title spoken in the mp3 BEFORE the start of any dialogue,
    MUST be put in the first line of unit_dialogue.txt
    """
    logging.debug('source_directory=%s',config['source_directory'])
    entries = {}    
    fin = glob.glob(config['source_directory']+u'*.mp3')
    logging.debug('len(fin)=%s',len(fin))
    e = 1
    for l in fin:
        if l.find(';;') == -1:
            source_base_file_name = l.split('/')[-1]
            tmp = source_base_file_name.split('.')[0].split('_')            
            volume = config['volume_number']
            unit = tmp[0][1]
            title_mp3 = ' '.join( tmp[2:-1] )                        
            page_num = int(tmp[-1].replace('p',''))
            page_txt = 'Page ' + str(page_num)
    
            # new audio file name
            afile = 'v' + volume + 'u' + unit + '_' + config['volume_name'] \
                        + '_p' + str(page_num) + '.mp3'
            unit_number = 'u' + unit            
            oafile = source_base_file_name           
            
            file_name = {}
            file_name['oldaudio'] = oafile
            file_name['dir'] = config['source_directory']
            file_name['newaudio'] = afile
            file_name['oldtext'] = oafile.replace('mp3','txt')
            file_name['file'] = oafile[:oafile.rfind('.')]

            # Storing entry
            logging.info('Storing entry %s', e)
            logging.debug('Base file name: %s', file_name['file'])
            entries[e] = (title_mp3,file_name,page_txt,unit)
        else:
            logging.info('Dropping entry %s', e)
            
        e = e + 1
        
    return entries

if __name__ == '__main__':    
    mainLogging()
    logging.info('Starting...')
    # reading config.ini file
    logging.info('Parsing config file...')
    config = parse('config.ini')
    language = config['language']
    logging.info('Done')
    
    # reading required entries
    logging.info('Reading mp3 files to process...')
    config_file = 'config.ini'
    entries = {}
    entries = readUnits(config)
    logging.info('Done')

    logging.info('Examining each entry...')
    for e in entries.keys():
        logging.debug('Entry %s',e)
        title,file_name,page,unit = entries[e]        
        
        # destination folder names
        destination_dir = file_name['newaudio'].split('.')[0]
        logging.debug('desitnation_dir=%s',destination_dir)
        
        # preparing destination directory if required                
        if not os.path.isdir(destination_dir):
            shutil.copytree('template/www',destination_dir)            
            # copying original mp3 to new destination with new name, if flag is active        
            oafile = file_name['oldaudio']
            afile = file_name['newaudio']
            file_to_move = config['source_directory'] + oafile
            file_new_name =  './' + destination_dir + "/mp3/" + afile            
            logging.debug('Audio file to move: %s into %s',file_to_move, file_new_name)
            shutil.copyfile(file_to_move, file_new_name)        

        # building label file
        if split_text:
            logging.info('processing Unit %s', unit)
            split.split(language, unit, page, title, file_name, flag)
    logging.info('Done')

            

