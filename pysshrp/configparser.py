#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pysshrp.
#
# pysshrp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pysshrp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pysshrp.  If not, see <http://www.gnu.org/licenses/>.

import logging, paramiko

class ConfigParser:
	# Default values
	listen = 2200
	key = ''
	level = logging.CRITICAL
	servers = []

	def __init__(self, *args, **kwargs):
		log_values = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
		for key, value in kwargs.items():
			# Check types
			if (key == 'listen') and not isinstance(value, int):
				raise Exception('value of "listen" must be an integer')
			elif (key == 'key') and not isinstance(value, str):
				raise Exception('value of "key" must be a string')
			elif (key == 'level') and not (value in log_values):
				raise Exception('value of "level" must be one of: %s' % ', '.join([i for i in log_values]))
			elif (key == 'servers') and not isinstance(value, list):
				raise Exception('value of "servers" must be an array')

			# Set value
			if key == 'servers':
				for upstream in value:
					self.servers.append(ConfigUpstream(**upstream))
			else:
				setattr(self, key, value)

		# Additional configuration
		logging.basicConfig(level=getattr(logging, self.level))

		try:
			self.key = paramiko.RSAKey.from_private_key_file(self.key)
		except IOError:
			raise pysshrp.PysshrpException('failed to open SSH key file "%s"' % self.key)
		except paramiko.SSHException:
			raise pysshrp.PysshrpException('invalid SSH key from "%s"' % self.key)

class ConfigUpstream():
	# Default values
	user = ''
	upstream_host = ''
	upstream_user = ''
	upstream_port = 22

	def __init__(self, *args, **kwargs):
		for key, value in kwargs.items():
			if (key == 'user') and not isinstance(value, str):
				raise Exception('value of "user" must be a string')
			elif (key == 'upstream_host') and not isinstance(value, str):
				raise Exception('value of "upstream_host" must be a string')
			elif (key == 'upstream_user') and not isinstance(value, str):
				raise Exception('value of "upstream_user" must be a string')
			elif (key == 'upstream_port') and not isinstance(value, int):
				raise Exception('value of "upstream_port" must be an integer')

			setattr(self, key, value)

		# Additional configuration
		if not self.upstream_host:
			raise PysshrpException('upstream_host is mandatory')