class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'do-i-really-need-this'
    FLASK_HTPASSWD_PATH = '/secret/.htpasswd'
    FLASK_SECRET = SECRET_KEY
    DB_HOST = 'database'  # a docker link
    GENSIM_DICTIONARY_PATH = ''
    GENSIM_CORPUS_PATH = ''
    PRETRAINED_VEC_PATH = ''
    GENSIM_DATA_PRETRAINED_PATH = ''
    DB_HOSTNAME = 'uni-frank.camb6ystrb7z.eu-central-1.rds.amazonaws.com'
    DB_PORT = 5432
    DB_USERNAME = 'politicai'
    DB_PASSWORD = 'KdzR7Z^h9YbW&yk9$nCGatG#2eQ$NH'
    DB_DATABASE = 'university'
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = '5780'


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    SECRET_KEY = 'do-i-really-need-this'
    FLASK_HTPASSWD_PATH = '/secret/.htpasswd'
    FLASK_SECRET = SECRET_KEY
    DB_HOST = 'database'  # a docker link
    GENSIM_DICTIONARY_PATH = ''
    GENSIM_CORPUS_PATH = ''
    PRETRAINED_VEC_PATH = ''
    GENSIM_DATA_PRETRAINED_PATH = ''
    DB_HOSTNAME = ''
    DB_PORT = ''
    DB_USERNAME = ''
    DB_PASSWORD = ''
