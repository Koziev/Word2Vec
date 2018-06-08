# -*- coding: utf-8 -*-
'''
'''

from __future__ import print_function
import os
import fasttext

SIZE=32
WINDOW=5
CBOW=1
MIN_COUNT=1

corpus_path =  os.path.expanduser('~/Corpus/word2vector/ru/SENTx.corpus.w2v.txt')

# Skipgram model
filename = 'fasttext.CBOW=' + str(CBOW)+'_WIN=' + str(WINDOW) + '_DIM='+str(SIZE)
if CBOW == 0:
    model = fasttext.skipgram(input_file=corpus_path, dim=SIZE, ws=WINDOW, min_count=1, thread=4, silent=0, output=filename)
    #print model.words # list of words in dictionary
else:
    # CBOW model
    model = fasttext.cbow(input_file=corpus_path, dim=SIZE, ws=WINDOW, min_count=1, thread=4, silent=0, output=filename)
    #print model.words # list of words in dictionary
