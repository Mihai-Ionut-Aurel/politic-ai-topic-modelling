import gensim.utils
import numpy as np
from gensim.models import LsiModel
from gensim.models import TfidfModel
import json
from ml_classes.mm_with_meta import *

#
# sys.path.append("pycharm-debug-py3k.egg")
# sys.path.append("C:\\Users\\Freakyjo\\.IntelliJIdea2017.2\\config\\plugins\\python\\helpers\\pydev\\pydevd.py")
# import pydevd
#
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
#

class SimilarDocumentsHelper:
    def __init__(self, dictionary_path, corpus_path, tfidf_path, corpus_tfidf_path, tfidf_index_sim_path, lsi_path,
                 lsi_index_path, stopwords_path, tweet_corpus_path):

        self.dictionary = gensim.corpora.Dictionary.load(dictionary_path)
        self.corpus = MmCorpusMeta(corpus_path, id2word=self.dictionary, metadata=True)
        self.tweet_corpus = MmCorpusMeta(tweet_corpus_path, id2word=self.dictionary, metadata=True)
        self.tfidf = TfidfModel.load(tfidf_path)
        self.corpus_tfidf = gensim.utils.unpickle(corpus_tfidf_path)
        self.lsi = LsiModel.load(lsi_path)
        self.lsi_index = gensim.similarities.MatrixSimilarity.load(lsi_index_path)
        with open(stopwords_path) as f:
            self.stopwords = json.load(f)
        self.tdidf_tweets = self.tfidf[self.tweet_corpus]
        self.lsi_tweets = self.lsi[self.tdidf_tweets]
        self.sim_tweets = gensim.similarities.MatrixSimilarity(self.lsi_tweets)
        print("loaded")

    def get_subjects_similar_query(self, query, threshold):
        bow = self.dictionary.doc2bow(self.__tokenize(query))
        sims_td = self.tfidf[bow]
        sims_lsi = self.lsi_index[self.lsi[sims_td]]
        sims_lsi_sorted = sorted(enumerate(sims_lsi), key=lambda item: -item[1])
        similarityIds = {'subjects': []}
        for sim in sims_lsi_sorted:
            if sim[1] > threshold:
                key = self.corpus.doc_metadata[sim[0]]['metadata']['id']
                value = float(sim[1])
                sim_dic = {key: value}
                similarityIds['subjects'].append(sim_dic)
        return similarityIds

    def get_similar_tweets(self, sub_id, threshold):
        sub = self.corpus[self.corpus.postgres_id_to_doc_id[sub_id]]
        td_sub = self.tfidf[sub]
        ls_sub = self.lsi[td_sub]
        sim_tweets_sub = self.sim_tweets[ls_sub]
        indexes = np.argsort(sim_tweets_sub)[::-1]
        similarityIds = []
        for sim_tweet_index in indexes:
            if sim_tweets_sub[sim_tweet_index] > threshold:
                key = self.tweet_corpus.doc_metadata[sim_tweet_index]['metadata']['id']
                value = self.tweet_corpus.doc_metadata[sim_tweet_index]['metadata']
                similarityIds.append(value)
        return similarityIds

    def __tokenize(self, document):
        tokens = list(gensim.utils.tokenize(document, lower=True))
        tokens = [token for token in tokens if token not in self.stopwords]
        return tokens
