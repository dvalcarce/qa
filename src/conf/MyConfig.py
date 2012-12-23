# -*- coding: utf-8 -*-

import ConfigParser

from ConfigParser import Error as ConfigError

class MyConfig:

	_instance = ConfigParser.SafeConfigParser()
	_instance.read("conf/config.conf")

	@classmethod
	def get(self, section, item):
		try:
			return self._instance.get(section, item)
		except ConfigError:
			raise MyConfigException("{0}->{1} not found".format(section, item))

class MyConfigException(Exception):
	pass
