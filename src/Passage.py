# -*- coding: utf-8 -*-

from pattern.web import Result, plaintext
from random import random

class Passage(object):

	def calculate_score(self):
		self.score = int(random()*10)

	def __init__(self, text):
		self.text = text
