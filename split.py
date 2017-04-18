#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import writeXml
import io
import logging
import collections
import os
from mutagen.mp3 import MP3 

def split(language, unit, page, dialogue_title, file_name, flag):
    # Storing the ordered name of the characters
    name = collections.OrderedDict()
    # text spoken by each character (name, line_number)
    speech_text = ['null', 'null']
    speech_line_spoken_by = []
    path           = file_name['dir']
    dialogue_file  = file_name['oldtext']
    audio_file     = file_name['oldaudio']
    new_audio_file = file_name['newaudio']
    base_file_name = file_name['file']
    
    logging.info('Splitting required')
    logging.info('Dialogue File: %s', dialogue_file)
    # input text
    logging.debug('Path: %s; dialogue file: %s',path,dialogue_file)
    # input text file with required base splitting
    fin = io.open(path + dialogue_file, encoding='utf-8', mode='r')
    # output file with new splitting based on dictionary, base splitting
    # and !?,;:.
    out_file  = path + base_file_name + '_mysplit.txt'
    file_mode = u'w'
    fout      = io.open(out_file,encoding='utf-8', mode=file_mode)

    # Variable used to check if the character name has been found and stored
    name_is_set = False
    num_line    = 2 # this variable stores each line number in the
                    # fout file

    # Flag used to identify the first line of the fin file reserved
    # to the title
    set_mp3_title = False
    for l in fin:
        if not set_mp3_title:
            if l != '\n': # if title not a blank line
                dialogue_title = l.strip('\n')
                # writing dialogue title to file for mp3 synchronization   
                fout.write(dialogue_title + '\n')                
            set_mp3_title = True
        elif l != '\n':
            word = l.split(' ')        
            ist = 0        
            # first word of the line is not a key and the name of who's talking
            # is not set
            if word[0] not in name and not name_is_set:
                key         = word[0].strip(':') # name of who's speaking
                name[key]   = [] # preparing for the phrase(s) that will be spoken                
                name_is_set = True
                ist         = 1        
                speech_line_spoken_by.append((key,num_line))
            # the first word is a name already present
            elif word[0] in name:
                name_is_set = True                    
                key         = word[0].strip(':')                
                ist         = 1
                speech_line_spoken_by.append((key,num_line))
            # There is no name in the first word    
            else:
                ist = 0            
            
            # splitting the phrase if required            
            phrase = " ".join(word[ist:])
            name[key].append(phrase.strip('\n'))
            wd = phrase.split()        
            if len(wd) <= 2:
                # By default 2 words are kept together
                fout.write(phrase)
                num_line = num_line + 1
                speech_text.append(phrase.strip('\n'))
            else:
                # Building speech line by line, storing how many split per line per author
                ck = re.split(r'(?<=[.,;?!:]) +',phrase.strip('\n'))
                for p in ck:
                    cks = re.split(r' \b(?=\bet)+',p)
                    for cksi in cks:
                        fout.write(cksi+'\n')
                        num_line = num_line + 1
                        speech_text.append(cksi.strip('\n'))
                
        else:
            name_is_set = False

    fin.close()
    fout.close()
    for k in name.keys():
        logging.debug('Character %s, type unicode %s', k, isinstance(k,unicode))

    # Finding duration (s) of audio file:    
    audio = MP3(path+audio_file)
    tend_s = audio.info.length # seconds

    # forced alignment between audio and text, if required. The splitting is inside "mysplit.txt"    
    out_map = path + base_file_name + '_map.txt'
    logging.debug('Map file: %s',out_map)
    if flag != 'nosync':
        logging.info('Synchronization required')
        command =   u'python -m aeneas.tools.execute_task ' \
                  + path + audio_file + u' ' + out_file \
                  + u' \"task_language=' + language \
                  + u'|os_task_file_format=audm|is_text_type=plain\" ' \
                  + out_map
        os.system(command)
        logging.debug('Aeneas command: %s',command)

    # preparing the structure with the timing        
    fin = io.open(out_map, encoding='utf-8', mode='r')

    # parsing the time map
    t_start = []
    # first line is gnored, since it is the title of the dialogue
    fin.readline()
    for l in fin:
        t_start.append(l.split('\t')[0])

    # Binding time to speaker
    text_to_print = []    
    logging.debug('EXCHANGE START')        
    for i in range(len(speech_line_spoken_by) ):
        ch  = speech_line_spoken_by[i][0]
        idx = speech_line_spoken_by[i][1]
        logging.debug('Speaker: %s',ch)
        if i != len(speech_line_spoken_by) - 1:
            idx1 = speech_line_spoken_by[i+1][1]
        else:
            idx1 = len(speech_text)
        text = [ t_start[idx-2:idx1-2] , speech_text[idx:idx1] ]            
        text_to_print.append([ch] + text)

    logging.debug('EXCHANGE STOP')
    
    # Writing xml file
    logging.debug('Writing XML file')   
    out_file = path + base_file_name + '.xml'
    logging.debug('XML file: %s', out_file)
    writeXml.writeXml(language, unit, dialogue_title, page, new_audio_file, \
                      tend_s, name.keys(), text_to_print, out_file)


if __name__ == '__main__':
    unit = u'3'
    page = u'Page 56'
    dialogue_title = 'Univers perso'
    base_file_name = u'u3_canulli_p56'
    dialogue_file  = base_file_name + u'.txt'
    old_audio_file = base_file_name + u'.mp3'
    new_audio_file = u'v1u3_canulli_p56.mp3'

    file_name = {}
    file_name['dir']      = u'./testSplit/'
    file_name['oldaudio'] = old_audio_file
    file_name['newaudio'] = new_audio_file
    file_name['oldtext']  = dialogue_file
    file_name['file']     = old_audio_file.split('.')[0]
    
    flag = 'sync' 

    split('fra', unit, page, dialogue_title, file_name, flag)
