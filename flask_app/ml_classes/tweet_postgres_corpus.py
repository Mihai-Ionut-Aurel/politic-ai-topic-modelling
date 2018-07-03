import copy

import gensim
import gensim.utils

from utility.document_streaming import *

# import sys
# sys.path.append("pycharm-debug-py3k.egg")
# sys.path.append("C:\\Users\\Freakyjo\\.IntelliJIdea2017.2\\config\\plugins\\python\\helpers\\pydev\\pydevd.py")
# import pydevd
#
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)


class TweetPostgresCorpus(object):
    def __init__(self, dictionary=None, clip_docs=None, create_dictionary=True, metadata=True):
        super(TweetPostgresCorpus, self).__init__()
        self.clip_docs = clip_docs
        self.documentStreaming = PostgresStreaming()
        self.dictionary = dictionary
        self.metadata = metadata
        if dictionary is None:
            self.dictionary = gensim.corpora.Dictionary()
        self.metadata = []
        self.create_dictionary = create_dictionary

    def __iter__(self):
        doc_id = 0
        for doc in self.documentStreaming.iter_tweets():
            bow = self.dictionary.doc2bow(doc['text'], allow_update=self.create_dictionary)
            if self.metadata:
                m = copy.deepcopy(doc)
                m['id'] = doc['metadata']['id']
                m['corpus_seq_id'] = doc_id
                doc_id += 1
                yield [bow, m]
            else:
                yield bow

    def getstream(self):
        return self.documentStreaming.iter_tweets()

    def __len__(self):
        if not hasattr(self, 'length'):
            # cache the corpus length
            self.length = sum(1 for _ in self.get_texts())
        return self.length

    def get_texts(self, raw=False):
        """
        yield raw text or tokenized text
        """
        for j in self.documentStreaming.iter_tweets():
            text = j["text"]
            if raw:
                yield text
            else:
                yield text

    def get_meta(self):
        """
        return a json object with meta data for the documents. It must return:
        id - id for this document
        optional title and tags. Tags will be used as base truth used to score document similarity results.
        """
        doc_id = 0
        for j in self.documentStreaming.iter_tweets():
            m = copy.deepcopy(j)
            m['id'] = j['metadata']['id']
            m['corpus_seq_id'] = doc_id
            doc_id += 1
            yield m

    def get_dictionary(self):
        return self.dictionary
