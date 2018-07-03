import logging

from gensim import utils
from gensim.corpora import MmCorpus
from six.moves import xrange, zip as izip

logger = logging.getLogger(__name__)


class MmCorpusMeta(MmCorpus):
    def __init__(self, fname, id2word=None, metadata=True):
        self.metadata = metadata
        MmCorpus.__init__(self, fname=fname)
        self.doc_metadata = {}
        self.metadata = metadata
        if not id2word:
            # build a list of all word types in the corpus (distinct words)
            logger.info("extracting vocabulary from the corpus")
            all_terms = set()
            self.use_wordids = False  # return documents as (word, wordCount) 2-tuples
            for doc in self:
                all_terms.update(word for word, wordCnt in doc)
            all_terms = sorted(all_terms)  # sort the list of all words; rank in that list = word's integer id
            # build a mapping of word id(int) -> word (string)
            self.id2word = dict(izip(xrange(len(all_terms)), all_terms))
        else:
            logger.info("using provided word mapping (%i ids)", len(id2word))
            self.id2word = id2word
        if metadata:
            self.doc_with_meta(fname)
        self.doc_id_to_postgres_id = {}
        self.postgres_id_to_doc_id = {}
        self.__build_relation_dictionaries()

    def __iter__(self):
        for doc_id, doc in super(MmCorpus, self).__iter__():
            yield doc  # get rid of doc id, return the sparse vector only

    def iter_meta(self):
        for key, meta in self.doc_metadata.items():
            yield key, meta

    def iter_doc(self):
        for doc_id, doc in super(MmCorpus, self).__iter__():
            yield doc_id, doc  # get rid of doc id, return the sparse vector only

    def doc_with_meta(self, fname):
        self.doc_metadata = utils.unpickle(fname + '.metadata.cpickle')

    def filter(self, doc_ids):

        self.index = [doc for id, doc in self.iter_doc() if id in doc_ids]
        self.doc_metadata = {key: metadata for key, metadata in self.iter_meta() if key in doc_ids}

    def __build_relation_dictionaries(self):
        for key, metadata in self.iter_meta():
            self.postgres_id_to_doc_id[metadata['id']] = key
            self.doc_id_to_postgres_id[key] = metadata['id']
