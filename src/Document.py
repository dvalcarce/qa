# -*- coding: utf-8 -*-

import logging
import os
import re
import struct
import utils

from algorithms.document import *
from conf.MyConfig import MyConfig, MyConfigException
from cStringIO import StringIO
from pattern.web import URL, plaintext
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf, PDFTextExtractionNotAllowed


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
        except PDFTextExtractionNotAllowed:
            logger = logging.getLogger("qa_logger")
            logger.warning("pdf file couldn't be retrieved (no permissions?)")
            return ""
        except struct.error as e:
            logger = logging.getLogger("qa_logger")
            logger.warning("pdfminer internal error " + str(e))
            return ""
        except Exception as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            return ""

        text = retrieval.getvalue()

        device.close()
        retrieval.close()
        f.close()
        os.remove(pdf_file)

        return utils.from_unicode_to_ascii(text)

    def _extract_text(self, text, mimetype):
        if mimetype == "text/html" or mimetype == "application/xml":
            return plaintext(text)
        elif mimetype == "application/pdf":
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
            timeout = int(MyConfig.get("document_retrieval", "timeout"))
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            timeout = 15

        try:
            mimetype = url.mimetype
            content = utils.from_unicode_to_ascii(url.download(timeout=timeout, unicode=True))
        except Exception as e:
            # If we cannot retrieve the document, we skip it
            logger = logging.getLogger("qa_logger")
            logger.warning("%s couldn't be retrieved", result.url)
            logger.warning(str(e))
            return ""

        return self._extract_text(content, mimetype)

    def __init__(self, result, rank):
        self.title = result.title
        self.url = utils.from_unicode_to_ascii(result.url)
        self.rank = rank
        self.description = utils.from_unicode_to_ascii(result.description)

        self.content = utils.from_unicode_to_ascii(self._get_content(result))

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
            self.passages = SplitIntoParagraphsAlgorithm.split_into_passages(self)
