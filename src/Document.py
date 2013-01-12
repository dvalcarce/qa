# -*- coding: utf-8 -*-

import logging
import os
import re
import utils

from algorithms.document import *
from conf.MyConfig import MyConfig, MyConfigException
from cStringIO import StringIO
from Passage import Passage
from pattern.web import Result, URL, URLError, plaintext
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf

class Document(object):

	def _binary_to_plaintext(self, content):
		text = " ".join(re.findall(r"[\w'?!\(\)\{\}\[\]\$\.,:;\-\_@\&\*\+]+", content))
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
		try:
			process_pdf(resource_manager, device, f)
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("pdf file couldn't be retrieved (no permissions?)")
			return ""

		text = retrieval.getvalue()
		
		device.close()
		retrieval.close()
		f.close()
		os.remove(pdf_file)

		return text


	def _extract_text(self, text, mimetype):
		if (mimetype == "text/html" or mimetype == "xml"):
			try:
				text = plaintext(text)
			except:
				return ""
			return utils.from_unicode_to_ascii(text)
		elif (mimetype == "application/pdf"):
			self._pdf_to_plaintext(text)
		elif (mimetype == "text/plain"):
			return text
		else:
			logger = logging.getLogger("qa_logger")
			logger.debug("document mimetype %s processed", mimetype)
			return self._binary_to_plaintext(text)


	def _get_content(self, result):
		url = URL(result.url)
		try:
			mimetype = url.mimetype

			try:
				timeout = int(MyConfig.get("document_retrieval", "timeout"))
			except MyConfigException as e:
				logger = logging.getLogger("qa_logger")
				logger.warning(str(e))
				timeout = 15

			content = url.download(timeout=timeout)
		except:
			# If we cannot retrieve the document,
			# we skip it
			logger = logging.getLogger("qa_logger")
			logger.warning("%s couldn't be retrieved", result.url)
			return ""

		return self._extract_text(content, mimetype)


	def __init__(self, result, rank):
		self.title = result.title
		self.url = utils.from_unicode_to_ascii(result.url)
		self.rank = rank
		self.description = utils.from_unicode_to_ascii(result.description)

		self.content = self._get_content(result)

		# Split document into passages
		try:
			algorithm = MyConfig.get("document_segmentation", "algorithm")
			if algorithm == "lines":
				self.passages = SplitIntoLinesAlgorithm.split_into_passages(self)
			elif algorithm == "paragraphs":
				self.passages = SplitIntoParagraphsAlgorithm.split_into_passages(self)
			elif algorithm == "sentences":
				self.passages = SplitIntoSentencesAlgorithm.split_into_passages(self)
			else:
				self.passages = SplitIntoParagraphsAlgorithm.split_into_passages(self)
		except MyConfigException as e:
			logger = logging.getLogger("qa_logger")
			logger.warning(str(e))
			self.passages = SplitIntoParagraphsAlgorithm.split_into_passages(self, self.content)
