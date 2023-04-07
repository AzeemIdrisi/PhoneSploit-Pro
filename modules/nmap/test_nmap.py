#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nmap
import datetime
import os

from nose.tools import assert_equals
from nose.tools import raises
from nose import with_setup

from multiprocessing import Value

"""
test_nmap.py - tests cases for python-nmap

Source code : https://bitbucket.org/xael/python-nmap

Author :

* Alexandre Norman - norman at xael.org

Contributors:

* Steve 'Ashcrow' Milner - steve at gnulinux.net
* Brian Bustin - brian at bustin.us
* old.schepperhand
* Johan Lundberg
* Thomas D. maaaaz
* Robert Bost
 
Licence : GPL v3 or any later version


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""

##########################################################################################

"""
This plugin provides ``--pdb`` and ``--pdb-failures`` options. The ``--pdb``
option will drop the test runner into pdb when it encounters an error. To
drop into pdb on failure, use ``--pdb-failures``.
"""

import pdb
from nose.plugins.base import Plugin


class Pdb(Plugin):
    """
    Provides --pdb and --pdb-failures options that cause the test runner to
    drop into pdb if it encounters an error or failure, respectively.
    """

    enabled_for_errors = False
    enabled_for_failures = False
    score = 5  # run last, among builtins

    def options(self, parser, env):
        """Register commandline options.
        """
        parser.add_option(
            "--pdb",
            action="store_true",
            dest="debugBoth",
            default=env.get("NOSE_PDB", False),
            help="Drop into debugger on failures or errors",
        )
        parser.add_option(
            "--pdb-failures",
            action="store_true",
            dest="debugFailures",
            default=env.get("NOSE_PDB_FAILURES", False),
            help="Drop into debugger on failures",
        )
        parser.add_option(
            "--pdb-errors",
            action="store_true",
            dest="debugErrors",
            default=env.get("NOSE_PDB_ERRORS", False),
            help="Drop into debugger on errors",
        )

    def configure(self, options, conf):
        """Configure which kinds of exceptions trigger plugin.
        """
        self.conf = conf
        self.enabled_for_errors = options.debugErrors or options.debugBoth
        self.enabled_for_failures = options.debugFailures or options.debugBoth
        self.enabled = self.enabled_for_failures or self.enabled_for_errors

    def addError(self, test, err):
        """Enter pdb if configured to debug errors.
        """
        if not self.enabled_for_errors:
            return
        self.debug(err)

    def addFailure(self, test, err):
        """Enter pdb if configured to debug failures.
        """
        if not self.enabled_for_failures:
            return
        self.debug(err)

    def debug(self, err):
        import sys  # FIXME why is this import here?

        ec, ev, tb = err
        stdout = sys.stdout
        sys.stdout = sys.__stdout__
        try:
            pdb.post_mortem(tb)
        finally:
            sys.stdout = stdout


##########################################################################################


def setup_module():
    global nm
    nm = nmap.PortScanner()


@raises(nmap.PortScannerError)
def test_wrong_args():
    nm.scan(arguments="-wrongargs")


def test_host_scan_error():
    assert (
        "error" in nm.scan("noserver.example.com", arguments="-sP")["nmap"]["scaninfo"]
    )


def xmlfile_read_setup():
    nm.analyse_nmap_xml_scan(open("scanme_output.xml").read())


@with_setup(xmlfile_read_setup)
def test_command_line():
    try:
        global NMAP_XML_VERSION
        NMAP_XML_VERSION = os.environ["NMAP_XML_VERSION"]
    except Exception:
        raise ValueError("Set env NMAP_XML_VERSION")

    assert_equals(
        nm.command_line(),
        "./nmap-{0}/nmap -sV -oX scanme_output-{0}.xml scanme.nmap.org".format(
            NMAP_XML_VERSION
        ),
    )


@with_setup(xmlfile_read_setup)
def test_scan_info():
    assert "tcp" in nm.scaninfo()
    assert "method" in nm.scaninfo()["tcp"]
    assert_equals("connect", nm.scaninfo()["tcp"]["method"])
    assert "services" in nm.scaninfo()["tcp"]


@with_setup(xmlfile_read_setup)
def test_all_hosts():
    assert_equals(["45.33.32.156"], nm.all_hosts())


@with_setup(xmlfile_read_setup)
def test_host():
    assert_equals("scanme.nmap.org", nm["45.33.32.156"].hostname())
    assert {"name": "scanme.nmap.org", "type": "user"} in nm["45.33.32.156"].hostnames()
    assert_equals("up", nm["45.33.32.156"].state())
    assert_equals(["tcp"], nm["45.33.32.156"].all_protocols())


def test_host_no_hostname():
    # Covers bug : https://bitbucket.org/xael/python-nmap/issues/7/error-with-hostname
    nm.scan("127.0.0.2")
    assert_equals("", nm["127.0.0.2"].hostname())


@with_setup(xmlfile_read_setup)
def test_ports():
    ports = list(nm["45.33.32.156"]["tcp"].keys())
    ports.sort()
    assert_equals([22, 25, 80, 139, 445, 9929, 31337], ports)
    assert nm["45.33.32.156"].has_tcp(22)
    assert nm["45.33.32.156"].has_tcp(23) == False
    assert "conf" in list(nm["45.33.32.156"]["tcp"][22])
    assert "cpe" in list(nm["45.33.32.156"]["tcp"][22])
    assert "name" in list(nm["45.33.32.156"]["tcp"][22])
    assert "product" in list(nm["45.33.32.156"]["tcp"][22])
    assert "reason" in list(nm["45.33.32.156"]["tcp"][22])
    assert "state" in list(nm["45.33.32.156"]["tcp"][22])
    assert "version" in list(nm["45.33.32.156"]["tcp"][22])

    assert "10" in nm["45.33.32.156"]["tcp"][22]["conf"]
    global NMAP_XML_VERSION
    if NMAP_XML_VERSION == "6.40":
        assert_equals("", nm["45.33.32.156"]["tcp"][22]["cpe"])
        assert_equals("", nm["45.33.32.156"]["tcp"][22]["product"])
        assert_equals("", nm["45.33.32.156"]["tcp"][22]["version"])
    else:
        assert "cpe:/o:linux:linux_kernel" in nm["45.33.32.156"]["tcp"][22]["cpe"]
        assert "OpenSSH" in nm["45.33.32.156"]["tcp"][22]["product"]
        assert "6.6.1p1 Ubuntu 2ubuntu2.13" in nm["45.33.32.156"]["tcp"][22]["version"]

    assert "ssh" in nm["45.33.32.156"]["tcp"][22]["name"]
    assert "syn-ack" in nm["45.33.32.156"]["tcp"][22]["reason"]
    assert "open" in nm["45.33.32.156"]["tcp"][22]["state"]

    assert_equals(nm["45.33.32.156"]["tcp"][22], nm["45.33.32.156"].tcp(22))


@with_setup(xmlfile_read_setup)
def test_listscan():
    assert_equals("1", nm.scanstats()["uphosts"])
    assert_equals("0", nm.scanstats()["downhosts"])
    assert_equals("1", nm.scanstats()["totalhosts"])
    assert "timestr" in nm.scanstats().keys()
    assert "elapsed" in nm.scanstats().keys()


@with_setup(xmlfile_read_setup)
def test_csv_output():
    assert_equals(
        "host;hostname;hostname_type;protocol;port;name;state;product;extrainfo;reason;version;conf;cpe",
        nm.csv().split("\n")[0].strip(),
    )

    global NMAP_XML_VERSION
    result = None
    if NMAP_XML_VERSION == "6.40":
        result = "45.33.32.156;scanme.nmap.org;user;tcp;22;ssh;open;;protocol 2.0;syn-ack;;10;"

    elif NMAP_XML_VERSION == "7.01":
        result = '45.33.32.156;scanme.nmap.org;user;tcp;22;ssh;open;OpenSSH;"Ubuntu Linux; protocol 2.0";syn-ack;6.6.1p1 Ubuntu 2ubuntu2.13;10;cpe:/o:linux:linux_kernel'

    elif NMAP_XML_VERSION == "7.70":
        result = '45.33.32.156;scanme.nmap.org;user;tcp;22;ssh;open;OpenSSH;"Ubuntu Linux; protocol 2.0";syn-ack;6.6.1p1 Ubuntu 2ubuntu2.13;10;cpe:/o:linux:linux_kernel'

    elif NMAP_XML_VERSION == "7.91":
        result = '45.33.32.156;scanme.nmap.org;user;tcp;22;ssh;open;OpenSSH;"Ubuntu Linux; protocol 2.0";syn-ack;6.6.1p1 Ubuntu 2ubuntu2.13;10;cpe:/o:linux:linux_kernel'

    if result is not None:
        assert_equals(result, nm.csv().split("\n")[1].strip())


def test_listscan():
    assert 0 < len(nm.listscan("192.168.1.0/30"))
    assert_equals(
        ["127.0.0.0", "127.0.0.1", "127.0.0.2", "127.0.0.3"],
        nm.listscan("localhost/30"),
    )


def test_ipv6():
    if os.getuid() == 0:
        r = nm.scan("127.0.0.1", arguments="-6")
    else:
        r = nm.scan("127.0.0.1", arguments="-6", sudo=True)


def test_ipv4_async():
    global FLAG
    FLAG = Value("i", 0)
    nma = nmap.PortScannerAsync()

    def callback_result(host, scan_result):
        global FLAG
        FLAG.value = 1

    nma.scan(hosts="127.0.0.1", arguments="-p 22 -Pn", callback=callback_result)

    while nma.still_scanning():
        nma.wait(2)

    assert_equals(FLAG.value, 1)


def test_ipv6_async():
    global FLAG_ipv6
    FLAG_ipv6 = Value("i", 0)
    nma_ipv6 = nmap.PortScannerAsync()

    def callback_result(host, scan_result):
        global FLAG_ipv6
        FLAG_ipv6.value = 1

    nma_ipv6.scan(hosts="::1", arguments="-6 -p 22 -Pn", callback=callback_result)

    while nma_ipv6.still_scanning():
        nma_ipv6.wait(2)

    assert_equals(FLAG_ipv6.value, 1)


def scan_localhost_sudo_arg_O():
    lastnm = nm.get_nmap_last_output()

    if len(lastnm) > 0:
        try:
            nm.analyse_nmap_xml_scan(lastnm)
        except Exception:
            pass
        else:
            if nm.command_line() == "nmap -oX - -O 127.0.0.1":
                return

    if os.getuid() == 0:
        nm.scan("127.0.0.1", arguments="-O")
    else:
        nm.scan("127.0.0.1", arguments="-O", sudo=True)


@with_setup(scan_localhost_sudo_arg_O)
def test_sudo():
    assert "osmatch" in nm["127.0.0.1"]
    assert len(nm["127.0.0.1"]["osmatch"][0]["osclass"]) > 0
    assert_equals("Linux", nm["127.0.0.1"]["osmatch"][0]["osclass"][0]["vendor"])


@with_setup(scan_localhost_sudo_arg_O)
def test_parsing_osmap_osclass_and_others():
    # nosetests -v -s nmap/test_nmap.py:test_parsing_osmap_osclass_and_others
    assert "osmatch" in nm["127.0.0.1"]
    assert_equals(nm["127.0.0.1"]["osmatch"][0]["name"], "Linux 2.6.32")

    assert "accuracy" in nm["127.0.0.1"]["osmatch"][0]
    assert "line" in nm["127.0.0.1"]["osmatch"][0]

    assert "osclass" in nm["127.0.0.1"]["osmatch"][0]
    assert_equals(nm["127.0.0.1"]["osmatch"][0]["osclass"][0]["vendor"], "Linux")

    assert "type" in nm["127.0.0.1"]["osmatch"][0]["osclass"][0]
    assert "osfamily" in nm["127.0.0.1"]["osmatch"][0]["osclass"][0]
    assert "osgen" in nm["127.0.0.1"]["osmatch"][0]["osclass"][0]
    assert "accuracy" in nm["127.0.0.1"]["osmatch"][0]["osclass"][0]


@with_setup(scan_localhost_sudo_arg_O)
def test_all_protocols():
    assert "addresses" not in nm["127.0.0.1"].all_protocols()
    assert "hostnames" not in nm["127.0.0.1"].all_protocols()
    assert "status" not in nm["127.0.0.1"].all_protocols()
    assert "vendor" not in nm["127.0.0.1"].all_protocols()
    assert "osclass" not in nm["127.0.0.1"].all_protocols()
    assert "osmatch" not in nm["127.0.0.1"].all_protocols()
    assert "uptime" not in nm["127.0.0.1"].all_protocols()
    assert "portused" not in nm["127.0.0.1"].all_protocols()
    assert "tcp" in nm["127.0.0.1"].all_protocols()


def xmlfile_read_setup_multiple_osmatch():
    nm.analyse_nmap_xml_scan(open("osmatch_output.xml").read())


@with_setup(xmlfile_read_setup_multiple_osmatch)
def test_multipe_osmatch():
    assert "osmatch" in nm["127.0.0.1"]
    assert "portused" in nm["127.0.0.1"]

    for osm in nm["127.0.0.1"]["osmatch"]:
        assert "accuracy" in osm
        assert "line" in osm
        assert "name" in osm
        assert "osclass" in osm
        assert "accuracy" in osm["osclass"][0]
        assert "cpe" in osm["osclass"][0]
        assert "osfamily" in osm["osclass"][0]
        assert "osgen" in osm["osclass"][0]
        assert "type" in osm["osclass"][0]
        assert "vendor" in osm["osclass"][0]


@with_setup(xmlfile_read_setup)
def test_convert_nmap_output_to_encoding():
    a = nm.analyse_nmap_xml_scan(open("scanme_output.xml").read())
    out = nmap.convert_nmap_output_to_encoding(a, code="ascii")
    assert out["scan"]["45.33.32.156"]["addresses"]["ipv4"] == b"45.33.32.156"


# def test_host_and_port_as_unicode():
#     # nosetests -x -s nmap/test_nmap.py:test_port_as_unicode
#     # Covers bug : https://bitbucket.org/xael/python-nmap/issues/9/can-not-pass-ports-with-unicode-string-at
#     nma = nm.scan(hosts=u'127.0.0.1', ports=u'22')
#     assert_equals(nma['nmap']['scaninfo']['error'], '')


def test_WARNING_case_sensitive():
    nm.scan("localhost", arguments="-S 127.0.0.1")
    assert "warning" in nm.scaninfo()
    assert "WARNING" in nm.scaninfo()["warning"][0]


def test_scan_progressive():
    nmp = nmap.PortScannerAsync()

    def callback(host, scan_data):
        assert host is not None

    nmp.scan(hosts="127.0.0.1", arguments="-sV", callback=callback)
    nmp.wait()


def test_sudo_encoding__T24():
    """
    When using "sudo=True" like this 'nm.scan(hosts=ip_range, arguments="-sP", sudo = True)' 
    i got a UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 9: ordinal not in range(128). 
    But if sudo is false all thing work nice. 
    """
    r = nm.scan("192.168.1.1/24", arguments="-sP", sudo=True)
