# -*- coding: utf-8 -*-

import logging
from MyConfig import MyConfig
from pattern.web import Result, plaintext

class Answer(object):

	@classmethod
	def comparator(x, y):
		return cmp(x.score, y.score)

	def __str__(self):
		id_q = self.question.id_q
		
		try:
			exact = MyConfig.get("show_answer", "exact") == "True"
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("show_answer exact not found")
			exact = False

		run_tag = "plna" + ("ex" if exact else "st") + "031ms"
		score = self.score
		url = self.passage.document.url
		text = self.exact if exact else self.window

		return id_q + " " + run_tag + " {0} " + score + " " + url + " " + text


	def __init__(self, passage, question, window, exact, score):
		self.passage = passage
		self.question = question
		self.window = window
		self.exact = exact
		self.score = score
