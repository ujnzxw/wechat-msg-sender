#!/usr/bin/env python
#======================================================
# Title             : xzcfg.py
# Description       : config file parser
# Author            : ujnzxw
# Date              : 2016-07-16
# Version           : 0.0.1
# Usage             : python xzcfg.py
# Notes:            :
#======================================================

import ConfigParser
from xzlog import xzlog

__XZ_CONFIG_FILE__ = '/root/bihu24h/config.ini'
__XZ_LOG_FILE__    = '/root/logs/wechat.log'

def Singleton(cls):
    _instance = {}
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
    return _singleton

@Singleton
class xzCfg(object):

    # Init attribute
    def __init__(self, cfgfile = __XZ_CONFIG_FILE__):
        xzlog.init_logger(__XZ_LOG_FILE__)
        self._cfgfile = cfgfile
        self._parser  = ConfigParser.RawConfigParser()
        self._read()
        xzlog.info("Configure file is %s" % self._cfgfile)

    # Init the configure file
    #def _init(self, cfgfile=None):
    #    if cfgfile is not None:
    #        self._cfgfile = cfgfile
    #    self._read()
    #    xzlog.info("Configure file is %s" % self._cfgfile)

    # Read a configure file
    def _read(self):
        self._parser.read(self._cfgfile)

    # Get Sections in configure file
    def _sections(self):
        return self._parser.sections()

    # Get Options for one Section
    def _options(self, section):
        return self._parser.options(section)

    # Get Key-Value pairs for one Section
    def _items(self, section):
        return self._parser.items(section)

    # Get the Value of one Option in Section
    def _get(self, section, option):
        self._read()
        return self._parser.get(section, option)

    # Set the Value of one Option in Section
    def _set(self, section, option, value):
        self._parser.set(section, option, value)
        with open(self._cfgfile, 'wb') as configfile:
            self._parser.write(configfile)


    # Dump all info
    def _dump(self):
        print
        print "%-10s | %-10s | %-10s" \
            % ( 'Section', 'Option', 'Value')
        print "%-10s | %-10s | %-10s" \
            % ( '-'*10, '-'*10, '-'*10)
        for section in self._sections():
            for option in self._options(section):
                value = self._get(section,option)
                print "%-10s | %-10s | %-10s" \
                    % ( section, option, value)
        print
        print self._get('logs', 'logfile')

# xzcfg global hanlder
xzcfg = xzCfg()

def _test():
    cfg = xzCfg("../config.ini")
    cfg._dump()





if __name__ == "__main__":
    _test()
