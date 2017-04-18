# -*- coding=utf-8 -*-
# Simple tool for generating text files to store the speech of a given set
# of mp3(s).

import io

number_of_mp3 = 16

for i in range(1,number_of_mp3):
    if i != 3:
        for j in range(1,3):
            file_name = u'u'+str(i) + u'_dialogue_' + str(j) + u'.txt'
            f = io.open(file_name, encoding='utf-8', mode='a')
            f.close()
    
