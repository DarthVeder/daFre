#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import re
import writeXml
import io
import logging
import collections
import os
from mutagen.mp3 import MP3

dictionary = { 'eng': [u'and', u'of', u'the', u'to', u'and' , u'from'],
               'fra': [u'et']} 

def maxSplit(language, p):
    n_split = 0
    k_n = u''
    for k in dictionary[language]:        
        split_command = r' \b(?=\b' + k + r')+'
        cks = re.split(split_command, p)
        if len(cks) > n_split:
            n_split = len(cks)
            k_n = k
            
    split_command = r' \b(?=\b' + k_n + r')+'
    
    return re.split(split_command, p)
    

def split(language, unit, page, dialogue_title, file_name, flag, use_dictionary):
    """
    This function split a given text file following some syntacti rules and following a dictionary.
    It also calls the synchornization library aeneas
    """
    
    # Storing the ordered name of the characters
    character_name = collections.OrderedDict()
    # text spoken by each character (character_name, line_number)
    speech_text_lines      = [] 
    to_print               = [] 
    speech_line_spoken_by  = []
    path           = file_name['dir']
    dialogue_file  = file_name['oldtext']
    audio_file     = file_name['oldaudio']
    new_audio_file = file_name['newaudio']
    base_file_name = file_name['file']
    
    logging.info('Splitting required')
    logging.info('Dialogue File: %s', dialogue_file)
    # input text
    logging.debug('Path: %s; dialogue file: %s', path, dialogue_file)
    # input text file with required base splitting
    fin = io.open(path + dialogue_file, encoding='utf-8', mode='r')
    # output file with new splitting based on dictionary, base splitting
    # and !?,;:.
    out_file   = path + base_file_name + '_mysplit.txt'
    file_mode  = u'w'
    split_file = io.open(out_file, encoding='utf-8', mode=file_mode)

    # Variable used to check if the character name has been found and stored
    character_name_is_set = False
    num_line    = 0 # this variable stores each line number (starting from
                    # 1) in the
                    # fout file. The first line is reserved to the title,
                    # this is why num_line is 2

    # Flag used to identify the first line of the fin file reserved
    # to the title    
    if use_dictionary == True:
        logging.debug('Using dictionary language \'%s\'', language)
    else:
        logging.debug('Using NO dictionary')
    set_mp3_title = False
    for l in fin:        
        if not set_mp3_title:
            if l != '\n': # if title not a blank line, else do nothing
                dialogue_title = l.strip('\n')
                # writing dialogue title to file for mp3 synchronization   
                split_file.write(dialogue_title + u'\n')
            else:
                split_file.write(u'\n')
            set_mp3_title = True
        elif l != '\n' and l.find(r'\b') == -1:            
            word = l.split(' ')            
            ist = 0
            logging.debug('Words: %s', word)
            # first word of the line is not a key and the name of who's talking
            # is not set
            if word[0] not in character_name and not character_name_is_set:
                key         = word[0].strip(':') # name of who's speaking
                character_name[key]   = [] # preparing for the phrase(s) that will be spoken                
                character_name_is_set = True
                ist         = 1        
                speech_line_spoken_by.append((key,num_line))
                key_num_line = key + u' ' + str(num_line)
                logging.debug('. %s', key_num_line)
            # the first word is a name already present
            elif word[0] in character_name:
                character_name_is_set = True                    
                key         = word[0].strip(':')                
                ist         = 1
                speech_line_spoken_by.append((key,num_line))
                key_num_line = key + u' ' + str(num_line)
                logging.debug('.. %s', key_num_line)
            # There is no name in the first word    
            else:
                ist = 0            
            
            # splitting the phrase if required            
            phrase = " ".join(word[ist:])            
            character_name[key].append(phrase.strip('\n '))
            wd = phrase.split()        
            if len(wd) <= 2:
                # By default 2 words are kept together                
                split_file.write(phrase)                
                speech_text_lines.append(phrase.strip('\n '))
                to_print.append(0)
                num_line = num_line + 1
            else:                
                # Building speech line by line, storing how many split per line per author
                ck = re.split(r'(?<=[.,;?!:]) +', phrase.strip('\n '))
                for p in ck:                              
                    #cks = re.split(r' \b(?=\bet)+', p) # old version
                    # splitting on dictionary
                    if use_dictionary == True:                        
                        cks = maxSplit(language, p)
                        for cksi in cks:
                            split_file.write(cksi + u'\n')
                            speech_text_lines.append(cksi.strip('\n '))
                            to_print.append(0)
                            num_line = num_line + 1
                    else:                        
                        split_file.write(p + u'\n')
                        speech_text_lines.append(p.strip('\n '))
                        to_print.append(0)
                        num_line = num_line + 1
                #split_file.write(u'\n')
    
        elif l.find(r'\b') != -1:            
            comment_text = l.strip('\n')
            speech_text_lines.append(comment_text)
            to_print.append(1)
            num_line = num_line + 1    
        else:
            character_name_is_set = False
        

    fin.close()
    split_file.close()

    
    for k in character_name.keys():
        logging.debug('Character %s, type unicode %s', k, isinstance(k,unicode))

    for i in range(len(speech_text_lines)):
        logging.debug('%s %s %s', i, to_print[i], speech_text_lines[i])

    # Finding duration (s) of audio file:    
    audio = MP3(path+audio_file)
    tend_s = audio.info.length # seconds

    # forced alignment between audio and text, if required. The splitting is inside "mysplit.txt"    
    out_map = path + base_file_name + '_map.txt'
    logging.debug('Map file: %s',out_map)
    if flag != 'nosync':
        logging.info('Synchronization required')
        aeneas_shift = u' -r=mfcc_window_shift=0.012 '
        command =   u'python -m aeneas.tools.execute_task ' \
                  + path + audio_file + u' ' + out_file \
                  + u' \"task_language=' + language \
                  + u'|os_task_file_format=audm|is_text_type=plain\" ' \
                  + out_map \
	          + ' --presets-word '\
	          + aeneas_shift
        os.system(command)
        logging.debug('Aeneas command: %s',command)

    # preparing the structure with the timing
    if aeneas_shift != '':
        out_map = out_map.split('-')[0]
        logging.debug('Found aeneas specific shift: %s', aeneas_shift)
    
    fin = io.open(out_map, encoding='utf-8', mode='r')

    # parsing the time map
    t_start = []
    # first line is gnored, since it is the title of the dialogue
    fin.readline()
    for l in fin:
        t_start.append(l.split('\t')[0])

    logging.debug('Speech lines spoken by: %s', speech_line_spoken_by)
    

    # Binding time to speaker
    itime_start = 0
    itime_end = 0
    text_to_print = []    
    logging.debug('EXCHANGE START')        
    for i in range(len(speech_line_spoken_by) ):
        ch  = speech_line_spoken_by[i][0]
        idx = speech_line_spoken_by[i][1]        
        logging.debug('Speaker: %s / Line %s', ch, idx)
        if i != len(speech_line_spoken_by) - 1:
            idx1 = speech_line_spoken_by[i+1][1]
        else:
            idx1 = len(speech_text_lines)
        
        #speech = []
        for isp in range(idx, idx1):            
            if to_print[isp] == 0:
   #             speech.append(speech_text_lines[isp])
                itime_end = itime_end + 1
                
   #     text = [ t_start[itime_start:itime_end] , speech ]
        text = [ t_start[itime_start:itime_end] , speech_text_lines[idx:idx1] ]

        # print debug synchronization map
        for il in range(len(text[0])):
            if speech_text_lines[il].find(r'\b') == -1:
                logging.debug('%s -> %s', text[0][il], text[1][il])
        
        text_to_print.append([ch] + text)
        itime_start = itime_end

    logging.debug('EXCHANGE STOP')
   

    # Writing xml file
    logging.debug('Writing XML file')   
    out_file = path + base_file_name + '.xml'
    logging.debug('XML file: %s', out_file)
    writeXml.writeXml(language, unit, dialogue_title, page, new_audio_file, \
                      tend_s, character_name.keys(), text_to_print, out_file)


