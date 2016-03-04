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

import grp, logging, paramiko, pwd, pysshrp, re

# A class used for configuration syntax exceptions
class ConfigurationException(Exception):
	pass

class ConfigParser:
	# Default values
	listen = '0.0.0.0:2200'
	listenAddress = ''
	listenPort = ''
	key = ''
	keyData = None
	level = 'CRITICAL'
	user = ''
	userId = 0
	group = ''
	groupId = 0
	servers = []

	def __init__(self, *args, **kwargs):
		pysshrp.common.logger.info('Loading configuration')

		log_values = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
		for key, value in kwargs.items():
			# Check types
			if (key == 'listen') and not re.search(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):\d{1,5}$', value):
				raise ConfigurationException('invalid syntax of "listen". Might be something like "0.0.0.0:2200".')
			elif (key == 'key') and not isinstance(value, str):
				raise ConfigurationException('value of "key" must be a string')
			elif (key == 'level') and not (value in log_values):
				raise ConfigurationException('value of "level" must be one of: %s' % ', '.join([i for i in log_values]))
			elif (key == 'user') and not isinstance(value, str):
				raise ConfigurationException('value of "user" must be a string')
			elif (key == 'group') and not isinstance(value, str):
				raise ConfigurationException('value of "group" must be a string')
			elif (key == 'servers') and not isinstance(value, list):
				raise ConfigurationException('value of "servers" must be an array')

			# Set value
			if key == 'servers':
				for upstream in value:
					self.servers.append(ConfigUpstream(**upstream))
			else:
				setattr(self, key, value)

		# Additional configuration
		try:
			self.listenAddress = self.listen[:self.listen.find(':')]
			self.listenPort = int(self.listen[self.listen.find(':')+1:])
		except:
			raise pysshrp.PysshrpException('invalid address or port in "listen"')

		try:
			self.keyData = paramiko.RSAKey.from_private_key_file(self.key)
		except IOError:
			raise pysshrp.PysshrpException('failed to open SSH key file "%s"' % self.key)
		except paramiko.SSHException:
			raise pysshrp.PysshrpException('invalid SSH key from "%s"' % self.key)

		logging.getLogger().setLevel(getattr(logging, self.level))

		try:
			if self.user:
				self.userId = pwd.getpwnam(self.user).pw_uid
		except:
			raise pysshrp.PysshrpException('unable to find uid of user "%s"' % self.user)

		try:
			if self.group:
				self.groupId = grp.getgrnam(self.group).gr_gid
		except:
			raise pysshrp.PysshrpException('unable to find gid of group "%s"' % self.group)

class ConfigUpstream():
	# Default values
	user = ''
	upstream_host = ''
	upstream_user = ''
	upstream_port = 22
	upstream_root_path = ''
	allow_ssh = True
	allow_sftp = True

	def __init__(self, *args, **kwargs):
		for key, value in kwargs.items():
			if (key == 'user') and not isinstance(value, str):
				raise ConfigurationException('value of "user" must be a string')
			elif (key == 'upstream_host') and not isinstance(value, str):
				raise ConfigurationException('value of "upstream_host" must be a string')
			elif (key == 'upstream_user') and not isinstance(value, str):
				raise ConfigurationException('value of "upstream_user" must be a string')
			elif (key == 'upstream_port') and not isinstance(value, int):
				raise ConfigurationException('value of "upstream_port" must be an integer')
			elif (key == 'upstream_root_path') and not isinstance(value, str):
				raise ConfigurationException('value of "upstream_root_path" must be a string')
			elif (key == 'allow_ssh') and not isinstance(value, bool):
				raise ConfigurationException('value of "allow_ssh" must be a boolean')
			elif (key == 'allow_sftp') and not isinstance(value, bool):
				raise ConfigurationException('value of "allow_sftp" must be a boolean')

			setattr(self, key, value)

		# Additional configuration
		if not self.upstream_host:
			raise PysshrpException('upstream_host is mandatory')
