# -*- coding: utf-8 -*-
'''
Клавиатурные запросы к векторной модели слов и частей слов.
'''


from __future__ import print_function
from gensim.models import word2vec
import numpy as np
import math
from difflib import SequenceMatcher

# ----------------------------------------------------------------------

def v_cosine( a, b ):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

# ----------------------------------------------------------------------

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ----------------------------------------------------------------------

print( 'Loading the w2v model...' )
w2v = word2vec.Word2Vec.load_word2vec_format('/home/eek/polygon/w2v/wordparts.CBOW=0_WIN=1_DIM=32.model', binary=True)

wordvec_len =  w2v.syn0[0].size
print( 'wordvec_len=', wordvec_len )


# загрузим частоты фрагментов слова
wordpart2freq = {}
with open( '/home/eek/polygon/w2v/wordpart.frequencies.dat', 'r' ) as dat:
    for line in dat:
        toks = line.strip().decode('utf-8').split('\t')
        wordpart2freq[ toks[0] ] = int( toks[1] )

word2freq = {}
with open( '/home/eek/polygon/w2v/word.frequencies.dat', 'r' ) as dat:
    for line in dat:
        toks = line.strip().decode('utf-8').split('\t')
        word2freq[ toks[0] ] = int( toks[1] )

# ----------------------------------------------------------------------



# ----------------------------------------------------------------------

while True:
    word = raw_input('word: ').decode('utf-8')
    
    if word in w2v.vocab:
        print( 'Known word.' )
    
        print( 'Most similar by vector:' )
        for i,p in enumerate( w2v.most_similar(positive=word,topn=10) ):
            print( p[0], '==>', p[1] )
    else:        
        print( 'Unknown word.' )
        
        wlen = len(word)
        
        # 1. Ищем совпадение по окончанию.
        print( '\n--- SEARCHING BY ENDING ---' )
        for i0 in range(1,wlen-1):
            word2 = '~'+word[i0:]
            if word2 in w2v.vocab:
                print( word2, ' is known!' )
                
                for (w,p) in [ (w,p) for (w,p) in w2v.most_similar(positive=word2,topn=1000000000) if not u'~' in w ][0:10]: # покажем только полные слова
                    print( w, '==>', p )

                break # более короткие окончания уже не ищем


        # 2. Ищем и смешиваем все части слова
        print( '\n--- SEARCHING BY PARTS ---' )
        sum_num = np.zeros( (wordvec_len) )
        sum_denom = 0
        
        for i0 in range(0,wlen-1):
            for i1 in range(i0+1,wlen):
                word2 = u''
                if i0!=0:
                    word2 += u'~'
                word2 += word[i0:i1+1]
                if i1!=wlen-1:
                    word2 += u'~'
                
                if word2 in w2v.vocab:
                    part_len = i1-i0+1
                    freq = wordpart2freq[word2]
                    score = part_len * freq
                    sum_num += w2v[word2] * score
                    sum_denom += score
                    print( 'Known part found: ', word2, '\tfreq=', freq, '\tscore=', score )
                    
        v = sum_num/sum_denom
        
        # ищем ближайшие к этому вектору слова
        simx = [ (z,v_cosine(w2v[z],v)) for z in w2v.vocab if not u'~' in z ]
        for p in sorted(simx, key=lambda z: z[1], reverse=True )[0:10]:
            print( p[0], '==>', p[1] )



        # 3. Ищем и смешиваем все части слова, причем более крупные части поглощают менее крупные
        print( '\n--- SEARCHING BY PARTS WITH SIMPLE COMPETITON ---' )

        # в отдельный        
        max_prefix = u''
        max_ending = u''
        stems = []
        for i0 in range(0,wlen-1):
            for i1 in range(i0+1,wlen):
                word2 = u''
                if i0!=0:
                    word2 += u'~'
                word2 += word[i0:i1+1]
                if i1!=wlen-1:
                    word2 += u'~'
                
                if word2 in w2v.vocab:
                  if word2.endswith(u'~') and word2.startswith(u'~'):
                      stems.append( word2[1:-1] )
                  elif word2.startswith(u'~'):
                      # оставляем самое длинное окончание
                      ending = word2[1:]
                      if len(ending)>len(max_ending):
                        max_ending = ending
                  else:
                      # оставляем самую длинную приставку
                      prefix = word2[:-1]
                      if len(prefix)>len(max_prefix):
                          max_prefix = prefix
                          
        # теперь собираем средний вектор
        sum_num = np.zeros( (wordvec_len) )
        sum_denom = 0
        
        if len(max_prefix)>0:
            part_len = len(max_prefix)
            prefix = max_prefix+u'~'
            freq = wordpart2freq[prefix]
            score = part_len * freq
            sum_num += w2v[prefix] * score
            sum_denom += score
            print( 'max_prefix =', max_prefix, '\tfreq=', freq, '\tscore=', score )

        if len(max_ending)>0:
            part_len = len(max_ending)
            ending = u'~'+max_ending
            freq = wordpart2freq[ending]
            score = part_len * freq
            sum_num += w2v[ending] * score
            sum_denom += score
            print( 'max_ending =', max_ending, '\tfreq=', freq, '\tscore=', score )

        # для stems надо оставить только самые длинные куски, а входящие в них выкинуть
        for stem in stems:
            found_bigger = False
            for s2 in stems:
                if len(s2)>len(stem) and s2.find(stem):
                    found_bigger = True
                    break
            if not found_bigger:
                part_len = len(stem)
                s = u'~'+stem+u'~'
                freq = wordpart2freq[s]
                score = part_len * freq
                sum_num += w2v[s] * score
                sum_denom += score
                print( 'stem       =', stem, '\tfreq=', freq, '\tscore=', score )

        # итоговый средний вектор
        v = sum_num/sum_denom
        
        # ищем ближайшие к этому вектору слова
        simx = [ (z,v_cosine(w2v[z],v)) for z in w2v.vocab if not u'~' in z ]
        for p in sorted(simx, key=lambda z: z[1], reverse=True )[0:10]:
            print( p[0], '==>', p[1] )


        # Средний вектор по всему лексикону с весом похожести слова
        print( '\n--- AVERAGE VECTOR WEIGHTED BY CHAR SIMILARITY ---' )

        sims = sorted( [ (w,similar(w,word) * math.log(word2freq[w])) for w in w2v.vocab if w in word2freq ], key=lambda z:-z[1] )[0:10]
        print( 'Top char-similar words:' )
        for (w,p) in sims:
            print( w, '==>', p )

        sum_num = np.zeros( (wordvec_len) )
        sum_denom = 0.0
        
        for (word2,sim) in sims:
            sum_num += w2v[word2]*sim
            sum_denom += sim
        
        # итоговый средний вектор
        v = sum_num/sum_denom
        
        # ищем ближайшие к этому вектору слова
        print( '\nFinal set of nearest word:' )
        simx = [ (z,v_cosine(w2v[z],v)) for z in w2v.vocab if not u'~' in z ]
        for p in sorted(simx, key=lambda z: z[1], reverse=True )[0:10]:
            print( p[0], '==>', p[1] )
        
        
        
        
