# -*- coding: utf-8 -*-

import ConfigParser

class MyConfig:

	_instance = ConfigParser.ConfigParser()
	_instance.read("config.cfg")

	@classmethod
	def get(self, section, item):
		return self._instance.get(section, item)

