# -*- coding: utf-8 -*-

from stanford_ner.StanfordNER import StanfordNER

def clean():
	StanfordNER.disconnect_all()
	StanfordNER.stop_servlet()
	print "\nLimpiando..."
