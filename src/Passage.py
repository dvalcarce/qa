# -*- coding: utf-8 -*-

import logging

from algorithms.answer import *
from algorithms.passage import *
from conf.MyConfig import MyConfig, MyConfigException

class Passage(object):

	def calculate_score(self, question):
		try:
			algorithm = MyConfig.get("passage_filtering", "algorithm")
			if (algorithm == "similarity"):
				self.score = SimilarityAlgorithm.calculate_score(question, self)
			elif (algorithm == "proximity"):
				self.score = ProximityAlgorithm.calculate_score(question, self)
			elif (algorithm == "mixed"):
				self.score = MixedAlgorithm.calculate_score(question, self)
			else:
				self.score = MixedAlgorithm.calculate_score(question, self)
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			self.score = MixedAlgorithm.calculate_score(question, self)


	def find_answer(self, question):
		try:
			algorithm = MyConfig.get("answer_extraction", "algorithm")
			if (algorithm == "xxx"):
				self.answer = XXXAlgorithm.process_answer(self, question)
			elif (algorithm == "entity"):
				self.answer = EntityRecognitionAlgorithm.process_answer(self, question)
			else:
				self.answer = None
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			self.answer = EntityRecognitionAlgorithm.process_answer(self, question)

		return self.answer


	def __init__(self, text, document):
		self.text = text
		self.document = document
		self.score = 0
