#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import socket
import subprocess
import time

class StanfordParser(object):

	_instance = None

	@classmethod
	def get_instance(self):
		if self._instance is None:
			self._instance = StanfordParser()
		return self._instance


	@classmethod
	def disconnect_all(self):
		if self._instance is None:
			return
		try:
			self._instance.parser.terminate()
		except:
			logger = logging.getLogger("qa_logger")
			logger.info("parser couldn't be killed")
		else:
			self._instance.parser.kill()


	def __init__(self):
		self.launch_parser()


	def process(self, text):
		# Write to Stanford Parser stdin
		self.parser.stdin.write(text+"\n")

		# Read from Standrod Parser stdout
		buf = ""
		line = self.parser.stdout.readline()
		while line and line != "\n":
			buf += line
			line = self.parser.stdout.readline()

		return buf


	def launch_parser(self):
		classpath = os.path.join("qc", "stanford_parser", "stanford-parser.jar")+":"+os.path.join("qc", "stanford_parser", "stanford-models.jar")
		devnull = open(os.path.join("/", "dev", "null"), "a")

		self.parser = subprocess.Popen(["java", "-mx200m",
			"-cp", classpath,
			"edu.stanford.nlp.parser.lexparser.LexicalizedParser",
			"-sentences", "newline",
			os.path.join("edu", "stanford", "nlp", "models", "lexparser", "englishPCFG.ser.gz"),
			"-"],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=devnull
		)

		devnull.close()
		# Give some time to Stanford Parser to get ready
		time.sleep(1.0)


class StanfordParserError(Exception):
	pass


if __name__ == "__main__":
	os.chdir(os.pardir)
	try:
		text = raw_input("Write your text: ")
		while text and text != "":
			parser = StanfordParser.get_instance()
			processed_text = parser.process(text)
			print ">>>"
			print processed_text,
			print "<<<"
			text = raw_input("Write your text: ")
	except (EOFError, KeyboardInterrupt):
		print

