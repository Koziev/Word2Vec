from __future__ import print_function
import gensim
#import fasttext
from gensim.models.wrappers import FastText
import sys

model_path = '/home/eek/polygon/w2v/fasttext_model'

print( 'Loading fasttext model...' )
model = FastText.load_fasttext_format(model_path)


while True:
    w1 = raw_input('word1: ').decode(sys.stdout.encoding).strip().lower()
    w2 = raw_input('word2: ').decode(sys.stdout.encoding).strip().lower()
    print( 'similarity=', model.similarity( w1, w2 ) )
