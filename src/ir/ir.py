#!/usr/bin/env python
import nltk
import pprint
from pattern.web import Google, Bing, Wikipedia
#from Google import Google

def get_search_engines():
	lang = 'en'
	google_license = 'AIzaSyAZv8KvLW0f4PKQlO4jXQii9s9IuW4G1UE'
	bing_license = 'hMdI+RiXdHkJ694ZKjS9hDtLc+kjKc2C0y3XmJQYTag='
	throttle = 0.5

	return [
		Google(google_license, throttle, lang),
		Bing(bing_license, throttle, lang)
	]


def search(query):
	search_engines = get_search_engines()
	
	res = []
	for engine in search_engines:
		res += engine.search(query)

	return res

if __name__ == '__main__':
	query = raw_input("Dame una query: ")

	print "Buscando %s" % query

	result = search(query)

	for r in result:
		pprint.pprint(r)
		print r.description
