import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import time
from gensim.models import Word2Vec, KeyedVectors

# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._indexer.flag = "word2vec"
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        unique_doc = {}
        for doc in documents_list:
            if (doc[2], doc[8]) in unique_doc:
                continue
            else:
                unique_doc[(doc[2], doc[8])] = doc
        document_list = list(unique_doc.values())
        number_of_documents = 0
        for idx, document in enumerate(document_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        self._indexer.calculate_weigths()
        self._indexer.optimize()
        self._indexer.save_index("word2vec.pkl")
        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):

        inverted_idx = self._indexer.load_index(fn)
        self._indexer.docs_index = inverted_idx[2]
        self._indexer.postingDict = inverted_idx[1]
        self._indexer.inverted_idx = inverted_idx[0]

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        self._model = KeyedVectors.load_word2vec_format(model_dir+"/word2vec_model.model",binary=True, unicode_errors='ignore')
        self._indexer.calculate_average_vector(self._model)
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model,Search_method="word2vec")
        return searcher.search(query)

def main():
    search_engine = SearchEngine()
    search_engine.build_index_from_parquet("data_set/data/benchmark_data_train.snappy.parquet")
    search_engine.load_index("word2vec.pkl")
    search_engine.load_precomputed_model("model")
    print("start searching")
    start = time.time()
    print(search_engine.search("Bill Gates owns the patent and vaccine for coronavirus"))
    print(time.time()-start)

