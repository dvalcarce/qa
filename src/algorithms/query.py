# -*- coding: utf-8 -*-

import nltk.corpus

class QueryFormulationAlgorithm(object):

	@classmethod
	def formulate_query(self, question):
		pass

class StopwordsAlgorithm(QueryFormulationAlgorithm):

	@classmethod
	def formulate_query(self, question):
		question = question.lower()

		# Remove symbols
		l = list(question)									# list of characters
		symbols = [",", "?", "!", ".", "(", ")", ";", ":"]	# list of symbols
		l2 = filter(lambda x: x not in symbols , l)			# filter symbols
		question = "".join(l2)								# list of chars -> string

		# Tokenize question
		token_list = question.split()

		# Remove stopwords
		stopwords_list = nltk.corpus.stopwords.words('english')
		final_list = [w for w in token_list if not (w in stopwords_list)]

		return " ".join(final_list)
