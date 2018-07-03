import os

from flask import Flask, request, jsonify

from utility.documents_gensim import *
from utility.s3_files_download import *
import logging
application = Flask(__name__)

# app.wsgi_app = ProxyFix(app.wsgi_app)

# set config
app_settings = os.getenv('APP_SETTINGS')
application.config.from_object(app_settings)

# import sys
#
# sys.path.append("pycharm-debug-py3k.egg")
# sys.path.append("C:\\Users\\Freakyjo\\.IntelliJIdea2017.2\\config\\plugins\\python\\helpers\\pydev\\pydevd.py")
# import pydevd
#
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

download_s3_bucket_contents('./')

corpus_path = "./gensim_data/updated_subjects/politic-ai-corpus.mm"
trained_path = "./gensim_data/updated_subjects/trained/politic-ai-trained.tr"
similarDocumentsHelper = SimilarDocumentsHelper(dictionary_path=corpus_path + ".dict",
                                                corpus_path=corpus_path,
                                                tfidf_path=trained_path + ".tfidf",
                                                corpus_tfidf_path=trained_path + ".tfidf.corpus",
                                                tfidf_index_sim_path=trained_path + "tfidf.corpus.index",
                                                lsi_path=trained_path + ".lsi",
                                                lsi_index_path=trained_path + ".lsi.index",
                                                stopwords_path='./utility/files/stopwords.json',
                                                tweet_corpus_path="./gensim_data/updated_subjects/twitter/twitter-corpus.mm")


@application.route('/')
def index():
    return 'Index Page'


@application.route('/hello')
def hello():
    return 'Hello, World'


@application.route('/subjects/similar/')
def similar_subjects_to_query():
    query = request.args.get("query")
    threshold = float(request.args.get('threshold'))
    return jsonify(similarDocumentsHelper.get_subjects_similar_query(query, threshold))


@application.route('/tweets/subject/')
def similar_tweets_to_subject_id():
    sub_id = int(request.args.get("subject_id"))
    threshold = float(request.args.get('threshold'))
    count = int(request.args.get("count"))
    return jsonify(similarDocumentsHelper.get_similar_tweets(sub_id, threshold)[0:count])


# return top 20 most similar subjects to query

# @app.route('/search/<string:query>', methods=['GET'])
# def return_similar_subjects(query):
#     # vectorize the text into bag-of-words and tfidf
#
#     query_bow = documentClassifiers.dictionary.doc2bow(DocumentClassifiers.tokenize(query))
#     query_tfidf = documentClassifiers.tfidf_model[query_bow]
#     query_lsi = documentClassifiers.lsi_model[query_tfidf]
#     sims = sorted(enumerate(sims), key=lambda item: -item[1])
#
#     return 'User %s' % query
#
# #return top 10 similar words to given word
# @app.route('/similar/words/<string:word>', methods=['GET'])
# def return_similar_subjects(word):
#
#     return documentClassifiers.word2vec_model.similar_by_word(word, topn=10)
print("Before main {0}".format(__name__))

if __name__ == "__main__":
    # Only for debugging while developing
    logging.info("Listening to {0}:{1}".format(application.config['SERVER_HOST'],application.config['SERVER_PORT']))
    print("Listening to {0}:{1}".format(application.config['SERVER_HOST'],application.config['SERVER_PORT']))
    application.run(host=application.config['SERVER_HOST'], debug=application.config['DEBUG'],
                    port=application.config['SERVER_PORT'])
