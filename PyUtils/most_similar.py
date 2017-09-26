from __future__ import print_function
import gensim
import numpy as np

def v_cosine( a, b ):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))


print( 'Loading the w2v model...' )
w2v_path = 'f:/Word2Vec/word_vectors_cbow=1_win=5_dim=32.txt'
w2v = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=False)


while True:
    w = raw_input('word: ').decode('utf-8')
    for i,p in enumerate( w2v.most_similar(positive=w,topn=10) ):
        print( p[0], '==>', p[1] )

    #print( 'Most similar by vector:' )
    #v = w2v[w]
    #simx = [ (z,v_cosine(w2v[z],v)) for z in w2v.vocab ]
    #for p in sorted(simx, key=lambda z: z[1], reverse=True )[0:10]:
        #print( p[0], '==>', p[1] )
    
