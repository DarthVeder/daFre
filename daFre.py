# daFre.py is a controlling script to generate e final xml for duDAT
# karaoke.
#-*- coding:  utf-8 -*-

import shutil
import split
import io
import logging

# Book under forced alignement:
volume_name = u'echanges'

# Task required:
build_dirs = False
copy_audio_files = False
split_text = True
flag ='all'  #'all' 'xml'


# logging.INFO WARNING ERROR CRITICAL
def mainLogging():
    logging.basicConfig(filename='daFre.log', filemode = 'w', \
                        format='%(levelname)s %(module)s: %(message)s', \
                        level = logging.DEBUG)    

def readUnits(unit):
    fin = io.open('list.txt', encoding='utf-8', mode='r')
    u = 1
    for l in fin:        
        if l.find('DEMO') == -1 and l.find('DONE') == -1:
            tmp = l.split('/')
            title1 = tmp[0]
            base = title1.split('-')[0]
            other = tmp[1].split('p') 
            title2 = base + other[0]
            page1_num = int(other[1])
            page1 = 'Page ' + str(page1_num)
            page2_num = int(other[2])
            page2 = 'Page ' + str(page2_num)
            afile1 = 'v1u'+str(u)+'_'+volume_name+'_p'+str(page1_num)+'.mp3'
            oafile1 = 'u'+str(u)+'_dialogue_1.mp3'
            afile2 = 'v1u'+str(u)+'_'+volume_name+'_p'+str(page2_num)+'.mp3'
            oafile2 = 'u'+str(u)+'_dialogue_2.mp3'

            file_name1 = {}
            file_name1['oldaudio'] = oafile1
            file_name1['dir'] = '.\\audio_karaoke_echanges\\'
            file_name1['newaudio'] = afile1
            file_name1['oldtext'] = oafile1.replace('mp3','txt')

            file_name2 = {}
            file_name2['oldaudio'] = oafile2
            file_name2['dir'] = '.\\audio_karaoke_echanges\\'
            file_name2['newaudio'] = afile2
            file_name2['oldtext'] = oafile2.replace('mp3','txt')

            # Storing for unit u both title and audio files (relative file names) and relative pages
            logging.info('Storing unit %s', u)
            unit[u] = (title1,title2,file_name1,file_name2,page1,page2)
        else:
            logging.info('Dropping unit %s', u)
            
        u = u + 1

if __name__ == '__main__':
    mainLogging()
    # reading required units
    unit = {}
    readUnits(unit)
    
    for u in unit.keys():
        title1,title2,file_name1,file_name2,page1,page2 = unit[u]        
        
        # destination folder names
        destination_dir = []
        destination_dir.append(file_name1['newaudio'].split('.')[0])
        destination_dir.append(file_name2['newaudio'].split('.')[0])
        
        # preparing destination directory if required        
        if build_dirs:            
            shutil.copytree('template\www',destination_dir[0])
            shutil.copytree('template\www',destination_dir[1])

        # copying original mp3 to new destination with new name, if flag is active
        if copy_audio_files:
            for i in range(1,3):
                file_name = unit[u][i+1]
                oafile = file_name['oldaudio']
                afile = file_name['newaudio']
                file_to_move = '.\\audio_karaoke_echanges\\'+oafile
                file_new_name =  '.\\' + destination_dir[i-1] + "\\mp3\\" + afile
            
                logging.debug('Audio file to move: %s into %s',file_to_move, file_new_name)
                shutil.copyfile(file_to_move, file_new_name)
        #print(page1, title1, file_name1, file_name2)

        # building label file
        if split_text:
            logging.info('processing Unit %s', u)
            split.split(u, '1', page1, title1, file_name1, flag)
            split.split(u, '2', page2, title2, file_name2, flag)

            

