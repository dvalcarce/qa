# -*- coding: utf-8 -*-

import logging

from conf.MyConfig import MyConfig, MyConfigException


class Answer(object):

    @classmethod
    def get_run_tag(self):
        try:
            exact = MyConfig.get("show_answer", "exact") == "True"
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            exact = False

        return ("plna" + ("ex" if exact else "st") + "031ms", exact)

    def is_successful(self):
        return self.exact != "" or self.window != ""

    def __str__(self):
        id_q = self.question.id_q
        (run_tag, exact) = Answer.get_run_tag()
        score = self.score
        url = self.passage.document.url
        text = self.exact if exact else self.window

        text = text.replace("}", "}}").replace("{", "{{")

        return id_q + " " + run_tag + " {0} " + str(score) + " " + url + " " + text

    def __init__(self, passage, question, window, exact, score):
        self.passage = passage
        self.question = question
        self.window = window
        self.exact = exact
        self.score = score

    def __eq__(self, other):
        return self.exact.lower() == other.exact.lower()

    def __cmp__(self, other):
        return cmp(self.exact.lower(), other.exact.lower())

    def __hash__(self):
        return hash(self.exact.lower())
