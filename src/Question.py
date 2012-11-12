# -*- coding: utf-8 -*-

import nltk
import pprint
from Document import Document
from ConfigParser import ConfigParser
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
			config = ConfigParser()
			config.read('config.cfg')
			
			lang = config.get("search_engine", "lang")
			engines = eval(config.get("search_engine", "engines"))
			throttle = config.getint("search_engine", "throttle")
		except:
			pass


		# Eval config file to something like this:
		# Google(google_license, throttle, lang)			
		return [eval(engine + "(\"" + license + "\", throttle, lang)") for (engine, license) in engines]


	def search(self, num):
		search_engines = self._get_search_engines()
		
		results = []
		for engine in search_engines:
			results += engine.search(self.query, count=num)

		doc_list = []
		for resource in results:
			doc_list.append(Document(resource))

		return doc_list






