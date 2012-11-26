# -*- coding: utf-8 -*-

import logging
import Passage

from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from MyConfig import MyConfig
from query import *

# Algorithms for Passage Retrieval

class PassageRetrievalAlgorithm(object):

	@classmethod
	def split_into_passages(self, document):
		pass


class FixedNumberOfLinesAlgorithm(PassageRetrievalAlgorithm):

	@classmethod
	def split_into_passages(self, document, text):
		lines = document.split("\n")
		passage_list = []

		try:
			n_lines = int(MyConfig.get("passage_retrieval", "n_lines"))
		except:
			n_lines = 5

		# Iterating over the lines of the document
		# obtaining overlapped passages:
		# 	max(1, len(lines)-n_lines+1)
		# Don't ask: magic numbers ;-)
		for i in range(0, max(1, len(lines)-n_lines+1)):
			lines_of_text = lines[i : i+n_lines]
			# Join list of lines
			piece_of_text = "\n".join(lines_of_text)
			passage_list.append(Passage(piece_of_text, self))

		return passage_list


class SplitIntoParagraphsAlgorithm(PassageRetrievalAlgorithm):

	@classmethod
	def split_into_passages(self, document, text):
		paragraphs = text.split("\n")

		passage_list = []
		# Iterating over the lines of the document
		# obtaining overlapped passages:
		# 	max(1, len(lines)-n_lines+1)
		# Don't ask: magic numbers ;-)
		for paragraph in paragraphs:
			passage_list.append(Passage(paragraph, document))

		return passage_list


# Algorithms for Passage Evaluation

class PassageEvaluationAlgorithm(object):

	@classmethod
	def calculate_score(self, question, passage):
		pass

class SimilarityAlgorithm(PassageEvaluationAlgorithm):

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
			num = int(MyConfig.get("search_engine", "n_results"))
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("search_engine:n_results not found")
			return score

		# Reverse rank order from 1..n to n..1
		rank = num - rank + 1

		# Normalize rank from n..1 to 1..0
		rank = (rank - 1) / (num - 1)

		# Weight score by rank
		score = score * rank

		return score
