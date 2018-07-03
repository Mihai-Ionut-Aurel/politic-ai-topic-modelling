import json
import re

import gensim.utils

from utility.postgres_manager import *


# import sys
# sys.path.append("pycharm-debug-py3k.egg")
# sys.path.append("C:\\Users\\Freakyjo\\.IntelliJIdea2017.2\\config\\plugins\\python\\helpers\\pydev\\pydevd.py")
# import pydevd
#
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)


class PostgresStreaming:
    def __init__(self):
        self.postgresManager = PostgresManager()
        self.objectsPerQuery = 100
        with open('utility/files/stopwords.json') as f:
            self.stopwords = json.load(f)

    def iter_tokenize_statements(self):
        print(self.objectsPerQuery)
        statements_tokenized = 0
        for doc in self.iter_statements():
            if statements_tokenized % 100 == 0:
                print("Tokenized {0} statements".format(statements_tokenized))
            doc['text'] = self.__tokenize(doc['text'])
            yield doc
            statements_tokenized += 1

    def iter_statements(self):
        extracted = 0
        subjects = self.__select_subjects(extracted)
        while subjects:
            # if extracted % 900 == 0:
            #     print("Extract {0} subjects with statements, subjects: {1}".format(extracted, len(subjects)))
            #     print("Subject ID {0}".format(subjects[20]))
            #     print("Subject ID {0}".format
            for subject in subjects:
                subject_medata = {"id": subject[0]}
                statements = self.__select_statements(subject)
                if statements:
                    text = [statement[2] for statement in statements]
                    text.append(subject[1])
                    yield {"metadata": subject_medata, "text": self.__process_document(text)}
            extracted += self.objectsPerQuery
            subjects = self.__select_subjects(extracted)

    def __process_document(self, statements_list):
        content = u'\n\n'.join(statements_list[0:])
        return content

    def __select_statements(self, subject):
        statements = self.postgresManager.select_with_args(
            "SELECT id,subject_id,text FROM politicalai_ict.statement Where subject_id= %s ORDER BY id ;",
            (subject[0],))

        return statements

    def __select_subjects(self, start):
        # SELECT docs.id, docs.name FROM politicalai_ict.subject docs
        #     LEFT JOIN politicalai_ict.vote votes
        #     on docs.id = votes.subject_id
        #     Where votes.subject_id is null
        #     ORDER BY subject_id ASC;
        # Select only subjects that aren't votes
        subjects = self.postgresManager.select(
            "SELECT docs.id, docs.name FROM politicalai_ict.subject docs LEFT JOIN politicalai_ict.vote votes ON docs.id = votes.subject_id"
            "  Where votes.subject_id is null ORDER BY id ASC  LIMIT {0} OFFSET {1};".format(
                self.objectsPerQuery,
                start))
        return subjects

    def __tokenize(self, document):
        tokens = list(gensim.utils.tokenize(document, lower=True))
        tokens = [token for token in tokens if token not in self.stopwords]
        return tokens
        # wordLists = [word for word in (arrayItem.lower().split() for arrayItem in document)]
        # wordLists = [word for word in document.lower().split()]
        # texts = [word for x in wordLists for word in x if word not in self.stopwords]
        # # remove words that appear only once
        # frequency = defaultdict(int)
        # for token in texts:
        #     frequency[token] += 1
        # texts = [token for token in texts if frequency[token] > 1]
        # return texts

    def __select_tweets(self, start):
        tweets = self.postgresManager.select(
            "SELECT id,tweet,tweet_id,datetime FROM politicalai_ict.tweets "
            "ORDER BY id ASC  LIMIT {0} OFFSET {1};".format(
                self.objectsPerQuery,
                start))
        return tweets

    def iter_tweets(self):
        extracted = 0
        tweets = self.__select_tweets(extracted)
        while tweets:
            for tweet in tweets:
                tweet_medata = {"id": tweet[0]}
                text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', tweet[1])
                tweet_medata['tweet_id'] = tweet[2]
                tweet_medata['date_time'] = tweet[3]
                yield {"metadata": tweet_medata, "text": self.__tokenize(text)}
            extracted += self.objectsPerQuery
            tweets = self.__select_tweets(extracted)
