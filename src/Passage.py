# -*- coding: utf-8 -*-

import logging
from MyConfig import MyConfig

from algorithms.passage import *

class Passage(object):

	@classmethod
	def comparator(x, y):
		return cmp(x.score, y.score)

	def calculate_score(self, question):
		try:
			algorithm = MyConfig.get("passage_score", "algorithm")
			if (algorithm == "similarity"):
				self.score = SimilarityAlgorithm.calculate_score(question, self)
			elif (algorithm == "0"):
				self.score = 0
			else:
				self.score = 0
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("passage evaluation algorithm not found")
			self.score = SimilarityAlgorithm.calculate_score(question, self)

	def find_answer(self, question):
		try:
			algorithm = MyConfig.get("answer_retrieval", "algorithm")
			if (algorithm == "xxx"):
				self.answer = XXXAlgorithm.process_answer(self, question)
			elif (algorithm == "0"):
				self.answer = None
			else:
				self.answer = None
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("answer retrieval algorithm not found")
			self.answer = XXXAlgorithm.process_answer(self, question)

		return self.answer

	def __init__(self, text, document):
		self.text = text
		self.document = document
		self.score = 0
