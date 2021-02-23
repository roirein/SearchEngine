from nltk.corpus import stopwords
from document import Document
import json
import urllib.parse
from stemmer import Stemmer


class Parse:

    def __init__(self):
        stop_list = stopwords.words('english')
        stop_list.extend(["RT","I","web","status","Will","the","would","Would",'The','ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very',
     'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most',
     'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves',
     'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more',
     'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she',
     'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does',
     'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he',
     'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few',
     'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was',
     'here', 'than','we','since','coronaviru','people'
     'rt',"don't", '-', '&amp;', 'it’s', 'don’t', 'i’m', "it's", "doesn't",'t.co','im','yet','oh','hello','lol','wont','kaboooooooooooom','hahhahahahahha','hahahaaahahahahah','lollllll',"lolll","lollll","lololololol",".....http"
        "lolllllll","lolololololololol","lololololololol","lolololololol","^__^",
        "wtfffff","wtfff","wtff","howwww","howww","hahhaha","hahahahhaa","hahahahahhaha","hahhaa","hahhahahahahha","hahahha"
        ,"ohhhhhhhhh","helloooooooo","noooooooooooo","___",
        "hahahahahha","shittt","shitttt","shittt","waaaa","gtgtgtgtgtgtgtgt",'mask','coronavirus'
        "beacaus","sooooooooo","sooooooooooooooo","sooooooooooo","sooooooooo",'lol',"^^^",'wont',"bitchhhhhh",'let','hahahahahaha','corona','covid','19','2020'])
        self.stop_words = set(stop_list)
        self.redundant = set([",",":","?","!","*","&",";", "'", "\"","(",")", "|", "=","+","[","]","{","}","$","~","^"])
        self.numbers = set(["MILLION","million","mill","milli","Million","Thousand","thousand","THOUSAND","Billion","BILLION","billion"])
        self.perc = ["%","percent","percentage"]
        self.ents = {}
        self.stem = Stemmer()

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """

        final_list = []
        list_of_words = self.clean_text(text.split())
        i = 0
        plus = 1
        while i < len(list_of_words):
            if len(list_of_words[i]) < 2 and not list_of_words[i].isdigit():
                i+=1
                continue
            if not list_of_words[i].lower() in self.stop_words and list_of_words[i][0] != "@" and not list_of_words[i].startswith("https"):
                if list_of_words[i][0] == "#":
                    words = self.serpearte_hashtags(list_of_words[i])
                    for w in words:
                        if w != '' or w.lower() not in self.stop_words:
                            final_list.append(self.stem.stem_term(w.lower()))
                elif self.is_number(list_of_words[i]):
                    if i != len(list_of_words)-1 and list_of_words[i+1] in self.perc:
                        final_list.append(list_of_words[i] + "%")
                        plus=2#change to while later
                    if i != len(list_of_words)-1 and "/" in list_of_words[i+1]:
                        lst = list_of_words[i+1].split("/")
                        try:
                            float(lst[0])
                            float(lst[1])
                            final_list.append(list_of_words[i] + " " + list_of_words[i+1])
                            plus=2
                        except:
                            pass
                    if i != len(list_of_words)-1 and list_of_words[i+1] in self.numbers:
                        if list_of_words[i+1][0] == "t" or list_of_words[i+1][0] == "T":
                            final_list.append(list_of_words[i] + "K")
                        else:
                            final_list.append(list_of_words[i] + list_of_words[i+1][0].upper())
                        plus=2
                    else:
                        final_list.append(self.reduce_number(list_of_words[i]))
                elif "-" in list_of_words[i] or "/" in list_of_words[i] or "_":
                    if "/" in list_of_words[i]:
                        lst = list_of_words[i].split("/")
                    elif "-" in list_of_words[i]:
                        lst = list_of_words[i].split("-")
                    else:
                        lst = list_of_words[i].split("_")
                    for j in lst:
                        if j == '':
                            continue
                        if self.is_number(j):
                            final_list.append(self.reduce_number(j))
                        else:
                            if j.lower() not in self.stop_words:
                                final_list.append(self.stem.stem_term(j.lower()))
                elif ".." in list_of_words[i]:
                    for j in list_of_words[i]:
                        if j == ".":
                            list_of_words[i] = list_of_words[i].replace(j, " ")
                    s = list_of_words[i].split(" ")
                    for j in s:
                        if j != " " and j.lower() not in self.stop_words:
                            final_list.append(self.stem.stem_term(j.lower()))
                elif "." in list_of_words[i]:
                    words = list_of_words[i].split(".")
                    flag = True
                    for w in words:
                        if len(w) != 1:
                            flag = False
                    if flag:
                        i+=plus
                        continue
                    for w in words:
                        if w == '' or w[0] == "@":
                            continue
                        if self.is_number(w):
                            final_list.append(self.reduce_number(w))
                        else:
                            if w.lower() not in self.stop_words:
                                final_list.append(self.stem.stem_term(w.lower()))
                else:
                    if list_of_words[i].lower() not in self.stop_words:
                        final_list.append(self.stem.stem_term(list_of_words[i].lower()))
            i += plus
        final_list = list(filter(lambda a: a != '' or (len(a) != 1 and not a.isdigit()), final_list))
        return final_list


    def is_number(self,string):
        """
        check if a string is a number
        :param string:
        :return True or False:
        """
        try:
            float(string)
            return True
        except:
            return False

    def reduce_number(self,string):
        """
        recive a number as a string and formating the number according to itws size(1000,1000000...)
        :param string:
        :return:
        """
        number = float(string)
        if (number < 1000):
            return f'{number:g}'
        else:
            end = ""
            if 1000 <= number < 1000000:
                number = number / 1000
                end = "K"
            if 1000000 <= number < 1000000000:
                number = number / 1000000
                end = "M"
            if number >= 1000000000:
                number = number / 1000000000
                end = "B"
            number = '%.3f'%number
            number = str(number).rstrip('0').rstrip('.')
            number = number + end
            return number





    def serpearte_hashtags(self, hashtag):
        """
        recive a hashtag and return the hashtag seperated to its word
        :param hashtag:
        :return:
        """
        hashtag = hashtag[1:]
        if "_" in hashtag or "-" in hashtag:
            return hashtag.split('_')
        else:
            words = []
            word = ""
            if hashtag[0].isupper():
                flag = 'U'
            elif hashtag[0].isupper():
                flag = 'L'
            else:
                flag = "N"
            for i in hashtag:
                if i.isupper() and flag == 'U':
                    word += i
                elif (i.islower() or i.isdigit()) and flag == 'U':
                    if len(word) == 1:
                        word += i
                    else:
                        words.append(word)
                        word = i
                    if i.isdigit():
                        flag = "N"
                    else:
                        flag = "L"
                elif i.islower() and flag == 'L':
                    word += i
                elif (i.isupper() or i.isdigit()) and flag == 'L':
                    words.append(word)
                    word = i
                    if i.isdigit():
                        flag = "N"
                    else:
                        flag = "U"
                elif i.isdigit() and flag != "N":
                    words.append(word)
                    word = i
                    flag = "N"
                elif i.isdigit() and flag == "N":
                    word += i
                elif (i.islower() or i.isupper()) and flag == "N":
                    words.append(word)
                    word = i
                    if i.isupper():
                        flag = "U"
                    else:
                        flag = "L"
            words.append(word)
            if len(words) == 1:
                return words
            for i in words:
                if i.isupper():
                    if len(i) == 2 and words.index(i) < len(words) - 1:
                        if words[words.index(i) + 1].islower():
                            words[words.index(i) + 1] = i[1] + words[words.index(i) + 1]
                            words[words.index(i)] = i[0]
                        else:
                            words.insert(words.index(i) + 1, i[1])
                            words[words.index(i)] = i[0]
            if words[0] == '':
                words = words[1:]
            return words

    def clean_text(self, list_of_words):
        """
        remove from the text any char which is not ascii or in redundant char
        :param list_of_words:
        :return:
        """
        for i in range(len(list_of_words)):
            for j in list_of_words[i]:
                if not j.isdigit() or not j.isalpha():
                    if j in self.redundant or ord(j) > 127:
                        list_of_words[i] = list_of_words[i].replace(j,'')
            while list_of_words[i].endswith("."):
                list_of_words[i] = list_of_words[i][:-1]
        return list_of_words

    def parse_url(self,url,tweet_id):
            """
            recive url and parse its path domain
            :param url:
            :param tweet_id:
            :return:
            """
            urls = ""
            try:
                url = json.loads(url)
            except:
                pass
            tokenized_url = []
            for ur in url:
                curr = ""
                if url[ur] != None:
                    curr = url[ur]
                else:
                    curr = ur
                lst = urllib.parse.urlsplit(curr)
                path = lst.path.split("/")
                new_list = []
                for i in path:
                    if "-" in i:
                        new_list += i.split("-")
                    elif i.isdigit() or i.isalpha():
                        new_list.append(i)
                for i in new_list:
                    if i not in self.stop_words:
                         if i.isalpha():
                            if len(i) != 1 and i.lower() not in self.stop_words:
                                tokenized_url.append(self.stem.stem_term(i.lower()))
            return tokenized_url

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text)
        if url != "{}":
            tokenized_text += self.parse_url(url,tweet_id)
        if quote_text is not None:
            tokenized_text += self.parse_sentence(quote_text)
        if quote_url is not None:
            tokenized_text += self.parse_url(quote_url,tweet_id)
        doc_length = len(tokenized_text)  # after text operations.
        new_tokenized_text = []
        for i in tokenized_text:
            if len(i) > 1 and len(i) < 20 and i not in self.stop_words:
                new_tokenized_text.append(i)
        tokenized_text = new_tokenized_text
        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length,tokenized_text)
        return document
