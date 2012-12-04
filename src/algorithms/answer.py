# -*- coding: utf-8 -*-

import random

from Answer import Answer

class AnswerExtractionAlgorithm(object):

	@classmethod
	def cosa(self):
		pass


class XXXAlgorithm(AnswerExtractionAlgorithm):

	@classmethod
	def process_answer(self, passage, question):
		# Do magic
		window = "window = " + passage.text
		exact = "exact"
		random.seed()
		score = random.randint(0, 1000)
		if passage.document.url.find("wikipedia") != -1:
			score = 0

		answer = Answer(passage, question, window, exact, score)

		return answer
