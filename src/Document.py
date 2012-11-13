# -*- coding: utf-8 -*-

import os
import re
from pattern.web import Result, URL, URLError, plaintext
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

class Document(object):

	def _extract_text(self, content):
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


	def get_content(self, result):
		url = URL(result.url)
		mimetype = url.mimetype

		try:
			content = url.download()
		except URLError:
			return ""

		if (mimetype == "text/html" or mimetype == "xml"):
			return plaintext(content)
		elif (mimetype == "application/pdf"):
			self._pdf_to_plaintext(content)
		elif (mimetype == "text/plain"):
			return content
		else:
			return self._extract_text(content)


	def __init__(self, result):
		self.title = result.title
		self.url = result.url
		self.description = result.description
		self.content = self.get_content(result)
