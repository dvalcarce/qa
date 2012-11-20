# -*- coding: utf-8 -*-

import logging
from MyConfig import MyConfig

from algorythms.passage import *

class Passage(object):

	def calculate_score(self, question):

		try:
			algorythm = MyConfig.get("passage_score", "algorythm")
			if (algorythm == "similarity"):
				self.score = SimilarityAlgorithm.calculate_score(question, self)
			elif (algorythm == "0"):
				self.score = 0
			else:
				self.score = 0
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("passage algorythm not found")
			self.score = SimilarityAlgorithm.calculate_score(question, self)

	def __init__(self, text, document):
		self.text = text
		self.document = document
