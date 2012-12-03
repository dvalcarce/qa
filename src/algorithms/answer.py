# -*- coding: utf-8 -*-

from Answer import Answer

class AnswerExtractionAlgorithm(object):

	@classmethod
	def cosa(self):
		pass


class XXXAlgorithm(AnswerExtractionAlgorithm):

	@classmethod
	def process_answer(self, passage, question):
		# Do magic
		window = "window"
		exact = "exact"
		score = 0

		answer = Answer(passage, question, window, exact, score)

		return answer
