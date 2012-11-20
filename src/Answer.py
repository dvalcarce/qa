# -*- coding: utf-8 -*-

from pattern.web import Result, plaintext

class Answer(object):

	def _get_content(self, url):
		return plaintext(url.download())

	def __init__(self, result):
		self.title = result.title
		self.url = result.url
		self.description = result.description
		self.content = self._get_content(result)
