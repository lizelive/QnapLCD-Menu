import socket
import toml

from ..plugin import Plugin

class Hostname(Plugin):
    def report(self):
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        

        socket.gethostbyname(hostname)
        socket.get


        toml.dumps()
        