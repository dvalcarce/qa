# -*- coding: utf-8 -*-

import logging
import nltk
import pickle
import sys

from algorithms.query import *
from ast import literal_eval as safe_eval
from conf.MyConfig import MyConfig, MyConfigException
from Document import Document
from pattern.web import Google, Bing

class Question(object):

	def _formulate_query(self):
		try:
			algorithm = MyConfig.get("query_formulation", "algorithm")
			if algorithm == "stopwords":
				return StopwordsAlgorithm.formulate_query(self.text)
			else:
				return StopwordsAlgorithm.formulate_query(self.text)
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			return StopwordsAlgorithm.formulate_query(self.text)


	def __init__(self, id_q, text):
		self.id_q = id_q
		self.text = text
		self.query = self._formulate_query()


	def _get_search_engines(self):
		try:
			lang = MyConfig.get("document_retrieval", "lang")
			engines = safe_eval(MyConfig.get("document_retrieval", "engines"))
			throttle = MyConfig.get("document_retrieval", "throttle")

			l = []
			for (engine, license) in engines:
				# Eval to something like this:
				# Google(google_license, throttle, lang)
				l.append(eval(engine + "(\"" + license + "\", " + throttle + ", " + lang + ")"))
			return l

		except MyConfigException:
			sys.exit("_get_search_engines: config error")
		except:
			logger = logging.getLogger("qa_logger")
			logger.exception("_get_search_engines: fatal error")
			sys.exit(2)


	def search(self):
		search_engines = self._get_search_engines()

		try:
			num = int(MyConfig.get("document_retrieval", "n_results"))
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			num = 10

		results = []
		for engine in search_engines:
			results += engine.search(self.query, count=num)

		doc_list = []
		# rank loops over [0..num-1]
		rank = 0
		# ignore repeated urls
		unique_urls = set()
		for resource in results:
			if resource.url in unique_urls:
				continue
			unique_urls.add(resource.url)

			# rank+1 loops over [1..num]
			# rank+1 is the relative position of the results
			doc_list.append(Document(resource, rank+1))
			rank = (rank+1) % num

		try:
			if MyConfig.get("persistence", "document") == "True":
				output = open("documentos.pkl", "wb")
				pickle.dump(doc_list, output, 0)
				output.close()
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))

		return doc_list
