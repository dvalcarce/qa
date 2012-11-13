# -*- coding: utf-8 -*-

import nltk
import pickle
import pprint
import sys
import ConfigParser
from MyConfig import MyConfig
from Document import Document
from pattern.web import Google, Bing
#from Google import Google

class Question(object):

	def _formulate_query(self):
		
		q = self.text.lower()

		# Tokenize question
		token_list = q.split()

		# Remove stopwords
		stopwords_list = nltk.corpus.stopwords.words('english')
		final_list = [w for w in token_list if not (w in stopwords_list)]

		return " ".join(final_list)


	def __init__(self, id_q, text):
		self.id_q = id_q
		self.text = text
		self.query = self._formulate_query()


	def _get_search_engines(self):
		try:
			lang = MyConfig.get("search_engine", "lang")
			engines = eval(MyConfig.get("search_engine", "engines"))
			throttle = MyConfig.get("search_engine", "throttle")

			l = []
			for (engine, license) in engines:
				# Eval to something like this:
				# Google(google_license, throttle, lang)
				l.append(eval(engine + "(\"" + license + "\", " + throttle + ", " + lang + ")"))

			return l

		except ConfigParser.Error:
			sys.exit("_get_search_engines: config error")
		except Exception as e:
			print e
			sys.exit("_get_search_engines: fatal error")


	def search(self):
		search_engines = self._get_search_engines()

		try:
			num = int(MyConfig.get("search_engine", "n_results"))
		except ConfigParser.Error:
			num = 10

		results = []
		for engine in search_engines:
			results += engine.search(self.query, count=num)

		doc_list = []
		for resource in results:
			doc_list.append(Document(resource))

		
		output = open("documentos.pkl", "wb")
		pickle.dump(doc_list, output, 0)
		output.close()

		return doc_list






