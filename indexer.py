import pickle
import math
import numpy as np
from nltk.corpus import wordnet
# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.docs_index = {}
        self.config = config
        self.flag = ""


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        maximum = 0
        if len(document_dictionary) > 0:
            maximum = max(document_dictionary.values())
        self.docs_index[int(document.tweet_id)] = [maximum,len(document_dictionary),document.tokenized_text,0]
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                 try:
                     tf = document_dictionary[term]
                 except:
                     tf = 0
                 if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = [1, document_dictionary[term]]
                    self.postingDict[term] = [[int(document.tweet_id),document_dictionary[term]]]#{int(document.tweet_id):[
                 else:
                    self.inverted_idx[term][0] += 1
                    self.inverted_idx[term][1] += document_dictionary[term]
                    self.postingDict[term].append([int(document.tweet_id),document_dictionary[term]])

                #self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

            except:
                print(term)
                print('problem with the following key {}'.format(term[0]))

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        f = open(fn, "rb")
        lst = pickle.load(f)
        return lst


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """

        new_docs = {}
        for doc in self.docs_index:
            new_docs[doc] = self.docs_index[doc][:4]
        f = open(fn, "wb")
        pickle.dump([self.inverted_idx,self.postingDict,new_docs],f)

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []



    def optimize(self):
        """
        remove from the inverted index too rare words
        :return:
        """
        new_dict = {}
        for key in self.inverted_idx:
            if self.inverted_idx[key][1] > 10 and self.inverted_idx[key][0] > 10:
                new_dict[key] = self.inverted_idx[key]
        self.inverted_idx = new_dict

    def calculate_weigths(self):
        """
        calculate the weight of terms in senntence according to BM-25""
        :return:
        """
        sum_len = 0
        for i in self.docs_index:
            sum_len += len(self.docs_index[i][2])
        avg = sum_len/len(self.docs_index)
        k = 1.2
        b = 0.1
        for term in self.inverted_idx:
            idf = math.log(len(self.docs_index) / self.inverted_idx[term][0], 2)
            for doc in self.postingDict[term]:
                doc_len = len(self.docs_index[doc[0]][2])
                norm = 1 - b + b*(doc_len/avg)
                w = idf * (((k+1)*doc[1])/(k*norm+doc[1]))
                doc.append(w)
                self.docs_index[doc[0]][3] += (w**2)


    def calculate_average_vector(self,model):
        """
        caclculating the average vector of each doc using word2vec model
        :param model:
        :return:
        """
        for doc in self.docs_index:
            vec = []
            for term in self.docs_index[doc][2]:
                try:
                   vec.append(model.wv[term])
                except:
                    continue
            if len(vec) == 0:
                vec = []
            vec = np.add.reduce(vec)
            vec /= len(self.docs_index[doc][2])
            self.docs_index[doc][2] = vec


    def get_syns(self):
        """
        get the synonyms of each word using wordnet model
        :return:
        """
        for doc in self.docs_index:
            syns = []
            text = self.docs_index[doc][2]
            for word in text:
                w = wordnet.synsets(word)
                if len(w) > 0:
                    syns.append(wordnet.synsets(word)[0])
            self.docs_index[doc].append(syns)
