#!/usr/bin/env python
#======================================================
# Title             : csfcfg.py
# Description       : config file parser
# Author            : ujnzxw
# Date              : 2016-07-16
# Version           : 0.0.1
# Usage             : python csfcfg.py
# Notes:            :
#======================================================

import ConfigParser

from csflog import csflog

class csfCfg(object):

    # Init attribute
    def __init__(self, cfgfile = ''):
        csflog.init_logger("../logs/wechat.log")
        self._cfgfile = cfgfile
        self._parser  = ConfigParser.ConfigParser()

    # Init the configure file
    def _init(self, cfgfile):
        self._cfgfile = cfgfile
        self._read()
        csflog.info("Configure file is %s" % self._cfgfile)

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
        return self._parser.get(section, option)

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

# csfcfg global hanlder
csfcfg = csfCfg()

def _test():
    cfg = csfCfg("../cfg.ini")
    cfg._dump()





if __name__ == "__main__":
    _test()
