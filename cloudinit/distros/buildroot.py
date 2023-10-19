# Copyright (C) 2016 Matt Dainty
# Copyright (C) 2020 Dermot Bradley
# Copyright (C) 2023 IBM Corporation
#
# Author: Matt Dainty <matt@bodgit-n-scarper.com>
# Author: Dermot Bradley <dermot_bradley@yahoo.com>
# Author: Andrew Donnellan <ajd@linux.ibm.com>
#
# This file is part of cloud-init. See LICENSE file for license information.

import logging
import os

from cloudinit import distros, helpers, subp, util
from cloudinit.distros.parsers.hostname import HostnameConf
from cloudinit.settings import PER_INSTANCE

LOG = logging.getLogger(__name__)


class Distro(distros.Distro):
    # XXX: We assume use of systemd-networkd
    renderer_configs = {
        "networkd": {}
    }

    def __init__(self, name, cfg, paths):
        distros.Distro.__init__(self, name, cfg, paths)
        # This will be used to restrict certain
        # calls from repeatly happening (when they
        # should only happen say once per instance...)
        self.default_locale = "C.UTF-8"
        self.osfamily = "buildroot"

    def get_locale(self):
        """Return the default locale if set, else use default locale"""

        # read system locale value
        if not self.system_locale:
            self.system_locale = read_system_locale()

        # Return system_locale setting if valid, else use default locale
        return (
            self.system_locale if self.system_locale else self.default_locale
        )

    def install_packages(self, pkglist: distros.PackageList):
        raise NotImplementedError

    def _write_hostname(self, hostname, filename):
        conf = None
        try:
            # Try to update the previous one
            # so lets see if we can read it first.
            conf = self._read_hostname_conf(filename)
        except IOError:
            create_hostname_file = util.get_cfg_option_bool(
                self._cfg, "create_hostname_file", True
            )
            if create_hostname_file:
                pass
            else:
                return
        if not conf:
            conf = HostnameConf("")
        conf.set_hostname(hostname)
        util.write_file(filename, str(conf), 0o644)

    def _read_system_hostname(self):
        sys_hostname = self._read_hostname(self.hostname_conf_fn)
        return (self.hostname_conf_fn, sys_hostname)

    def _read_hostname_conf(self, filename):
        conf = HostnameConf(util.load_file(filename))
        conf.parse()
        return conf

    def _read_hostname(self, filename, default=None):
        hostname = None
        try:
            conf = self._read_hostname_conf(filename)
            hostname = conf.hostname
        except IOError:
            pass
        if not hostname:
            return default
        return hostname

    def _get_localhost_ip(self):
        return "127.0.1.1"

    def set_timezone(self, tz):
        distros.set_etc_timezone(tz=tz, tz_file=self._find_tz_file(tz))

    def package_command(self, command, args=None, pkgs=None):
        raise NotImplementedError

    def update_package_sources(self):
        raise NotImplementedError

    @property
    def preferred_ntp_clients(self):
        """Allow distro to determine the preferred ntp client list"""
        if not self._preferred_ntp_clients:
            self._preferred_ntp_clients = ["chrony", "ntp"]

        return self._preferred_ntp_clients

    @staticmethod
    def uses_systemd():
        """
        We assume that systemd is being used.
        
         TODO: maybe you don't need this at all, the default should detect it?
        """
        return True

    def apply_locale(self, locale, out_fn=None):
        """
        XXX: we just return here, don't do anything
        """
        return

def read_system_locale(sys_path=None, keyname="LANG"):
    """XXX: be useless here"""
    return ""
