#!/usr/bin/env python

import nltk
from nltk.corpus import stopwords

def formulate_query(question):
	question = question.lower()
	token_list = question.split()

	stopwords_list = stopwords.words('english')
	final_list = [w for w in token_list if not (w in stopwords_list)] 

	return " ".join(final_list)

if __name__ == '__main__':
	question = raw_input("Write your question: ")
	query = formulate_query(question)
	print query

