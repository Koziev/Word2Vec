# -*- coding: utf-8 -*-
'''
'''

from __future__ import print_function
import os
import fasttext

SIZE=64
WINDOW=5
CBOW=0
MIN_COUNT=1

corpus_path =  os.path.expanduser('~/Corpus/word2vector/ru/SENTx.corpus.w2v.txt')

# Skipgram model
model = fasttext.skipgram(input_file=corpus_path, dim=SIZE, ws=WINDOW, min_count=1, thread=4, silent=0, output='fasttext_model')
#print model.words # list of words in dictionary

# CBOW model
#model = fasttext.cbow(input_file=corpus_path, dim=64, ws=WIN, 'model')
#print model.words # list of words in dictionary
