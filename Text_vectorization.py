import gensim
from gensim.models import word2vec
import pandas as pd
import nltk
import numpy as np
## Load the word2vec model

word_vec = word2vec.Word2Vec.load('./models/Trained_model_Full_v2_win5_dim300')
df_score= pd.read_csv('./models/Tf_idf_score.csv')
df_score.set_index('words', inplace=True)
print('Vocabulary len:' +str(len(word_vec.wv.vocab.keys())))
word_vec.most_similar('risk|clev', topn=5)
#text tokenizing
def w2v_tokenize_text(text):
    tokens = []
    for sent in nltk.sent_tokenize(text, language='english'):
        for word in nltk.word_tokenize(sent, language='english'):
            if len(word) < 2:
                continue
            tokens.append(word)
    return tokens
def word_weighting_averaging(words, weights):
    all_words, mean = set(), []
    
    for word in words:
        if isinstance(word, np.ndarray):
            mean.append(word)
        elif word in word_vec.wv.vocab:
            word1 = word.split('|')
            try:
                mean.append(weights[word1[0]]* word_vec.wv.syn0norm[word_vec.wv.vocab[word].index])  
                print(word)
                all_words.add(word_vec.wv.vocab[word].index)
            except:
                if word in word_vec.wv.vocab:
                    mean.append(word_vec.wv.syn0norm[word_vec.wv.vocab[word].index])
                    all_words.add(word_vec.wv.vocab[word].index)

    if not mean:
        print ("cannot compute similarity with no input")
        # FIXME: remove these examples in pre-processing
        return np.zeros(300,)

    #mean = gensim.matutils.unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
    mean = gensim.matutils.unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
    return mean

def  word_averaging_wei_list(text_list, df_score):
    return np.vstack([word_weighting_averaging(review,df_score) for review in text_list])

def text_vector(df_test):
    test_tokenized = []
    testlabels= []
    for i in range(df_test.shape[0]):
        newContent = df_test.iloc[i]['MOD_SNIPPET'].lower()
        test_tokenized.append(w2v_tokenize_text(newContent))
    X_test_word_average = word_averaging_wei_list(test_tokenized, df_score)
    return X_test_word_average
