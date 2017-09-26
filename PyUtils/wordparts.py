# -*- coding: utf-8 -*-
'''
Генерация word2vector моделей для слов и частей слов.
Используется возможность gensim брать текст из генератора.
'''

from __future__ import print_function
from gensim.models import word2vec
import logging
import os
import random
from collections import Counter


# ----------------------------------------------------------------------------

# Будем генерировать корпус с частями слов на лету, читая по одному предложению
# из исходного корпуса. Для каждого исходного предложения создается несколько
# новых предложений, включая исходный вариант.
class WordPartsGenerator:
    '''
    fname - имя файла с исходным корпусом
    max_per_line - макс. число предложений с частями слов, генерируемых из одного исходного
    '''
    def __init__(self, fname, max_per_line, min_part_len, max_part_len, max_lines ):
        self.fname = fname
        self.max_per_line = max_per_line
        self.min_part_len = min_part_len
        self.max_part_len = max_part_len
        self.max_lines = max_lines
        self.line_buf = []
        self.ibuf= 0
        self.rdr = None
        self.total_lines = 0
        
    def fill_buffer(self):
        self.line_buf = []
        self.ibuf = 0

        line = self.rdr.readline().decode('utf-8').strip()
        if line==None:
            return

        n_generated=0
        nprobe=0
        words = line.split(' ')
        
        self.line_buf.append( words ) # исходное предложение добавляется обязательно
        self.total_lines += 1
        
        if len(words)>2:
            while n_generated<self.max_per_line and nprobe<100:
                nprobe += 1
                # выбираем слово для получения частей
                iword = random.randint(0,len(words)-1)
                word = words[iword]
                wlen = len(word)
                if wlen>self.max_part_len and not '_' in word:
                    pos0 = random.randint(0,wlen-self.min_part_len-1)
                    maxpos1 = min( wlen-1, pos0+self.max_part_len-1 )
                    pos1 = random.randint(pos0+self.min_part_len,maxpos1)
                    
                    word2 = u''
                    if pos0>0:
                        word2 += u'~'
                        
                    word2 += word[pos0:pos1+1]
                    
                    if pos1<wlen-1:
                        word2 += u'~'
                        
                    line2 = words[:iword] + [word2] + words[iword+1:]
                    #str2 = str.join( ' ', line2 )
                    #self.line_buf.append( str2 )
                    self.line_buf.append( line2 )
                    n_generated += 1
                    self.total_lines += 1

    def __iter__(self):
        self.line_buf = []
        self.ibuf= 0
        self.total_lines = 0
        if self.rdr!=None:
            self.rdr.close()

        self.rdr = open( self.fname, 'r' )
        return self;

    def next(self):
        if self.ibuf==len(self.line_buf):
            self.fill_buffer()
            if len(self.line_buf)==0 or self.total_lines>self.max_lines:
                raise StopIteration

        line = self.line_buf[self.ibuf]
        self.ibuf += 1
        return line

# ----------------------------------------------------------------------------

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# путь к файлу с исходным текстовым корпусом.
# файл содержит одно предложение в каждой строке. слова приведены к нижнему регистру,
# пунктуаторы убраны, токены разделены пробелами.
corpus_path =  os.path.expanduser('~/Corpus/word2vector/ru/SENTx.corpus.w2v.txt')

# параметры w2v модели
SIZE=32
WINDOW=1
CBOW=0
MIN_COUNT=2

# минимальная длина фрагмента слова
MIN_PART_LEN = 2

# максимальная длина фрагмента слова
MAX_PART_LEN = 4

# сколько вариантов замен получается из одного предложения
N_NEWLINE_PER_SENTENCE = 10


# подсчитаем, сколько строк в исходном корпусе, чтобы потом
# давать оценку завершенности генерации корпуса.
print( 'Counting lines in source corpus', corpus_path, '...' )
nline=0
for line in open(corpus_path,'r'):
    nline += 1
print( 'Done, ', nline, ' lines.' )

max_lines = nline*N_NEWLINE_PER_SENTENCE


# Соберем частотный словарь для слов и частей слов.
print( 'Collecting the wordpart frequencies...' )
wordpart_counts = Counter()
word_counts = Counter()
corp = WordPartsGenerator(corpus_path,N_NEWLINE_PER_SENTENCE,MIN_PART_LEN,MAX_PART_LEN,max_lines)
nline=0
for line in corp:
    for word in line:
        if u'~' in word:
            wordpart_counts[word] += 1
        else:
            word_counts[word] += 1    

    nline += 1
    if 0 == (nline % 10000):
        print( '{0}/{1} ==> {2}%'.format(nline,max_lines,100.0*n_line/max_lines), end='\r' )

print( 'done, {0} lines processed. {1} unique words, {2} unique word parts'.format(nline,len(word_counts),len(wordpart_counts) ) )

WORDPART_FREQUENCIES_FILENAME = 'wordpart.frequencies.dat'
with open( WORDPART_FREQUENCIES_FILENAME, 'w' ) as f:
    for d in wordpart_counts.iteritems():
        f.write( d[0].encode('utf-8') + '\t' + str(d[1]) + '\n' )

WORD_FREQUENCIES_FILENAME = 'word.frequencies.dat'
with open( WORD_FREQUENCIES_FILENAME, 'w' ) as f:
    for d in word_counts.iteritems():
        f.write( d[0].encode('utf-8') + '\t' + str(d[1]) + '\n' )


filename = 'wordparts.CBOW=' + str(CBOW)+'_WIN=' + str(WINDOW) + '_DIM='+str(SIZE)

# в отдельный текстовый файл выведем все параметры модели
with open( filename + '.info', 'w+') as info_file:
    print('corpus_path=', corpus_path, file=info_file)
    print('SIZE=', SIZE, file=info_file)
    print('WINDOW=', WINDOW, file=info_file)
    print('CBOW=', CBOW, file=info_file)
    print('MIN_COUNT=', MIN_COUNT, file=info_file)

# начинаем обучение w2v на генерируемом корпусе
sentences = WordPartsGenerator(corpus_path,N_NEWLINE_PER_SENTENCE,MIN_PART_LEN,MAX_PART_LEN,max_lines)
model = word2vec.Word2Vec(sentences, size=SIZE, window=WINDOW, cbow_mean=CBOW, min_count=MIN_COUNT, workers=4, sorted_vocab=1, iter=1 )

model.init_sims(replace=True)

# сохраняем готовую w2v модель
model.save_word2vec_format( filename + '.model', binary=True)

