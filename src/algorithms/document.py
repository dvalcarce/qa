# -*- coding: utf-8 -*-

import logging
import nltk

from conf.MyConfig import MyConfig, MyConfigException
from Passage import Passage


# Algorithms for Document Segmentation

class DocumentSegmentationAlgorithm(object):

    @classmethod
    def split_into_passages(self, document):
        pass


class SplitIntoLinesAlgorithm(DocumentSegmentationAlgorithm):

    @classmethod
    def split_into_passages(self, document):
        if document is None or document.content is None or document.content == "":
            return []

        lines = document.content.split("\n")
        passage_list = []

        try:
            n_lines = int(MyConfig.get("document_segmentation", "n_lines"))
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            n_lines = 5

        # Iterating over the lines of the document
        # obtaining overlapped passages:
        #   max(1, len(lines)-n_lines+1)
        # Don't ask: magic numbers ;-)
        for i in range(0, max(1, len(lines) - n_lines + 1)):
            lines_of_text = lines[i: i + n_lines]
            # Join list of lines
            piece_of_text = "\n".join(lines_of_text)
            passage_list.append(Passage(piece_of_text, document))

        # Adds search engine snippet
        passage_list.append(Passage(document.description, document))

        return passage_list


class SplitIntoParagraphsAlgorithm(DocumentSegmentationAlgorithm):

    @classmethod
    def split_into_passages(self, document):
        if document is None or document.content is None or document.content == "":
            return []

        paragraphs = document.content.split("\n")

        passage_list = []

        for paragraph in paragraphs:
            passage_list.append(Passage(paragraph, document))

        # Adds search engine snippet
        passage_list.append(Passage(document.description, document))

        return passage_list


class SplitIntoSentencesAlgorithm(DocumentSegmentationAlgorithm):

    @classmethod
    def _aux(self, content, n_sentences, document):
        sent_list = nltk.sent_tokenize(content)
        passage_list = [Passage(" ".join(sent_list[i: i + n_sentences]),
            document) for i in range(0, max(1, len(sent_list) - n_sentences + 1))]

        return passage_list

    @classmethod
    def split_into_passages(self, document):
        if document is None or document.content is None or document.content == "":
            return []

        try:
            n_sentences = int(MyConfig.get("document_segmentation", "n_sentences"))
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            n_sentences = 5

        passage_list = self._aux(document.content, n_sentences, document)

        # Adds search engine snippet
        passage_list += self._aux(document.description, n_sentences, document)

        return passage_list
