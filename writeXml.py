#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
from lxml import etree as ET
import logging

unit_text      = { 'fra': u'Unité ', 'eng': u'Unit '}
character_text = { 'fra': u'Teller', 'eng': u'Speaker' }
character_id   = string.lowercase[:26]

def writeXml(language, unit, dialogue_title, page, audio_file, tend, character, text_to_print, out_file):
    name_to_id = {}
    root       = ET.Element('karaoke_config')
    b          = ET.SubElement(root, 'book_info')
    u          = ET.SubElement(b, 'unit')    
    u.text     = unit_text[language] + str(unit)
    p          = ET.SubElement(b, 'page')
    p.text     = page
    t          = ET.SubElement(b, 'title')
    t.text     = dialogue_title
    
    k      = ET.SubElement(root, 'karaoke')
    a      = ET.SubElement(k, 'audio')
    a.text = audio_file
    l      = ET.SubElement(k, 'lang')
    l.text = language

    c = ET.SubElement(k, 'characters')

    if character_text[language] not in character:        
        c1 = ET.SubElement(c, 'character')
        c1.attrib['id'] = 'teller'
        c1.attrib['visible'] = 'false'
        
    idx = 0    
    for ch in character:
        c1 = ET.SubElement(c, 'character')        
        c1.attrib['id'] = character_id[idx]
        if ch == character_text[language]:
            c1.attrib['visible'] = 'true'            
        name_to_id[ch] = character_id[idx]        
        c1.text        = ch
        idx            = idx + 1

    s = ET.SubElement(k, 'subtitles')
    
    for i in range(0,len(text_to_print)):
        lr = ET.SubElement(s, 'line')
        lr.attrib['ref'] = name_to_id[text_to_print[i][0]]
        time = text_to_print[i][1][:]
        phrase = text_to_print[i][2][:]
        for j in range(0,len(time)):            
            tmp                 = float(time[j])            
            time_string         = ' %.6f ' % tmp
            cue                 = ET.SubElement(lr, 'cue')
            cue.attrib['start'] = time_string            
            cue.text            = phrase[j]    

    cue = ET.SubElement(s, 'cue')
    cue.attrib['start'] = '%.6f' % tend
    
    tree = ET.ElementTree(root)
    logging.info('Printing: %s', out_file)
    tree.write(out_file, pretty_print=True, encoding='utf-8')        

if __name__ == '__main__':
    unit = u'3'
    dialogue_title = u'Tu vas au cours de piano? - Dialogue 2'
    page = u'Page 57'
    audio_file = u'v1u3_echanges_p57.mp3'
    character = ['Nathan', 'Abdou']
    out_file = 'myxml.xml'
    text_to_print = []
    text_to_print.append(['Nathan', ['8.800'], ['Salut Abdou!']])
    text_to_print.append(['Abdou',  ['10.160', '11.120'], ['Salut Nathan!', '\xc3\x87a va?']])
    
    writeXml('fr', unit, dialogue_title, page, audio_file, character, text_to_print, out_file)
