# -*- coding: utf-8 -*-

from stanford_ner.StanfordNER import StanfordNER

def clean():
	StanfordNER.disconnect_all()
	print "\nLimpiando..."