class SplitTest(unittest.TestCase):
    def test_splitting_text(self):
        unit = u'3'
        page = u'Page 56'
        dialogue_title = 'Univers perso'
        base_file_name = u'u3_canulli_p56'
        dialogue_file  = base_file_name + u'.txt'
        old_audio_file = base_file_name + u'.mp3'
        new_audio_file = u'v1u3_canulli_p56.mp3'

        file_name             = {}
        file_name['dir']      = u'./testSplit/'
        file_name['oldaudio'] = old_audio_file
        file_name['newaudio'] = new_audio_file
        file_name['oldtext']  = dialogue_file
        file_name['file']     = old_audio_file.split('.')[0]
    
        flag = 'sync' 

        split('fra', unit, page, dialogue_title, file_name, flag)

        rel_path_file = u'.' + os.sep + u'testSplit' + os.sep
        comparisonFile = rel_path_file + u'u3_canulli_p56_mysplit.sol'
        testFile      = rel_path_file + u'u3_canulli_p56_mysplit.txt'
        
        import difflib

        diff = difflib.context_diff(io.open(testFile, encoding='utf-8', mode='r').readlines(), \
                             io.open(comparisonFile, encoding='utf-8', mode='r').readlines()  )
        it = 0
        for el in diff:
            it = it + 1

        print it
        self.assertEqual(it, 0, 'Split file not equal to comparison sol file')

    def test_comments(self):
        unit = u'1'
        page = u'Page 63'
        dialogue_title = 'Anonymous from Beowulf The Coming of Beowulf '
        base_file_name = u'u1_beowulf_p63'
        dialogue_file  = base_file_name + u'.txt'
        old_audio_file = base_file_name + u'.mp3'
        new_audio_file = u'v1u1_cattaneo_p63.mp3'

        file_name             = {}
        file_name['dir']      = u'./testSplit/'
        file_name['oldaudio'] = old_audio_file
        file_name['newaudio'] = new_audio_file
        file_name['oldtext']  = dialogue_file
        file_name['file']     = old_audio_file.split('.')[0]
    
        flag = 'sync' 

        split('eng', unit, page, dialogue_title, file_name, flag)

        rel_path_file = u'.' + os.sep + u'testSplit' + os.sep
        comparisonFile = rel_path_file + u'u1_beowulf_p63_xml.sol'
        testFile      = rel_path_file + u'u1_beowulf_p63.xml'
        
        import difflib

        diff = difflib.context_diff(io.open(testFile, encoding='utf-8', mode='r').readlines(), \
                             io.open(comparisonFile, encoding='utf-8', mode='r').readlines()  )
        it = 0
        for el in diff:
            it = it + 1

        print it
        self.assertEqual(it, 0, 'Split comment xml file not equal to comparison xml file')        
        
if __name__ == '__main__':
    unittest.main()
