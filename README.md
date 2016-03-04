# pysshrp

## Presentation
`pysshrp` is a Python daemon (`pysshrpd` script) providing SSH and SFTP reverse-proxying, as seen with nginx/apache2 mod_proxy, etc. It works as a transparent proxy to allow **downstreams** to connect to **upstreams** depending on the provided **user**. Here is the classic schema:

	  client 	---------> pysshrpd --------> remote server
	downstream 			pysshrp module			upstream
						paramiko module

It uses [Paramiko](https://github.com/paramiko/paramiko) to handle SSH connections with downstream and upstream.

## Installation
This commands will quickly install `pysshrp` and associated `pysshrpd` daemon (tested on Debian 8, as **root**):

	git clone https://github.com/ybulach/pysshrp.git
	cd pysshrp/
	python setup.py install
	useradd pysshrp
	mkdir /etc/pysshrp
	cp docs/config_sample.py /etc/pysshrp/config.py
	openssl genrsa 2048 > /etc/pysshrp/server.key
	cp docs/systemd_sample.service /etc/systemd/system/
	systemctl daemon-reload

This will create a configuration directory in `/etc/pysshrp` with a server key (`server.key`), a sample configuration (`config.py`) and a dedicated user/group (`pysshrp`) to run the daemon threads as. A **systemd** service is also installed.

Once the `/etc/pysshrp/config.py` file has been edited to suit your needs (see **Configuration** below), the service can be started with:

	systemctl start pysshrpd

and logs can be seens with:

	systemctl status pysshrpd

## Configuration
A sample configuration file is available in `docs/config_sample.py`. It is actually a Python script and requires Python syntax.

### Global configuration
The below variables take care of the configuration of the `pysshrpd` daemon itself.

- `listen`: bind to an address/port
- `level`: define the log level (using values from Python's logging module: https://docs.python.org/2/library/logging.html#levels)
- `key`: path to an SSH private key to use for the server thread (must be created manually)
- `user`: the user to run client thread as (only works when server thread runs as root)
- `group`: the group to run client thread as (only works when server thread runs as root)

### Upstreams configuration
Upstream servers configuration is made in `servers` (must be an **array**). Each upstream server may define some of the below parameters (in a **dict**).

- `user`: **MANDATORY** a string/regex for the incoming login:
- `upstream_host`: **MANDATORY** the address of the upstream SSH server
- `upstream_user`: set another login for the upstream server
- `upstream_port`: the port of the upstream server
- `upstream_root_path`: the base path for SFTP connections (client will not be able to go in a parent directory)

Regexes allow extractring patterns, to use them in `upstream_*` variables. Regexes are handled only when the values start with `^`. For example:

	{
		'user': r'^web(?P<srv_id>\d+)$'
		'upstream_host': 'web\g<srv_id>.example.lan'
	}
