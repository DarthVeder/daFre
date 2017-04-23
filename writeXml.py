#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
from lxml import etree as ET
import logging

unit_text      = { 'fra': u'Unité ', 'eng': u'Unit '}
character_text = { 'fra': u'Teller', 'eng': u'Speaker' }
character_id   = string.lowercase[:26]
xml_language   = { 'fra' : u'fr', 'eng': u'en'}

def writeXml(language, unit, dialogue_title, page, audio_file, \
             tend, character, text_to_print, out_file):
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
    l.text = xml_language[language]

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
        
        itime = 0
        for j in range(0,len(phrase)):            
            is_comment = False
            if phrase[j].find(r'\b') != -1:
                is_comment = True                
                
            if not is_comment:                
                tmp                 = float(time[itime])            
                time_string         = ' %.6f ' % tmp
                cue                 = ET.SubElement(lr, 'cue')
                cue.attrib['start'] = time_string            
                cue.text            = phrase[j]
                itime = itime + 1
            elif is_comment:
                comment_text = phrase[j].split(r'\b')[1]                
                if comment_text.replace(' ','') == '':
                    comment_text = u'<br />'
                    
                cue      = ET.SubElement(lr, 'print_html')                
                cue.text = ET.CDATA(comment_text) 
                
            

    cue = ET.SubElement(s, 'cue')
    cue.attrib['start'] = '%.6f' % tend
    
    tree = ET.ElementTree(root)
    logging.info('Printing: %s', out_file)
    tree.write(out_file, pretty_print=True, encoding='utf-8')        

if __name__ == '__main__':
    pass
