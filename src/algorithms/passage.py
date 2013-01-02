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

		# Normalize rank from n..1 to 1..0.5
		rank = (rank - 2 + num) / (2*num - 2)

		# Weight score by rank
		score = score * rank

		return score


class ProximityAlgorithm(PassageFilteringAlgorithm):

	@classmethod
	def calculate_score(self, question, passage):
		rank= passage.document.rank
		q= question.text
		text= passage.text

		# Removestopwords from question and passage
		# and split it into words
		q= StopwordsAlgorithm.formulate_query(q).split()
		text= StopwordsAlgorithm.formulate_query(text).split()

		# Apply stemming to q and text
		porter= PorterStemmer()
		q= map(porter.stem, q)
		text= map(porter.stem, text)

		score= 0
		searched_term= 0
		last_match= 0
		first_match= True

		if len(q) < 1:
			return 0

		for i in range(1, len(text)):
			if searched_term >= len(q):
				searched_term= 0
			if text[i] == q[searched_term]:
				if first_match:
					score+= 1
					first_match= False
				else:
					score+= 1/(i-last_match)
				last_match= i
				searched_term+= 1

		try:
			num = int(MyConfig.get("document_retrieval", "n_results"))
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			return score

		# Reverse rank order from 1..n to n..1
		rank = num - rank + 1

		# Normalize rank from n..1 to 1..0.5
		rank = (rank - 2 + num) / (2*num - 2)

		# Weight score by rank
		score = score * rank

		return score


class MixedAlgorithm(PassageFilteringAlgorithm):

	@classmethod
	def calculate_score(self, question, passage):
		score1 = SimilarityAlgorithm.calculate_score(question, passage)
		score2 = ProximityAlgorithm.calculate_score(question, passage)

		return (score1 + score2) / 2

