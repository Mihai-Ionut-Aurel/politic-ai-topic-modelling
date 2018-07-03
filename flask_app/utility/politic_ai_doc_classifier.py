import numpy as np
from gensim.models import KeyedVectors
from gensim.models import LsiModel
from gensim.models import TfidfModel
from gensim.similarities import MatrixSimilarity
from sklearn.cluster import SpectralClustering
from sklearn.metrics.pairwise import cosine_similarity

from ml_classes import *


class DocumentClassifier:
    def __init__(self, dictionary_path, corpus_path, pretrained_vec_path, gensim_pretrained_path=None):

        self.dictionary = gensim.corpora.Dictionary.load(dictionary_path)
        self.n_clusters = 100
        self.n_topics = 500
        self.corpus = MmCorpusMeta(corpus_path, id2word=self.dictionary)
        self.word2vec_model = KeyedVectors.load(pretrained_vec_path)
        self.postgresManager = PostgresManager()
        if gensim_pretrained_path:
            self.load_train_data(gensim_pretrained_path)
        else:
            self.tfidf_model = None
            self.lsi_model = None
            self.sim_matrix = None

    def filter_docs(corpus, condition_on_doc):
        """
        Filter corpus, texts and labels given the function condition_on_doc which takes
        a doc.
        The document doc is kept if condition_on_doc(doc) is true.
        """
        number_of_docs = len(corpus)
        corpus = [doc for doc in corpus if condition_on_doc(doc)]
        print("{} docs removed".format(number_of_docs - len(corpus)))
        return corpus

    def has_vector_representation(word2vec_model, doc, dict):
        """check if at least one word of the document is in the
        word2vec dictionary"""

        return not all(dict[word[0]] not in word2vec_model.vocab for word in doc)

    def document_vector(word2vec_model, doc, dict):
        # remove out-of-vocabulary words
        doc = [dict[word[0]] for word in doc if dict[word[0]] in word2vec_model.vocab]
        return np.mean(word2vec_model[doc], axis=0)

    def most_similar(i, X_sims, topn=None):
        """return the indices of the topn most similar documents with document i
        given the similarity matrix X_sims"""

        r = np.argsort(X_sims[i])[::-1]
        if r is None:
            return r
        else:
            return r[:topn]

    def spectral_clustering(n_clusters, sims_matrix, method):
        n_clusters = n_clusters
        sc = SpectralClustering(n_clusters=n_clusters,
                                affinity='precomputed')
        matrix = sims_matrix['politicai'][method]

        sc.fit(matrix)
        print("Method: {}".format(method))
        print(sc.labels_[1::10])
        print("-" * 10)
        return sc

    def train(self):
        tfidf = TfidfModel(self.corpus, id2word=self.dictionary)
        corpus_tfidf = tfidf[self.corpus]
        index = gensim.similarities.MatrixSimilarity(tfidf[self.orpus])
        sims = index[corpus_tfidf]
        sims = {'politicai': {}}
        lsi = LsiModel(corpus_tfidf, id2word=self.dictionary, num_topics=self.n_topics)
        lsi_index = MatrixSimilarity(lsi[corpus_tfidf])
        sims['politicai']['LSI'] = np.array([lsi_index[lsi[corpus_tfidf[i]]]
                                             for i in range(len(self.corpus))])
        sims['politicai']['centroid'] = cosine_similarity(
            np.array([self.document_vector(self.word2vec_model, doc, self.dictionary)
                      for doc in self.corpus]))
        sc_lsi = self.spectral_clustering(n_clusters=self.n_clusters, sims_matrix=sims, method="LSI")
        sc_word2vec = self.spectral_clustering(n_clusters=self.n_clusters, sims_matrix=sims, method="centroid")

    def save_train_data(self, path, tfidf_model, sims, lsi):
        tfidf_model.save(path + '.tfidf')
        lsi.save(path + '.lsi')
        utils.pickle(sims, path + '.sims')

    def load_train_data(self, path):
        self.tfidf_model = TfidfModel.load(path + '.tfidf')
        self.lsi_model = LsiModel.load(path + '.lsi')
        self.sim_matrix = utils.unpickle(path + '.sims')

    def generate_categories(self, sc_lsi, sc):
        subject_dict = []
        for _, meta in self.corpus.doc_metadata.items():
            s_dict = {}
            s_dict['sub_id'] = meta['metadata']['id']
            s_dict['doc_id'] = meta['id']
            s_dict['seq_id'] = meta['corpus_seq_id']
            cluster = {}
            cluster['lsi'] = sc_lsi.labels_[meta['corpus_seq_id']]
            cluster['word2vec'] = sc.labels_[meta['corpus_seq_id']]
            s_dict['spec_clust'] = cluster
            subject_dict.append(s_dict)

    def aggregate_categories_cluster(self, subject_dict, sc, algorithm):
        cluster_docs = {
            label: {'documents': []} for label in sc.labels_
        }
        for meta in subject_dict:
            label = meta['spec_clust']['algorithm']
            doc_dic = {'doc_id': meta['doc_id'], 'sub_id': meta['sub_id'],
                       'doc_uniq_words': len(self.corpus[meta['seq_id']]),
                       'seq_id': meta['seq_id']}
            cluster_docs[label]['documents'].append(doc_dic)

        for label, cluster in cluster_docs.items():
            max_uniq_words_sub_id = max(cluster['documents'], key=lambda x: x['doc_uniq_words'])
            subject = self.postgresManager.select(
                "Select * FROM politicalai_ict.subject where id = {0};".format(max_uniq_words_sub_id['sub_id']))
            self.postgresManager.commit_changes()
            cluster_docs[label]['title'] = subject[0][1]

    def insert_new_dossiers(self, cluster_docs, method):
        for label, cluster in cluster_docs.items():
            self.postgresManager.insert_with_args(
                "insert into politicalai_ict.dossier(id,name,description,onlineid,ml_algorithm,clustering_algorithm)"
                " values(DEFAULT ,%s,NULL,NULL,%s,%s) RETURNING id",
                (cluster['title'], method, 'spectral-clustering'))
        self.postgresManager.commit_changes()
        cluster_id = self.postgresManager.cursor.fetchone()[0]
        cluster['database_cluster_id'] = cluster_id
        for doc in cluster['documents']:
            self.postgresManager.insert_with_args(
                "insert into politicalai_ict.subject_to_dossier(rel_id,subject_id,dossier_id,ml_algorithm,clustering_algorithm)"
                " values(DEFAULT ,%s,%s,%s,%s) RETURNING rel_id",
                (doc['sub_id'], cluster_id, method, 'spectral-clustering'))
            self.postgresManager.commit_changes()
            try:
                rel_id = self.postgresManager.cursor.fetchone()[0]
                doc['database_rel_id'] = rel_id
            except psycopg2.ProgrammingError:
                # take some other action
                print("Error inserting doc {0} from topic {1}".format(doc['sub_id'], label))

    # TODO: improve tokenizer
    def tokenize(self, text):
        tokens = list(gensim.utils.tokenize(text, lower=True))
        return tokens

    def contains_word_w2v(self, word):
        return word in self.word2vec_model.vocab

    def contains_word_dict(self, word):
        return word in self.dictionary.values()
