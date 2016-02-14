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

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name = 'pysshrp',
	description = 'A Python SSH/SFTP reverse proxy',
	version = '0.1',
	license = 'LGPL'
	author = 'Yamine BULACH',
	author_email = 'contact@yamine-bulach.eu',
	url = 'https://github.com/ybulach/pysshrp',
	packages = ['pysshrp'],
	scripts = ['bin/pysshrpd'],
	install_requires = ['paramiko']
)
