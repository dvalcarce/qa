#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import nltk
import os
import pickle
import random
import sys

from nltk.corpus import qc
from nltk.tree import Tree

try:
	from qc.stanford_parser.StanfordParser import StanfordParser
except ImportError as e:
	from stanford_parser.StanfordParser import StanfordParser


class QuestionClassifier(object):

	classifiers = [
		("Naive Bayes", nltk.NaiveBayesClassifier, "qc_bayes.pkl"),
		("Decision Tree", nltk.DecisionTreeClassifier, "qc_dtc.pkl"),
		("Maximum Entropy", nltk.MaxentClassifier, "qc_maxent.pkl")
	]

	# For caching purposes
	_questions = {}
	_classifiers = {}

	_preps = ["in", "on"]

	_rules = {
		"ROOT": {
			"reverse": False,
			"type": "Category",
			"list": ["S", "SBARQ"]
			},
		"S": {
			"reverse": False,
			"type": "Category",
			"list": ["VP", "FRAG", "SBAR", "ADJP"]
			},
		"SBARQ": {
			"reverse": False,
			"type": "Category",
			"list": ["SQ", "S", "SINV", "SBARQ", "FRAG"]
			},
		"SQ": {
			"reverse": False,
			"type": "Category",
			"list": ["NP", "VP", "SQ"]
			},
		"NP": {
			"reverse": True,
			"type": "Position",
			"list": ["NP", "NN", "NNP", "NNPS", "NNS", "NX"]
			},
		"PP": {
			"reverse": False,
			"type": "Category",
			"list": ["WHNP", "NP", "WHADVP", "SBAR"]
			},
		"WHNP": {
			"reverse": False,
			"type": "Category",
			"list": ["NP", "NN", "NNP", "NNPS", "NNS", "NX"]
			},
		"WHADVP": {
			"reverse": False,
			"type": "Category",
			"list": ["NP", "NN", "NNP", "NNPS", "NNS", "NX"]
			},
		"WHADJP": {
			"reverse": False,
			"type": "Category",
			"list": ["NP", "NN", "NNP", "NNPS", "NNS", "NX"]
			},
		"WHPP": {
			"reverse": True,
			"type": "Category",
			"list": ["WHNP", "WHADVP", "NP", "SBAR"]
			},
		"VP": {
			"reverse": True,
			"type": "Category",
			"list": ["NP", "NN", "NNP", "NNPS", "NNS", "NX", "SQ", "PP"]
			},
		"SINV": {
			"reverse": False,
			"type": "Category",
			"list": ["NP"]
			},
		"NX": {
			"reverse": False,
			"type": "Category",
			"list": ["NP", "NN", "NNP", "NNPS", "NNS", "NX", "SQ"]
			}
	}


	@classmethod
	def _apply_rules(self, tree):
		node = tree.node

		if node not in self._rules:
			return ""

		# Non-trivial rules
		subtree = None
		if node == "SBARQ":
			for subtree in tree:
				if subtree.node in ["WHNP", "WHPP", "WHADJP", "WHADVP"] and len(subtree) >= 2:
					# Second non-trivial rule
					if subtree.node != "WHNP":
						return subtree
					else:
						for t in subtree:
							if t.node == "NP" and t[len(t)-1].node == "POS":
								return t
						return subtree

		# Percolation rules
		if self._rules[node]["reverse"]:
			tree.reverse()

		if self._rules[node]["type"] == "Category":
			for category in self._rules[node]["list"]:
				for child in tree:
					if category == child.node:
						if self._rules[node]["reverse"]:
							tree.reverse()
						return child
		else:
			for child in tree:
				if child.node in self._rules[node]["list"]:
					if self._rules[node]["reverse"]:
						tree.reverse()
					return child

		if self._rules[node]["reverse"]:
			tree.reverse()

		return ""


	@classmethod
	def _extract_head_word(self, tree):
		if not isinstance(tree, Tree):
			return tree
		if not isinstance(tree[0], Tree):
			return tree.leaves()[0]
		else:
			tree = self._apply_rules(tree)

			return self._extract_head_word(tree)


	@classmethod
	def _get_head_word(self, question):
		parser = StanfordParser.get_instance()
		processed_text = parser.process(question)
		tree = Tree(processed_text)
		return self._extract_head_word(tree)


	@classmethod
	def get_features(self, question, features):
		# Query question cache (optimization)
		if question in self._questions:
			return self._questions[question]

		tokens = nltk.word_tokenize(question)
		tagged_tokens = nltk.pos_tag(tokens)
		nouns = filter(lambda x: x[1] == "NN" or x[1] == "NNS", tagged_tokens)

		result = {}
		if "f" in features:
			result["first"] = tokens[0].lower() if tokens[0] not in self._preps else tokens[0] + " " + tokens[1]
		if "n" in features:
			result["noun"] = nouns[0][0].lower() if len(nouns) > 0 else ""
		if "h" in features:
			result["head"] = self._get_head_word(question).lower()

		self._questions[question] = result

		return result


	@classmethod
	def get_qc_corpus(self, path):
		f = open(path, "r")
		corpus = f.read()
		corpus = corpus.split("\n")
		corpus = [tuple(line.split(" ", 1)) for line in corpus]
		f.close()
		return corpus


	@classmethod
	def _get_folder(self, features):
		features = list(features)
		features.sort()
		folder = "".join(features)

		if not os.path.exists(os.path.join("qc", folder)):
			os.mkdir(os.path.join("qc", folder))

		return folder

	@classmethod
	def train(self, features):
		print "Getting training corpus"
		train_corpus = QuestionClassifier.get_qc_corpus(os.path.join("qc", "corpus", "qc_train.txt"))
		train_set = [(QuestionClassifier.get_features(question, features), entity) for (entity, question) in train_corpus]

		folder = self._get_folder(features)

		classifier = {}
		for (name, c, filename) in self.classifiers:
			print "Training " + name + " Classifier..."
			if name == "Maximum Entropy":
				classifier[name] = c.train(train_set, algorithm="iis")
			else:
				classifier[name] = c.train(train_set)
			f = open(os.path.join("qc", folder, filename), "wb")
			pickle.dump(classifier[name], f, 0)
			f.close()


	@classmethod
	def test(self, features):
		print "Getting testing corpus"
		test_corpus = QuestionClassifier.get_qc_corpus(os.path.join("qc", "corpus", "qc_test.txt"))
		test_set = [(QuestionClassifier.get_features(question, features), entity) for (entity, question) in test_corpus]

		folder = self._get_folder(features)

		classifier = {}
		print "Accuracy tests"
		for (name, _, filename) in self.classifiers:
			pkl_file = open(os.path.join("qc", folder, filename), "rb")
			classifier[name] = pickle.load(pkl_file)
			accuracy = nltk.classify.accuracy(classifier[name], test_set)
			print name + " Classifier: \t" + str(accuracy)
			pkl_file.close()


	@classmethod
	def classify(self, path, question, features):
		# Classifier cache (optimization)
		if path not in self._classifiers:
			try:
				pkl_file = open(path)
			except IOError:
				try:
					pkl_file = open(os.path.join("qc", "fhn", "qc_bayes.pkl"))
				except IOError:
					logger = logging.getLogger("qa_logger")
					logger.error("Question classifier not available. Please, train one with qc/QuestionClassifier.py")
					sys.exit()

			self._classifiers[path] = pickle.load(pkl_file)
			pkl_file.close()

		return self._classifiers[path].classify(self.get_features(question, features))


