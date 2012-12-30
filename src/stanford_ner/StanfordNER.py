#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import socket
import subprocess
import time

class StanfordNER(object):

	_instances = {}

	@classmethod
	def get_instance(self, host, port):
		if not self._instances.__contains__((host, port)):
			self._instances[(host, port)] = StanfordNER(host, port)
		return self._instances[(host, port)]


	@classmethod
	def disconnect_all(self):
		for instance in self._instances.itervalues():
			try:
				instance.servlet.terminate()
			except:
				logger = logging.getLogger("qa_logger")
				logger.info("Servlet couldn't be killed")
			else:
				instance.servlet.kill()


	def __init__(self, host, port):
		self.host = host
		self.port = port


	def connect(self):
		try:
			return socket.create_connection((self.host, self.port))
		except socket.error as e:
			self.launch_servlet(self.host, self.port)
			logger = logging.getLogger("qa_logger")
			logger.debug("Stanford servlet automatically launched")

		try:
			return socket.create_connection((self.host, self.port))
		except socket.error as e:
			raise StanfordNERError("Stanford servlet not found")


	def disconnect(self):
		try:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
		except socket.error:
			logger = logging.getLogger("qa_logger")
			logger.warning("error closing socket " + str(socket))


	def process(self, text):
		self.socket = self.connect()

		try:
			msg = (text + "\n").encode('utf-8')
			self.socket.sendall(msg)
			buf = self.socket.recv(len(text)*3)
			self.socket.close()
		except socket.error:
			logger = logging.getLogger("qa_logger")
			logger.warning("error with socket " + str(socket.getsockname()))
			return ""

		return buf


	def launch_servlet(self, host, port):
		if self.host != "localhost" \
			and self.host != socket.gethostbyname("localhost") \
			and self.host != socket.gethostbyname(socket.gethostname()):
			raise StanfordNERError("Stanford servlet cannot be automatically launched")

		dev_null = open(os.path.join("/", "dev", "null"), "w")
		log = open(os.path.join("log", "stanford_ner.log"), "a")

		self.servlet = subprocess.Popen(["java", "-mx500m",
			"-cp", os.path.join("stanford_ner", "stanford-ner.jar"),
			"edu.stanford.nlp.ie.NERServer",
			"-loadClassifier",
			os.path.join("stanford_ner", "classifiers", "english.muc.7class.distsim.crf.ser.gz"),
			"-port", str(port),
			"-outputFormat", "inlineXML"],
			stdout=log,
			stderr=log
		)

		dev_null.close()
		log.close()

		# Give some time to Stanford NER Servlet to get ready
		time.sleep(5.0)


class StanfordNERError(Exception):
	pass

if __name__ == "__main__":
	os.chdir(os.pardir)
	host = raw_input("Choose host: ")
	port = int(raw_input("Choose port: "))
	text = raw_input("Write your text: ")
	recognizer = StanfordNER.get_instance(host, port)
	processed_text = recognizer.process(text)
	print processed_text
