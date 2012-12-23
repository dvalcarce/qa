#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import logging, logging.config
import os
import pickle
import re
import sys
import utils

from Answer import Answer
from ConfigParser import ConfigParser
from datetime import datetime
from conf.MyConfig import MyConfig, MyConfigException
from nltk.probability import FreqDist
from Passage import Passage
from Question import Question

class QA(object):

	def init_logger(self):
		directory = "log"
		log_config = os.path.join("conf", "logging.conf")
		if not os.path.exists(directory):
			os.mkdir(directory)
		if not os.path.exists(log_config):
			sys.exit("Missing or invalid log configuration")

		try:
			logging.config.fileConfig(log_config)
		except:
			sys.exit("fileConfig: Critical error")

		logging.getLogger("qa_logger").debug('logging initialized')


	def ask(self):
		print "Welcome to the best Question Answering System"
		q = raw_input("Write your question: ")

		while (q == None or q == ""):
			q = raw_input("Write your question: ")

		return [Question("0001", q)]


	def parse_questions(self, path):
		try:
			q_file = codecs.open(path, "r", encoding="utf-8", errors="ignore")
		except:
			sys.exit("QA Error: bad argument")

		questions = []
		for line in q_file:
			# We use a regular expression for matching questions
			m = re.match(r"(?P<id>[^ \t]+)[ \t]*(?P<question>.+)", line)
			id_q = m.group("id")
			q = m.group("question")
			questions.append(Question(id_q, q))

		try:
			q_file.close()
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("Questions file not closed")

		return questions


	def score_passages(self, doc_list, question):
		passage_list = []

		logger = logging.getLogger("qa_logger")
		logger.info("%s:\t\tDocument Segmentation", question.id_q)

		for doc in doc_list:
			for passage in doc.passages:
				passage.calculate_score(question)
				passage_list.append(passage)

		return passage_list


	def get_relevant_passages(self, doc_list, question):
		logger = logging.getLogger("qa_logger")
		logger.info("%s:\tPassage Retrieval", question.id_q)

		passage_list = self.score_passages(doc_list, question)
		passage_list.sort(key=lambda x: x.score, reverse=True)

		# Select n best passages
		try:
			n = int(MyConfig.get("document_segmentation", "n_relevants"))
		except:
			n = 100
			logger = logging.getLogger("qa_logger")
			logger.warning("n_relevants not found")

		logger.info("%s:\t\tPassage Filtering", question.id_q)

		return passage_list[:n]


	def get_best_answers(self, passage_list, q):
		logger = logging.getLogger("qa_logger")
		logger.info("%s:\tAnswer Processing", q.id_q)

		empty = passage_list == []

		logger.info("%s:\t\tAnswer Extraction", q.id_q)

		answer_list = []
		for passage in passage_list:
			a = passage.find_answer(q)
			if a.is_successful():
				answer_list.append(a)

		if not answer_list:
			return ([], empty)

		logger.info("%s:\t\tAnswer Filtering", q.id_q)

		# Obtain answer frequency
		fd = FreqDist(answer_list)

		# Normalize frequencies
		normalize = fd.freq(fd.max())

		# Modify scores by frequency
		for answer in answer_list:
			answer.score = int(answer.score * (fd.freq(answer) / normalize))

		# Sort answers by score
		answer_list.sort(key=lambda x: x.score, reverse=True)

		# Filter bad answers
		try:
			threshold = int(MyConfig.get("answer_filtering", "threshold"))
		except:
			logger = logging.getLogger("qa_logger")
			logger.error("answer quality threshold not found")
			threshold = 50

		answer_list = filter(lambda x: x.score > threshold, answer_list)

		final_answers = []
		for a in answer_list:
			if a not in final_answers:
				final_answers.append(a)
			if len(final_answers) == 3:
				break

		return (final_answers, empty)


	def write_answers(self, answer_list, empty, q):
		id_q = q.id_q
		(run_tag, _) = Answer.get_run_tag()

		date = datetime.strftime(datetime.today(), "%Y-%m-%d_%H:%M:%S")
		folder = "answers"
		if not os.path.isdir(folder) and os.path.exists(folder):
			logger = logging.getLogger("qa_logger")
			logger.error("answers folder cannot be created")
			sys.exit()
		if not os.path.exists(folder):
			os.mkdir(folder)

		f = codecs.open(os.path.join(folder, date + ".txt"), "a", encoding="utf-8", errors="ignore")

		if answer_list == []:

			if empty:
				# If there are no documents related to the query,
				# then there is no answer with maximum probability.
				f.write(id_q + " " + run_tag + " 1 1000 NIL\n")
			else:
				# If there are no good answer,
				# then we return NIL with score 0.
				f.write(id_q + " " + run_tag + " 1 0 NIL\n")
			return

		position = 1
		for answer in answer_list:
			f.write(str(answer).format(position) + "\n")
			position += 1

		if len(answer_list) < 3:
			# If the are less than 3 good answers,
			# then we return NIL with score 0 in the next position
			f.write(id_q + " " + run_tag + " " + str(position) + " 0 NIL\n")

		f.close()


	def debug(self):
		pkl_file = open('documentos.pkl', 'rb')
		doc_list = pickle.load(pkl_file)
		q = Question("0001", "Who discovered radium?")
		passages = self.get_relevant_passages(doc_list, q)
		(answers, empty) = self.get_best_answers(passages, q)
		self.write_answers(answers, empty, q)

		sys.exit()

	def main(self):
		try:
			self.init_logger()

			if len(sys.argv) == 1:
				questions = self.ask()
			elif len(sys.argv) == 2:
				# DEBUG
				if sys.argv[1] == "pickle":
					self.debug()
				# END DEBUG
				questions = self.parse_questions(sys.argv[1])
			else:
				sys.exit("QA Error: bad syntax\nQA.py [file]")

			for q in questions:
				doc_list = q.search()
				passages = self.get_relevant_passages(doc_list, q)
				(answers, empty) = self.get_best_answers(passages, q)
				self.write_answers(answers, empty, q)

		except KeyboardInterrupt:
			sys.exit("Exiting...")
		finally:
			utils.clean()


if __name__ == '__main__':
	qa = QA()
	qa.main()
