# -*- coding: utf-8 -*-
'''
Генерация word2vector моделей для слов.
Используется готовый корпус, в котором каждое слово отделено пробелами, и каждое
предложение находится на отдельной строке.
'''

from __future__ import print_function
from gensim.models import word2vec
import logging
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

corpus_path =  os.path.expanduser('~/Corpus/word2vector/ru/SENTx.corpus.w2v.txt')
SIZE=64
WINDOW=1
CBOW=0
MIN_COUNT=1

filename = 'w2v.CBOW=' + str(CBOW)+'_WIN=' + str(WINDOW) + '_DIM='+str(SIZE)

# в отдельный текстовый файл выведем все параметры модели
with open( filename + '.info', 'w+') as info_file:
    print('corpus_path=', corpus_path, file=info_file)
    print('SIZE=', SIZE, file=info_file)
    print('WINDOW=', WINDOW, file=info_file)
    print('CBOW=', CBOW, file=info_file)
    print('MIN_COUNT=', MIN_COUNT, file=info_file)

# начинаем обучение w2v
#sentences = word2vec.Text8Corpus(corpus_path)
sentences = word2vec.LineSentence(corpus_path)
model = word2vec.Word2Vec(sentences, size=SIZE, window=WINDOW, cbow_mean=CBOW, min_count=MIN_COUNT, workers=4, sorted_vocab=1, iter=1 )
model.init_sims(replace=True)

# сохраняем готовую w2v модель
model.save_word2vec_format( filename + '.model', binary=True)
#model.save_word2vec_format( filename + '.model.txt', binary=False)

