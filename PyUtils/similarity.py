from __future__ import print_function
import gensim
import sys

#w2v_path = '/home/eek/polygon/w2v/w2v.CBOW=0_WIN=3_DIM=32.txt'
w2v_path = '/home/eek/polygon/w2v/w2v.CBOW=0_WIN=5_DIM=32.txt'

print( 'Loading the w2v model...' )
w2v = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=False)


while True:
    w1 = raw_input('word1: ').decode(sys.stdout.encoding).strip().lower()
    w2 = raw_input('word2: ').decode(sys.stdout.encoding).strip().lower()

    all_known = True
    for w in [w1,w2]:
        if w not in w2v:
            print(u'{} is out of vocabulary'.format(w))
            all_known = False

    if all_known:
        print( 'similarity=', w2v.similarity( w1, w2 ) )

