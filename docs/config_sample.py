# This configuration file uses Python syntax

# Bind to this address/port
listen = '0.0.0.0:2200'

# Define the log level (using values from Python's logging module)
# https://docs.python.org/2/library/logging.html#levels
level = 'INFO'

# Path to an SSH private key to use for the server thread
key = '/etc/pysshrp/server.key'

# The user/group to run client thread as (when server thread runned as root)
user = "pysshrp"
group = "pysshrp"

# Define the servers to serve via pysshrp
servers = [
	# Each server may define some of this parameters (here with the default values):
	#
	# {
	# 	'user': '',					# a string/regex for the incoming login
	#
	# 	'upstream_host': '',		# the address of the upstream SSH server
	# 	'upstream_user': ''			# set another login for the upstream server
	# 	'upstream_port': 22,		# the port of the upstream server
	# 	'upstream_root_path': '',	# the base path for SFTP connections
	#
	# 	'allow_ssh': True,			# SSH access permission (allowed/denied)
	# 	'allow_sft': True			# SFTP access permission (allowed/denied)
	# }
	#
	# Regex allows extractring patterns, to use them in upstream_* variables
	# For example:
	# {
	# 	'user': r'^web(?P<srv_id>\d+)$'
	# 	'upstream_host': 'web\g<srv_id>.example.lan'
	# }

	# Connection from a specific user
	{
		'user': 'foo',
		'upstream_host': 'foo.example.lan'
	},

	# Redirect multiple users with a regex
	{
		'user': r'^web(?P<srv_id>\d+)$',
		'upstream_host': 'web\g<srv_id>.example.lan',
		'upstream_user': 'root',
		'upstream_root_path': '/var/www',
		'allow_ssh': False
	}
]
