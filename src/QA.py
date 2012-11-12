#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from Question import Question
from ConfigParser import ConfigParser

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
		pass

	return questions

def show_answers(algo):
	#do algo
	pass

if __name__ == '__main__':
	try:
		if len(sys.argv) == 1:
			questions = ask()
		elif len(sys.argv) == 2:
			questions = parse_questions(sys.argv[1])
		else:
			sys.exit("QA Error: bad syntax\nQA.py [file]\n")

		try:
			config = ConfigParser()
			config.read('config.cfg')
			num = config.getint("search_engine", "n_results")
		except:
			num = 10

		# questions :: list of Question
		for q in questions:
			q.search(num)

	except KeyboardInterrupt:
		sys.exit()

