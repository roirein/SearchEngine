# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
from itertools import product
from nltk.corpus import wordnet
import time
import math
from numpy.linalg import norm
from numpy import dot
class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_docs, k=None,query=None, rank=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """

        res = relevant_docs
        if rank == "wordnet":
            res = Ranker.wordnet_rank(relevant_docs)
        elif rank == 'spellchecker':
            res = Ranker.tf_idf_rank(relevant_docs,query)
        elif rank == 'word2vec':
            res = Ranker.word2vec_rank(relevant_docs, query)
        #print(res)
        ranked_results = sorted(res.items(), key=lambda item: item[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        return [d[0] for d in ranked_results]

    @staticmethod
    def wordnet_rank(relevant_docs):
        rank_score = {}
        for doc in relevant_docs:
            score = 0
            count = 0
            for tup in relevant_docs[doc]:
                if len(tup[1]) > 0:
                    score += max(tup[1])
                    count += 1
            if count != 0:
                score /= count
            else:
                score = 0
            rank_score[doc] = score
        return rank_score

    @staticmethod
    def tf_idf_rank(relevant_docs,query):
        rank_socre = {}
        for doc in relevant_docs:
            sum = 0
            count = 0
            for i in query:
                if i in relevant_docs[doc][1]:
                    sum += relevant_docs[doc][1][i]
                    count += 1
            sum_w_squeard = relevant_docs[doc][0][3]
            rank_socre[doc] = sum/math.sqrt(sum_w_squeard*count)
        return rank_socre

    @staticmethod
    def word2vec_rank(relevant_docs,query):
        rank_score = {}
        for i in relevant_docs:
            try:
                score = dot(relevant_docs[i], query)/(norm(relevant_docs[i])*norm(query))
                if type(score) == float:
                    rank_score[i] = score
                else:
                    rank_score[i] = 0
            except:
                rank_score[i] = 0
        return rank_score
