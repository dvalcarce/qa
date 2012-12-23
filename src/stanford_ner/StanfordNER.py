#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import subprocess
import os
import time

class StanfordNER:

	_instances = {}

	@classmethod
	def get_instance(self, host, port):
		if not self._instances.__contains__((host, port)):
			self._instances[(host, port)] = StanfordNER(host, port)
		return self._instances[(host, port)]


	@classmethod
	def disconnect_all(self):
		for _instance in self.instances.itervalues():
			try:
				_instance.socket.shutdown(socket.SHUT_RDWR)
				_instance.socket.close()
			except:
				logger = logging.getLogger("qa_logger")
				logger.warning("error closing socket " + str(socket))
			try:
				_instance.servlet.kill()
			except:
				pass


	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


	def process(self, text):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.connect((self.host, self.port))
		except socket.error as e:
			self.launch_servlet(self.host, self.port)
			logger = logging.getLogger("qa_logger")
			logger.info("stanford servlet manually launched")
			time.sleep(2.0)
			self.socket.connect((self.host, self.port))

		try:
			msg = (text + "\n").encode('utf-8')
			self.socket.sendall(msg)
			buf = self.socket.recv(len(text)*3)
			self.socket.close()

			result = map(lambda x: tuple(x.split("/")), buf.split())
			result = filter(lambda x: len(x) == 2, result)
		except socket.error:
			return ""

		return result


	def launch_servlet(self, host, port):
		if self.host != "localhost" \
			and self.host != socket.gethostbyname("localhost") \
			and self.host != socket.gethostbyname(socket.gethostname()):
			raise StanfordNERError("Stanford servlet not found")

		dev_null = open(os.path.join("/", "dev", "null"), "w")
		log = open(os.path.join("conf", "config.conf"))

		self.servlet = subprocess.Popen(["java", "-mx700m",
			"-cp", os.path.join("stanford_ner", "stanford-ner.jar"),
			"edu.stanford.nlp.ie.NERServer",
			"-loadClassifier",
			os.path.join("stanford_ner", "classifiers", "english.muc.7class.distsim.crf.ser.gz"),
			"-port", str(port)],
			stdout=dev_null,
			stderr=log
			)

		dev_null.close()
		log.close()



class StanfordNERError(Exception):
	pass

if __name__ == "__main__":
	host = raw_input("Choose host: ")
	port = int(raw_input("Choose port: "))
	text = raw_input("Write your text: ")
	os.chdir(os.pardir)
	recognizer = StanfordNER.get_instance(host, port)
	processed_text = recognizer.process(text)
	print processed_text
