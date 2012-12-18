#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

class StanfordNER:

	instances = {}

	@classmethod
	def get_instance(self, host, port):
		if not self.instances.__contains__((host, port)):
			self.instances[(host, port)] = StanfordNER(host, port)
		return self.instances[(host, port)]

	@classmethod
	def disconnect_all(self):
		for instance in self.instances.itervalues():
			instance.socket.shutdown(socket.SHUT_RDWR)
			instance.socket.close()

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	def process(self, text):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))

		msg = (text + "\n").encode('utf-8')
		self.socket.sendall(msg)
		buf = self.socket.recv(len(text)*3)
		self.socket.close()

		result = map(lambda x: tuple(x.split("/")), buf.split())
		result = filter(lambda x: len(x) == 2, result)
		return result


if __name__ == "__main__":
	host = raw_input("Choose host: ")
	port = int(raw_input("Choose port: "))
	text = raw_input("Write your text: ")
	recognizer = StanfordNER.get_instance(host, port)
	processed_text = recognizer.process(text)
	print processed_text
