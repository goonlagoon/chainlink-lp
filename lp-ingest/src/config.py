#!/usr/bin/python
from configparser import ConfigParser


def appconfig(filename='/configs/liquidity_pool.ini', section='app'):
	# create a parser
	parser = ConfigParser()
	# read config file
	parser.read(filename)

	# get section, default to app
	app = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			app[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))

	return app