if __name__ == '__main__':
	os.chdir(os.pardir)

	print "1. Train models"
	print "2. Test models"
	print "3. Classify question"
	print "4. Extract features"
	choice = int(raw_input("Choose what you want: "))

	print "f. First word"
	print "h. Head word"
	print "n. First noun"
	choice2 = raw_input("Choose the preferred features: ").lower()

	features = set(choice2) & {"f", "h", "n"}

	if choice == 1:
		# Choice 1 (Train)
		QuestionClassifier.train(features)
	if choice < 3:
		# Choices 1 and 2 (Train and Test)
		QuestionClassifier.test(features)
	else:
		# Choices 3 and 4 (Classify and Extract features)
		question = raw_input("Write your question: ")
		print "Getting features"
		result = QuestionClassifier.get_features(question, features)
		if choice == 3:
			# Choice 3 (Classify)
			try:
				classifier = {}
				for (name, _, filename) in QuestionClassifier.classifiers:
					folder = QuestionClassifier._get_folder(features)
					f = open(os.path.join("qc", folder, filename), "rb")
					classifier[name] = pickle.load(f)
					f.close()
					entities = classifier[name].classify(result)
					print name + " Classifier: \t" + str(entities)
			except Exception as e:
				print e
		else:
			# Choice 4 (Extract features)
			print result
