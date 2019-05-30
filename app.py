#!/usr/bin/env python

from mysql.connector import (connection)
from mysql.connector.network import MySQLTCPSocket
import os
import re
import socket
import socks

try:
    QG_ENVVAR = os.environ['QUOTAGUARDSTATIC_URL']
except KeyError:
    try:
        QG_ENVVAR = os.environ['QUOTAGUARDSHIELD_URL']
    except KeyError:
        print("Missing QUOTAGUARDSTATIC_URL and QUOTAGUARDSHIELD_URL. Exiting")
        exit(1)

QG_PORT = 1080
QG_USER, QG_PASS, QG_HOST = re.split(r"[:@\/]", QG_ENVVAR)[3:-1]

PATCH = True

def monkey_patch_open_connection(self):
    """Open the TCP/IP connection to the MySQL server
    """
    # Get address information
    addrinfo = [None] * 5
    try:
        addrinfos = socket.getaddrinfo(self.server_host,
                                       self.server_port,
                                       0, socket.SOCK_STREAM,
                                       socket.SOL_TCP)
        # If multiple results we favor IPv4, unless IPv6 was forced.
        for info in addrinfos:
            if self.force_ipv6 and info[0] == socket.AF_INET6:
                addrinfo = info
                break
            elif info[0] == socket.AF_INET:
                addrinfo = info
                break
        if self.force_ipv6 and addrinfo[0] is None:
            raise errors.InterfaceError(
                "No IPv6 address found for {0}".format(self.server_host))
        if addrinfo[0] is None:
            addrinfo = addrinfos[0]
    except IOError as err:
        raise errors.InterfaceError(
            errno=2003, values=(self.get_address(), _strioerror(err)))
    else:
        (self._family, socktype, proto, _, sockaddr) = addrinfo

    # Instanciate the socket and connect
    try:
        self.sock = socks.socksocket(self._family, socktype, proto) #socket.socket(self._family, socktype, proto)
        self.sock.set_proxy(socks.SOCKS5, QG_HOST, QG_PORT, True, QG_USER, QG_PASS)
        self.sock.settimeout(self._connection_timeout)
        self.sock.connect(sockaddr)
    except IOError as err:
        raise errors.InterfaceError(
            errno=2003, values=(self.get_address(), _strioerror(err)))
    except Exception as err:
        raise errors.OperationalError(str(err))

# link in the monkey patch
if PATCH:
    MySQLTCPSocket.open_connection = monkey_patch_open_connection

if __name__ == "__main__":

    try:
        DB_ENVVAR = os.environ['DATABASE']
        DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME = re.split(r"[:@\/]", DB_ENVVAR)[3:]
    except KeyError:
        print("Missing DATABASE environment variable")
        exit(1)

    print("Connecting {}:{} to {} on {}:{}".format(DB_USER, DB_PASS, DB_NAME, DB_HOST, DB_PORT))

    # test the connection
    cnx = connection.MySQLConnection(user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME, port=DB_PORT)

    cursor = cnx.cursor()
    query = "SELECT SUBSTRING_INDEX(USER(),'@',-1)"

    cursor.execute(query)

    for (ip) in cursor:
        try:
            octet = "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
            match = "({}[-.]{}[-.]{}[-.]{})\.".format(octet, octet, octet, octet)
            found = re.sub(r"-", ".", re.search(match, ip[0]).group(1))

            #validate IP
            match = "({}\.{}\.{}\.{})".format(octet, octet, octet, octet)
            found = re.search(match, found).group(1)

            print("Connected via {}".format(found))
        except AttributeError:
            print("Connected, but unable to determine IP address: {}".format(ip[0]))


    cursor.close()
    cnx.close()
