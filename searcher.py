import time
from ranker import Ranker
from nltk.corpus import wordnet
from spellchecker import SpellChecker
import numpy as np
from stemmer import Stemmer

# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None, Search_method=None):
        self._parser = parser
        self._indexer = indexer
        self._indexer.flag = 'word2vec'
        self._ranker = Ranker()
        self._model = model
        self.Search_method = Search_method

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """

        query_as_list = self._parser.parse_sentence(query)
        if self.Search_method == "spellchecker":
            spell = SpellChecker()
            misspelled = spell.unknown(query_as_list)
            for i in range(len(query_as_list)):
                if query_as_list[i] in misspelled:
                    query_as_list[i] = spell.correction(query_as_list[i])
        if self.Search_method == 'word2vec':
            query_as_list = self.extend_query(query_as_list)
        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        if self.Search_method == 'word2vec':
            query_vec = self.query_to_vector(query_as_list)
            ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs,query=query_vec, rank='word2vec')
        elif self.Search_method == 'wordnet':
            ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs,query=query_as_list, rank='wordnet')
        elif self.Search_method == "spellchecker":
            ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs,query=query_as_list, rank='spellchecker')
        else:
            ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """

        relevant_docs = {}
        query = []
        temp_dict = {}
        ranked = {}
        if self.Search_method == "wordnet":
            doc_list = self._indexer.docs_index
            for term in query_as_list:
                w = wordnet.synsets(term)
                if len(w) > 0:
                    query.append(w[0])
                try:
                    posting_list = self._indexer.postingDict[term]
                    for doc in posting_list:
                        if doc[0] in temp_dict:
                            ranked[doc[0]][1][term] = doc[2]
                        else:
                            temp_dict[doc[0]] = doc_list[doc[0]]
                            ranked[doc[0]] = [doc_list[doc[0]], {term: doc[2]}]
                except:
                    pass
            #sorted_by_tf_idf = Ranker.rank_relevant_docs(ranked,query=query_as_list)
            #sorted_by_tf_idf = sorted_by_tf_idf[:1500]
            for doc in temp_dict:
                doc_and_query = []
                for w1 in query:
                    scores = []
                    for w2 in temp_dict[doc][4]:
                        sc = wordnet.path_similarity(w1, w2)
                        if sc is not None:
                            scores.append(sc)
                    doc_and_query.append((w1, scores))
                relevant_docs[doc] = doc_and_query
            return relevant_docs
        elif self.Search_method == "spellchecker":
            doc_list = self._indexer.docs_index
            for term in query_as_list:
                try:
                    posting_list = self._indexer.postingDict[term]
                    for doc in posting_list:
                        if doc[0] in temp_dict:
                            relevant_docs[doc[0]][1][term] = doc[2]
                        else:
                            relevant_docs[doc[0]] = [doc_list[doc[0]], {term: doc[2]}]
                except:
                    pass
            return relevant_docs
        elif self.Search_method == "word2vec":
            doc_list = self._indexer.docs_index
            for term in query_as_list:
                try:
                    posting_list = self._indexer.postingDict[term]
                    for doc in posting_list:
                        if doc[0] in temp_dict:
                            continue
                        else:
                            relevant_docs[doc[0]] = doc_list[doc[0]][2]
                except:
                    pass
            return relevant_docs

    def query_to_vector(self,query):
        """
        calcualte the average vector of query using
        word2vec model
        :param query:
        :return:
        """
        vec = []
        for term in query:
            try:
                vec.append(self._model.wv[term])
            except:
                continue
        if len(vec) == 0:
            return []
        vec = np.add.reduce(vec)
        vec /= len(query)
        return vec


    def extend_query(self,query):
        """
        expand the query according to the most similar words according
        to word2vec model
        :param query:
        :return:
        """
        expanded_terms = []
        for term in query:
            try:
                expanded_terms.append(term)
                temp = self._model.most_similar(term)
                for i in temp:
                    expanded_terms.append(i[0])
            except:
                expanded_terms.append(term)
        return expanded_terms
