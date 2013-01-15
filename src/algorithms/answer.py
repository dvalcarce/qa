# -*- coding: utf-8 -*-

import itertools
import logging
import nltk
import os
import random
import re

from Answer import Answer
from conf.MyConfig import MyConfig, MyConfigException
from lxml.etree import fromstring
from nltk.probability import FreqDist
from nltk.tree import Tree
from qc.QuestionClassifier import QuestionClassifier
from stanford_ner.StanfordNER import StanfordNER, StanfordNERError


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
            features = MyConfig.get("answer_extraction", "question_features")
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            features = "fnh"

        try:
            classifier_file = MyConfig.get("answer_extraction", "question_classifier")
            classifier_path = os.path.join("qc", features, classifier_file)
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            classifier_path = os.path.join("qc", "fhn", "qc_bayes.pkl")

        # Question classification
        return QuestionClassifier.classify(classifier_path, question, features)

    @classmethod
    def _nltk_ner(self, text, searched_entity):
        # Entity Classification
        sentences = nltk.sent_tokenize(text)
        tokenized_sentences = [nltk.word_tokenize(s) for s in sentences]
        tagged_sentences = [nltk.pos_tag(s) for s in tokenized_sentences]
        ne_chunked_sentences = nltk.batch_ne_chunk(tagged_sentences)

        # Entity Extraction
        entities = []
        all_entities = []
        for tree in ne_chunked_sentences:
            for child in tree:
                if isinstance(child, Tree):
                    entity = " ".join([word for (word, pos) in child.leaves()])
                    if child.node == searched_entity:
                        entities.append(entity)
                    all_entities.append(entity)

        if 'OTHER' in searched_entity:
            entities += self._other_recognition(tagged_sentences, all_entities)

        if 'NUMBER' in searched_entity:
            entities += self._number_recognition(text, tagged_sentences, all_entities)

        return entities

    @classmethod
    def _stanford_ner(self, text, searched_entity):
        sentences = nltk.sent_tokenize(text)
        tokenized_sentences = [nltk.word_tokenize(s) for s in sentences]
        tagged_sentences = [nltk.pos_tag(s) for s in tokenized_sentences]

        # Entity Classification
        try:
            host = MyConfig.get("answer_extraction", "stanford_host")
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            host = "localhost"

        try:
            port = int(MyConfig.get("answer_extraction", "stanford_port"))
        except MyConfigException as e:
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))
            port = 1234

        try:
            recognizer = StanfordNER.get_instance(host, port)
            text = recognizer.process(text)
        except StanfordNERError:
            logger = logging.getLogger("qa_logger")
            logger.warning("Stanford NER not available, using NLTK NER")
            return self._nltk_ner(text, searched_entity)

        # XML Parsing
        text = "<xml>" + text.replace("&", "") + "</xml>"
        try:
            tree = fromstring(text)
        except:
            return []

        # Entity Extraction
        entities = []
        all_entities = []
        for element in tree.iterchildren():
            if element is None:
                continue
            if element.tag == searched_entity:
                entities.append(element.text)
            all_entities.append(element.text)

        if 'OTHER' in searched_entity:
            entities += self._other_recognition(tagged_sentences, all_entities)

        if 'NUMBER' in searched_entity:
            entities += self._number_recognition(text, tagged_sentences, all_entities)

        return entities

    @classmethod
    def _other_recognition(self, tagged_sentences, all_entities):
        # Nouns retrieval
        nouns = []
        for sentence in tagged_sentences:
            nouns += filter(lambda x: x[1] == "NN", sentence)
        nouns = [noun for (noun, tag) in nouns]
        nouns = set(nouns)

        # Nouns filtering
        # Remove all entities that are nouns
        all_entities = set(itertools.chain(*map(str.split, all_entities)))
        nouns -= all_entities

        return list(nouns)

    @classmethod
    def _number_recognition(self, text, tagged_sentences, all_entities):
        # Numbers retrieval
        numbers = re.findall(r"[0-9]+", text)
        numbers = set(numbers)

        # Number filtering
        # Remove all entities that are numbers
        all_entities = set(itertools.chain(*map(str.split, all_entities)))
        numbers -= all_entities

        # Numerals retrieval
        # CD = numeral, cardinal
        # JJ = numeral, ordinal
        numerals = []
        for sentence in tagged_sentences:
            numerals += filter(lambda x: x[1] == "CD" or x[1] == "JJ", sentence)
        numerals = [noun for (noun, tag) in numerals]
        numerals = set(numerals)

        return list(numbers | numerals)

    @classmethod
    def _filter_entities(self, entities, question):
        words = nltk.word_tokenize(question.lower())
        return [entity for entity in entities if entity.lower() not in words]

    @classmethod
    def _entity_ranking(self, question, entities):
        if len(entities) == 0:
            return "", "", int(0)

        # Obtain frequency of entities
        entities_freq = FreqDist(entities)

        # Our answer is the sample with the greatest number of outcomes
        exact = entities_freq.max()

        # Our window is empty because this algorithm generates exact answers
        window = ""

        # Our score is the entity frequency
        score = int(entities_freq.freq(exact) * 1000)

        return exact, window, score

    @classmethod
    def process_answer(self, passage, question):
        q = question.text
        p = passage.text

        searched_entity = self._question_classification(q)

        try:
            ner_algorithm = MyConfig.get("answer_extraction", "ner")
        except MyConfigException as e:
            ner_algorithm = "stanford"
            logger = logging.getLogger("qa_logger")
            logger.warning(str(e))

        if ner_algorithm == "nltk":
            entities = self._nltk_ner(p, searched_entity)
        else:
            entities = self._stanford_ner(p, searched_entity)

        entities = self._filter_entities(entities, q)

        exact, window, score = self._entity_ranking(q, entities)

        answer = Answer(passage, question, window, exact, score)

        return answer
