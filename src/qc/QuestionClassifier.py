#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
import pickle

from nltk.corpus import qc


class QuestionClassifier(object):

	classifiers = [
		("Naive Bayes", nltk.NaiveBayesClassifier, "qc_bayes.pkl"),
		("Decision Tree", nltk.DecisionTreeClassifier, "qc_dtc.pkl"),
		("Maximum Entropy", nltk.MaxentClassifier, "qc_maxent.pkl")
	]

	# For caching purposes
	_questions = {}

	_preps = ["in", "on"]

	@classmethod
	def get_features(self, question):
		# Query question cache (optimization)
		if self._questions.__contains__(question):
			return self._questions[question]

		q = question.lower()
		q = nltk.word_tokenize(q)
		tokens = nltk.pos_tag(q)
		nouns = filter(lambda x: x[1] == "NN", tokens)

		result = {}
		result["first"] = q[0] if q[0] not in self._preps else q[0] + " " + q[1]
		result["noun"] = nouns[0] if len(nouns) > 0 else ""

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
	def train(self):
		print "Getting training corpus"
		train_corpus = QuestionClassifier.get_qc_corpus("corpus/qc_train.txt")
		train_set = [(QuestionClassifier.get_features(question), entity) for (entity, question) in train_corpus]

		print "Getting testing corpus"
		test_corpus = QuestionClassifier.get_qc_corpus("corpus/qc_test.txt")
		test_set = [(QuestionClassifier.get_features(question), entity) for (entity, question) in test_corpus]

		classifier = {}
		for (name, c, filename) in self.classifiers:
			print "Training " + name + " Classifier..."
			if name == "Maximum Entropy":
				classifier[name] = c.train(train_set, algorithm="iis")
			else:
				classifier[name] = c.train(train_set)
			f = open(filename, "wb")
			pickle.dump(classifier[name], f, 0)
			f.close()

		print "Accuracy tests"
		for (name, _, _) in self.classifiers:
			accuracy = nltk.classify.accuracy(classifier[name], test_set)
			print name + " Classifier: \t" + str(accuracy)


if __name__ == '__main__':
	print "1. Train models"
	print "2. Classify question"
	choice = int(raw_input("Choose what you want: "))

	if choice == 1:
		QuestionClassifier.train()
	else:
		question = raw_input("Write your question: ")
		print "Getting features"
		features = QuestionClassifier.get_features(question)
		try:
			classifier = {}
			for (name, _, filename) in QuestionClassifier.classifiers:
				f = open(filename, "rb")
				classifier[name] = pickle.load(f)
				f.close()
				entities = classifier[name].classify(features)
				print name + " Classifier: \t" + str(entities)
		except Exception as e:
			print e
