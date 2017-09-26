from __future__ import print_function
"""
Определение косинусной близости двух слов.
w2v модель должна быть заранее построена (см. путь w2v_path)
"""
import gensim
import sys

print( 'Loading the w2v model...' )
w2v_path = 'f:/Word2Vec/word_vectors_cbow=1_win=5_dim=32.txt'
w2v = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=False)


while True:
    w1 = raw_input('word1: ').decode(sys.stdout.encoding).strip().lower()
    w2 = raw_input('word2: ').decode(sys.stdout.encoding).strip().lower()
    print( 'similarity=', w2v.similarity( w1, w2 ) )
