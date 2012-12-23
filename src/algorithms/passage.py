# -*- coding: utf-8 -*-

import logging

from conf.MyConfig import MyConfig, MyConfigException
from nltk.stem.porter import PorterStemmer
from query import *

# Algorithms for Passage Filtering

class PassageFilteringAlgorithm(object):

	@classmethod
	def calculate_score(self, question, passage):
		pass


class SimilarityAlgorithm(PassageFilteringAlgorithm):

	@classmethod
	def calculate_score(self, question, passage):
		rank = passage.document.rank
		q = question.text
		text = passage.text

		# Remove stopwords from question and passage
		# and split it into words
		q = StopwordsAlgorithm.formulate_query(q).split()
		text = StopwordsAlgorithm.formulate_query(text).split()

		# Apply stemming to q and text
		porter = PorterStemmer()
		q = map(porter.stem, q)
		text = map(porter.stem, text)

		# Filter all words in passage that they are
		# not present in question
		words = filter(lambda x: x in q, text)

		# Our initial score is the number of coincidences
		score = len(words)

		try:
			num = int(MyConfig.get("document_retrieval", "n_results"))
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			return score

		# Reverse rank order from 1..n to n..1
		rank = num - rank + 1

		# Normalize rank from n..1 to 1..0
		rank = (rank - 1) / (num - 1)

		# Weight score by rank
		score = score * rank

		return score
