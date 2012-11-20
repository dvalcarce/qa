# -*- coding: utf-8 -*-

import logging
import os
import re
from pattern.web import Result, URL, URLError, plaintext
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from Passage import Passage

class Document(object):

	def _binary_to_plaintext(self, content):
		print content
		text = " ".join(re.findall(r"[\w'?!\(\)\{\}\[\]\$\.,:;\-\_@\&\*\+]+", content))
		print "\n"*5
		print text
		return text

	def _pdf_to_plaintext(self, content):
		pdf_file = "tmp.pdf"

		f = open(pdf_file, "w")
		f.write(content)
		f.close()

		retrieval = StringIO()
		resource_manager = PDFResourceManager()
		layout_params = LAParams()
		encoding = "utf-8"
		device = TextConverter(resource_manager, retrieval, codec=encoding, laparams=layout_params)

		f = file(pdf_file, "rb")
		process_pdf(resource_manager, device, f)

		text = retrieval.getvalue()
		
		device.close()
		retrieval.close()
		f.close()
		os.remove(pdf_file)

		return text

	def _extract_text(self, text, mimetype):
		if (mimetype == "text/html" or mimetype == "xml"):
			return plaintext(text)
		elif (mimetype == "application/pdf"):
			self._pdf_to_plaintext(text)
		elif (mimetype == "text/plain"):
			return text
		else:
			return self._binary_to_plaintext(text)

	def _get_content(self, result):
		url = URL(result.url)
		mimetype = url.mimetype

		try:
			content = url.download()
		except:
			# If we cannot retrieve the document,
			# we skip it
			logger = logging.getLogger("qa_logger")
			logger.warning("%s couldn't be retrieved", result.url)
			return ""

		return self._extract_text(content, mimetype)


	def _get_passages(self, text):

		lines = text.split("\n")
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

	def __init__(self, result, rank):
		self.title = result.title
		self.url = result.url
		self.rank = rank
		self.description = plaintext(result.description)

		# Split document into passages
		content = self._get_content(result)
		self.passages = self._get_passages(content)

