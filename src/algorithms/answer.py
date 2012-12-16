# -*- coding: utf-8 -*-

import itertools
import logging
import nltk
import pickle
import random
import re

from Answer import Answer
from collections import Counter
from MyConfig import MyConfig
from nltk.probability import FreqDist
from nltk.tree import Tree
from res.qc import QuestionClassifier

class AnswerExtractionAlgorithm(object):

	@classmethod
	def process_answer(self, passage, question):
		pass


class XXXAlgorithm(AnswerExtractionAlgorithm):

	@classmethod
	def process_answer(self, passage, question):
		# Do magic
		window = "window = " + passage.text
		exact = "exact"
		random.seed()
		score = random.randint(0, 1000)
		if passage.document.url.find("wikipedia") != -1:
			score = 0

		answer = Answer(passage, question, window, exact, score)

		return answer


class EntityRecognitionAlgorithm(AnswerExtractionAlgorithm):

	@classmethod
	def _question_classification(self, question):
		# Choose the specified classifier
		try:
			classifier = MyConfig.get("answer_extraction", "question_classifier")
			if classifier == "bayes":
				pkl_file = open('res/qc_bayes.pkl')
			elif classifier == "dct":
				pkl_file = open('res/qc_dtc.pkl')
			else:
				pkl_file = open('res/qc_maxent.pkl')
		except:
			logger = logging.getLogger("qa_logger")
			logger.warning("EntityRecognitionAlgorithm: question_classifier not found")
			pkl_file= open('res/qc_maxent.pkl')

		classifier = pickle.load(pkl_file)
		pkl_file.close()

		# Question classification
		return classifier.classify(QuestionClassifier.get_features(question))

	@classmethod
	def _ne_recognition(self, text, searched_entities):
		# Entity Classification
		sentences = nltk.sent_tokenize(text)
		tokenized_sentences = [nltk.word_tokenize(s) for s in sentences]
		tagged_sentences = [nltk.pos_tag(s) for s in tokenized_sentences]
		ne_chunked_sentences = nltk.batch_ne_chunk(tagged_sentences)

		# Entity Extraction
		entities = []
		for tree in ne_chunked_sentences:
			for child in tree:
				if isinstance(child, Tree) and child.node in searched_entities:
					entity = " ".join([word for (word, pos) in child.leaves()])
					entities.append(entity)

		if 'OTHER' in searched_entities:
			entities += self._other_recognition(tagged_sentences, entities)

		if 'NUMBER' in searched_entities:
			entities += self._number_recognition(text, entities)

		return entities

	@classmethod
	def _other_recognition(self, tagged_sentences, entities):
		# Nouns retrieval
		nouns = []
		for sentence in tagged_sentences:
			nouns += filter(lambda x: x[1] == "NN", sentence)
		nouns = [noun for (noun, tag) in nouns]
		nouns = set(nouns)

		# Nouns filtering
		#for noun in nouns:
		#	for entity in entities:
		#		nouns -= set(entity.split())
		entities = set(itertools.chain(*map(str.split, entities)))
		nouns -= entities

		return list(nouns)

	@classmethod
	def _number_recognition(self, text, entities):
		numbers = re.findall(r"[0-9]+", text)
		numbers = set(numbers)
		
		#for number in numbers:
		#	for entity in entities:
		#		numbers -=  set(entity.split())
		entities = set(itertools.chain(*map(str.split, entities)))
		numbers -= entities

		numerals = []
		for sentence in tagged_sentences:
			numerals += filter(lambda x: x[1] == "CD", sentence)
		numerals = [noun for (noun, tag) in numerals]
		numerals = set(numerals)

		return list(numbers | numerals)

	@classmethod
	def _entity_ranking(self, question, entities):
		if len(entities) == 0:
			return "", "", int(0)

		# Obtain frequency of entities
		entities_freq = FreqDist(entities)

		# Our answer is the sample with the greatest number of outcomes
		exact = entities_freq.max()

		# Our window is ??? TODO
		window = "ventana de texto"

		# Our score is the entity frequency
		# To be improved...
		score = int(entities_freq.freq(exact) * 1000)

		return exact, window, score

	@classmethod
	def process_answer(self, passage, question):
		q = question.text
		p = passage.text

		searched_entities = self._question_classification(q)

		entities = self._ne_recognition(p, searched_entities)
		print searched_entities
		exact, window, score = self._entity_ranking(q, entities)

		answer = Answer(passage, question, window, exact, score)

		return answer
