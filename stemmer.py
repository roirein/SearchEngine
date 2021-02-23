from nltk.stem import porter


class Stemmer:
    def __init__(self):
        self.stemmer = porter.PorterStemmer()

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        return self.stemmer.stem(token)
