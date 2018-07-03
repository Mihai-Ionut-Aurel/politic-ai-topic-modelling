import copy

import gensim
import gensim.utils

from utility.document_streaming import *


# sys.path.append("pycharm-debug-py3k.egg")
# sys.path.append("C:\\Users\\Freakyjo\\.IntelliJIdea2017.2\\config\\plugins\\python\\helpers\\pydev\\pydevd.py")
# import pydevd
#
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)


class DocumentsPostgresCorpus(object):
    def __init__(self, dictionary=None, clip_docs=None, create_dictionary=True, metadata=True, min_word_count=100,
                 min_unique_words=50):
        super(DocumentsPostgresCorpus, self).__init__()
        self.clip_docs = clip_docs
        self.documentStreaming = PostgresStreaming()
        self.dictionary = dictionary
        self.metadata = metadata
        self.min_word_count = min_word_count
        self.min_unique_words = min_unique_words
        if dictionary is None:
            self.dictionary = gensim.corpora.Dictionary()
        self.metadata = []
        self.create_dictionary = create_dictionary
        if self.create_dictionary:
            self.dictionary.add_documents(self.get_texts())

    def __iter__(self):
        doc_id = 0
        for doc in self.documentStreaming.iter_tokenize_statements():
            # wordLists=[word for word in (arrayItem.lower().split() for arrayItem in document)]
            # texts = [word for x in wordLists for word in x if word not in self.stopwords]
                bow = self.dictionary.doc2bow(doc['text'], allow_update=self.create_dictionary)
                if self.has_min_requirements(bow):
                    if self.metadata:
                        m = copy.deepcopy(doc)
                        m['id'] = doc['metadata']['id']
                        m['corpus_seq_id'] = doc_id
                        doc_id += 1
                        yield [bow, m]
                    else:
                        yield bow

    def getstream(self):
        return self.documentStreaming.iter_tokenize_statements()

    def __len__(self):
        if not hasattr(self, 'length'):
            # cache the corpus length
            self.length = sum(1 for _ in self.get_texts())
        return self.length

    def get_texts(self, raw=False):
        """
        yield raw text or tokenized text
        """
        for j in self.documentStreaming.iter_tokenize_statements():
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
        for j in self.documentStreaming.iter_tokenize_statements():
            m = copy.deepcopy(j)
            m['id'] = j['metadata']['id']
            m['corpus_seq_id'] = doc_id
            doc_id += 1
            yield m

    def get_dictionary(self):
        return self.dictionary

    def has_min_requirements(self, doc):
        return self.__has_minimum_unique_words_than__(doc, self.min_unique_words) and self.__has_minimum_word_count__(
            doc, self.min_word_count)

    def __has_minimum_unique_words_than__(self, doc, minimun_unique_words):
        count = len([word for word in doc])
        return count >= minimun_unique_words

    def __has_minimum_word_count__(self, doc, minimun_word_count):
        count = sum(word[1] for word in doc)
        return count >= minimun_word_count
