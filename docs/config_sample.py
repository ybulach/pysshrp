# This configuration file uses Python syntax

# Bind to this port
listen = 2200

# Define the log level (using values from Python's logging module)
# https://docs.python.org/2/library/logging.html#levels
level = 'INFO'

# Path to an SSH private key to use for the server thread
key = '/path/to/server.key'

# Define the servers to serve via pysshrp
servers = [
	# Each server may define some of this parameters:
	#
	# {
	# 	'user': '',				# a string/regex for the incoming login
	#
	# 	'upstream_host': '',	# the address of the upstream SSH server
	# 	'upstream_user': ''		# set another login for the upstream server
	# 	'upstream_port': 0		# the port of the upstream server
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
		'upstream_user': 'root'
	}
]