#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name = 'pysshrp',
	description = 'A Python SSH/SFTP reverse proxy',
	version = '0.1',
	author = 'Yamine BULACH',
	author_email = 'contact@yamine-bulach.eu',
	url = 'https://github.com/ybulach/pysshrp',
	packages = ['pysshrp'],
	scripts = ['bin/pysshrpd'],
	install_requires = ['paramiko']
)
