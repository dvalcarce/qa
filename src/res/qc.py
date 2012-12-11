#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
import pickle

from nltk.corpus import qc

_preps = ["in", "on"]

def get_features(question):
	q = question.lower()
	q = nltk.word_tokenize(q)
	tokens = nltk.pos_tag(q)
	nouns = filter(lambda x: x[1] == "NN", tokens)
	result = {}
	result["first"] = q[0] if q[0] not in _preps else q[0] + " " + q[1]
	result["noun"] = nouns[0] if len(nouns) > 0 else ""
	return result

def get_qc_corpus(path):
	f = open(path, "r")
	corpus = f.read()
	corpus = corpus.split("\n")
	corpus = [tuple(line.split(" ", 1)) for line in corpus]
	f.close()
	return corpus

train_corpus = get_qc_corpus("corpus/qc_train.txt")
train_set = [(get_features(question), entity) for (entity, question) in train_corpus]

test_corpus = get_qc_corpus("corpus/qc_test.txt")
test_set = [(get_features(question), entity) for (entity, question) in test_corpus]

classifier = nltk.NaiveBayesClassifier.train(train_set)
f = open("qc_bayes.pkl", "wb")
pickle.dump(classifier, f, 0)
f.close()
print nltk.classify.accuracy(classifier, test_set)

classifier = nltk.MaxentClassifier.train(train_set)
f = open("qc_maxent.pkl", "wb")
pickle.dump(classifier, f, 0)
f.close()
print nltk.classify.accuracy(classifier, test_set)
