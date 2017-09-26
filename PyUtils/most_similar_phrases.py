# -*- coding: utf-8 -*-
from __future__ import print_function
"""
Эксперимент для проверки возможности испоьзования среднего невзвешенного w2v вектора
для сравнения близости двух фраз.

Сценарий эксперимента.

1) С клавиатуры вводим фразу - несколько разделенных пробелами слов
2) Модель вычисляет средний вектор этих слов
3) Идем по корпусу подготовленных предложений, в которых слова уже разделены пробелами и нормализованы
4) Ищем и показываем top n ближайших фраз
"""

import gensim
import scipy.spatial.distance
import numpy as np
import codecs
import collections
import math
import sys
import gc

# w2v_path = r'/home/eek/polygon/w2v/word_vectors_cbow=1_win=5_dim=32.txt'
corp_path = r'f:\Corpus\SENTx\ru\SENT5.txt'
w2v_path = r'f:\Word2Vec\word_vectors_cbow=1_win=5_dim=32.txt'

def v_cosine( a, b ):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))


print('Loading w2v model...')
w2v = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=False)

nword = len(w2v.vocab)
print('Number of words={0}'.format(nword))
vec_len = len(w2v.syn0[0])
print('Vector length={0}'.format(vec_len))

while True:
    words = raw_input('word(s): ').decode(sys.stdout.encoding).strip().lower().split(u' ')
    if len(words) > 0:
        v = np.zeros( vec_len )
        denom=0
        for word in words:
            if word in w2v:
                v += w2v[word]
                denom += 1
            else:
                print(u'Word {} is missing in lexicon'.format(word))

        if denom>0:
            query_v = v/denom

            sent_rel = []

            try:
                with codecs.open(corp_path, 'r', 'utf-8') as rdr:
                    sent_count=0
                    for line in rdr:
                        words = line.strip().lower().split(u' ')

                        v = np.zeros( vec_len )
                        denom=0
                        sent_ok = True
                        for word in words:
                            if word in w2v:
                                v += w2v[word]
                                denom += 1
                            else:
                                sent_ok = False
                                break

                        if sent_ok:
                            sent_v = v / denom
                            sim = v_cosine(query_v, sent_v)
                            sent_rel.append( (line.strip(), sim) )
                            sent_count += 1

                            if (sent_count%10000)==0:
                                print('\nAfter {} sentences processed the most similar sentences are as follows:'.format(sent_count))
                                for sent,sim in sorted(sent_rel, key=lambda z:-z[1])[:10]:
                                    print(u'{} ==> {}'.format(sent,sim))

                                if sent_count > 1000000:
                                    break
            except KeyboardInterrupt:
                print('Search is interrupted.')

            print('\n\nFinal results:')
            for sent, sim in sorted(sent_rel, key=lambda z: -z[1])[:10]:
                print(u'{} ==> {}'.format(sent, sim))
            print('\n')
