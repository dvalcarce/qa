#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging, logging.config
import os
import sys
import re
import pickle
from Answer import Answer
from Passage import Passage
from MyConfig import MyConfig
from Question import Question
from ConfigParser import ConfigParser

def init_logger():
	directory = "log"
	log_config = "conf/logging.conf"
	if not os.path.exists(directory):
		os.mkdir(directory)
	if not os.path.exists(log_config):
		sys.exit("Missing or invalid log configuration")

	try:
		logging.config.fileConfig(log_config)
	except:
		sys.exit("fileConfig: Critical error")

	logging.getLogger("qa_logger").debug('logging initialized')


def ask():
	print "Welcome to the best Question Answering System"
	q = raw_input("Write your question: ")
	
	while (q == None or q == ""):
		q = raw_input("Write your question: ")

	return [Question("0001", q)]


def parse_questions(path):
	try:
		q_file = open(path, "r")
	except:
		sys.exit("QA Error: bad argument\n")

	questions = []
	for line in q_file:
		# We use a regular expression for matching questions
		m = re.match(r"(?P<id>[^ \t]*)[ \t]*(?P<question>.*)", line)
		id_q = m.group("id")
		q = m.group("question")
		questions.append(Question(id_q, q))

	try:
		q_file.close()
	except:
		logger = logging.getLogger("qa_logger")
		logger.warning("Questions file not closed")

	return questions


def score_passages(doc_list, question):
	passage_list = []

	for doc in doc_list:
		for passage in doc.passages:
			passage.calculate_score(question)
			passage_list.append(passage)

	return passage_list


def get_relevant_passages(doc_list, question):
	passage_list = score_passages(doc_list, question)
	passage_list.sort(key=lambda x: x.score, reverse=True)

	# Select n best passages
	try:
		n = int(MyConfig.get("passage_retrieval", "n_relevants"))
	except:
		n = 100
		logger = logging.getLogger("qa_logger")
		logger.warning("n_relevants not found")
	
	return passage_list[:n]


def get_best_answers(passage_list, q):
	answer_list = []
	for passage in passage_list:
		answer_list.append(passage.find_answer(q))

	# Calculate best answers
	answer_list.sort(key=lambda x: x.score, reverse=True)

	return answer_list[:3]


def show_answers(answer_list):
	for i in range(0, 3):
		print str(answer_list[i]).format(i+1)


if __name__ == '__main__':
	try:
		init_logger()

		if len(sys.argv) == 1:
			questions = ask()
		elif len(sys.argv) == 2:
			# DEBUG
			if sys.argv[1] == "pickle":
				pkl_file = open('documentos.pkl', 'rb')
				doc_list = pickle.load(pkl_file)
				score_passages(doc_list, Question("0001", "Who discovered radium?"))
			# END DEBUG
			questions = parse_questions(sys.argv[1])
		else:
			sys.exit("QA Error: bad syntax\nQA.py [file]")

		for q in questions:
			doc_list = q.search()
			passages = get_relevant_passages(doc_list, q)
			answers = get_best_answers(passages, q)
			show_answers(answers)


	except KeyboardInterrupt:
		sys.exit("\nExiting...")

