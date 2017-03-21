# -*- coding: utf-8 -*-
import re
import writeXml
import io
import logging
import collections
from subprocess import call

def split(unit, dialogue, page, dialogue_title, file_name, flag):
    #name = {}
    name = collections.OrderedDict()
    #ordered_character = []
    speech_text = ['null', 'null']
    speech_line_spoken_by = []
    path = file_name['dir']
    dialogue_file = file_name['oldtext']
    audio_file = file_name['oldaudio']
    new_audio_file = file_name['newaudio']
    
    logging.info('Splitting required')
    logging.info('Dialogue File: %s', dialogue_file)
    # input text
    logging.debug('Path: %s; dialogue file: %s',path,dialogue_file)        
    fin = io.open(path+dialogue_file, encoding='utf-8', mode='r')
    # Splitting all the text for align with the audio
    out_file = path + u'u' + str(unit) + u'_dialogue_' + dialogue + u'_mysplit.txt'
    file_mode = u'w'
    fout = io.open(out_file,encoding='utf-8', mode=file_mode)
    
    # Differentiaiting between title of first dialogue, and title of second dialogue
    if dialogue == '1':
        long_title = u'Unité ' + str(unit) + ' ' + dialogue_title
        fout.write(long_title+'\n')
    else:
        short_title = u'Unité ' + str(unit) + ' dialogue 2'
        fout.write(short_title+'\n')

    name_is_set = False
    num_line = 2
    iid = 0
    for l in fin:
        if l != '\n':        
            word = l.split(' ')        
            ist = 0        
            # firt word of the line is not a key and the name of who's talking
            # is not set
            if word[0] not in name and not name_is_set:
                key = word[0] # name of who's speaking
                name[key] = [] # preparing for the phrase(s) that will be spoken
                #if key not in ordered_character:
                #    ordered_character.append(key)
                name_is_set = True
                ist = 1        
                speech_line_spoken_by.append((key,num_line))
            # the first word is a name already present
            elif word[0] in name:
                name_is_set = True                    
                key = word[0]
                #if key not in ordered_character:
                #    ordered_character.append(key)
                ist = 1
                speech_line_spoken_by.append((key,num_line))
            # There is no name in the first word    
            else:
                ist = 0            
            
            # splitting the phrase if required            
            phrase = " ".join(word[ist:])
            name[key].append(phrase.strip('\n'))
            wd = phrase.split()        
            if len(wd) <= 2:
                fout.write(phrase)
                num_line = num_line + 1
                speech_text.append(phrase.strip('\n'))
            else:            
                ck = re.split(r'(?<=[.,;?!:]) +',phrase.strip('\n'))
                for c in ck:
                    fout.write(c+'\n')
                    num_line = num_line + 1
                    speech_text.append(c.strip('\n'))
            # Building speech line by line, storing how many split per line per author
        else:
            name_is_set = False

    fin.close()
    fout.close()
    for k in name.keys():
        logging.debug('Charcter %s, type unicode %s', k, isinstance(k,unicode))

    # forced alignment between audio and text. The splitting is inside "mysplit.txt"
    if flag == 'all':    
        logging.info('Synchronization required')
        out_map = path + 'u'+ str(unit) + '_dialogue_' + dialogue + '_map.audm'
        logging.debug('Map file: %s',out_map)
        call('python -m aeneas.tools.execute_task '+path+audio_file+' '+out_file+ \
             ' \"task_language=fr|os_task_file_format=audm|is_text_type=plain\" '+out_map)

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
        #for i in speech_line_spoken_by:
        #    print(i[1])
        logging.debug('EXCHANGE START')        
        for i in range(len(speech_line_spoken_by) ):
            ch = speech_line_spoken_by[i][0]
            idx = speech_line_spoken_by[i][1]
            logging.debug('Speaker: %s',ch)
            if i != len(speech_line_spoken_by) - 1:
                idx1 = speech_line_spoken_by[i+1][1]
            else:
                idx1 = len(speech_text)
            text = [ t_start[idx-2:idx1-2] , speech_text[idx:idx1] ]            
            #for j in text:
            #    print(j)
            text_to_print.append([ch] + text)

        logging.debug('EXCHANGE STOP')
        #for i in text_to_print:
        #    print(i)
    
    # Writing xml file
    if flag == 'xml' or flag == 'all':
        logging.debug('Writing XML file')
        out_file = path + u'u' + str(unit) + u'_dialogue_' + dialogue + '.xml'
        logging.debug('XML file: %s', out_file)
        #writeXml.writeXml(unit, dialogue_title, page, new_audio_file, ordered_character, text_to_print, out_file)
        writeXml.writeXml(unit, dialogue_title, page, new_audio_file, name.keys(), text_to_print, out_file)


if __name__ == '__main__':
    unit = u'2'
    page = u'Page 28'
    dialogue_title = 'Tu es sportif, nest-ce pas? - Dialogue 1'

    dialogue = u'1'
    dialogue_file = u'u2_dialogue_1.txt'
    old_audio_file = dialogue_file.replace('txt','mp3')
    new_audio_file = u'v1u2_echanges_p28.mp3'
    file_name = {}
    file_name['dir'] = u'.\\audio_karaoke_echanges\\'
    file_name['oldaudio'] = old_audio_file
    file_name['newaudio'] = new_audio_file
    file_name['oldtext'] = dialogue_file

    flag = 'all' # 'xml'

    split(unit, dialogue, page, dialogue_title, file_name, flag)
