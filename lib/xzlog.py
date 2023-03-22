# -*- coding: GB18030 -*-
'''
Created on May 8, 2012

@author: ujnzxw

@summary: uniform log object

@note:
 - debug     : debug info
 - info      : key process info
 - success   : important success info
 - warning   : warning message and may ignore
 - diagnose  : error diagnose info
 - error     : task error interruption (the process incldue many tasks)
 - critical  : process error interruption

 - info level (or higher) log should be formated in order to grep easily
 - info ( or higher level) log will be printed to STDOUT
 - all level log will print to log file
 - wf (warning file) log file print the log level > warning
'''

import os
import sys
import traceback
import logging
import inspect


# init logging
SUCCESS = 25    # higher than INFO, lower than WARNING
DIAGNOSE = 35   # > WARNING, < ERROR
def init_logging():
    # add a SUCCESS level
    logging.addLevelName(SUCCESS, "SUCC")

    # add a DIAGNOSE level
    logging.addLevelName(DIAGNOSE, "DIAG")

# global init function
init_logging()

def Singleton(cls):
    _instance = {}
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
    return _singleton

@Singleton
class XZLog(object):
    def __init__(self, logger_name="xzlog", tag_name="XZLog"):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.tag_name = tag_name

        # other members
        self.sh = None
        self.fmt_sh = None
        self.logpath = None

        # set whole logger level
        self.logger.setLevel(logging.DEBUG)

    def set_tag_name(self, tag_name):
        self.tag_name = tag_name

    # screen log setting
    def init_stream_handler(self):
        # determine if double init
        for h in self.logger.handlers:
            if isinstance(h, logging.StreamHandler):
                self.warning("Logger %s already has stream handler, ignore this one" % self.logger_name)
                return


        # print info (or higher) level log info to STDOUT
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)

        # log format for STDOUT
        self.fmt_sh = logging.Formatter("[\033[1;%(colorcode)sm%(levelname)-8s\033[0m %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        sh.setFormatter(self.fmt_sh)

        # add handler in logger
        self.logger.addHandler(sh)

        # save STDOUT handle for further use
        self.sh = sh

    def set_no_color(self):
        '''@summary: don't print color in STDOUT'''
        self.fmt_sh = logging.Formatter("[%(levelname)-8s %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        self.sh.setFormatter(self.fmt_sh)

    def set_sh_debug(self):
        '''@summary: print debug level log to STDOUT'''
        self.sh.setLevel(logging.DEBUG)

    def set_sh_warning(self):
        '''@summary: print warningfatal level log to STDOUT '''
        self.sh.setLevel(logging.WARNING)


    def init_logger(self, logpath, mode="a", force=False):
        '''
        @summary: init logfile logger processor
        @param mode: 'w' for overwrite, 'a' for append
        @param force: ignore the other init when get the first False overriter the privious init when get the last True
        '''
        # determine if double init
        fhs = [fh for fh in self.logger.handlers if isinstance(fh, logging.FileHandler)]
        if fhs:
            # already init by other file
            if force:
                # force update
                map(self.logger.removeHandler, fhs)
            else:
                # keep the privious setting
                self.warning("Logger %s already has file handler\nIgnore this one: %s\nReserve old one: %s" % (self.logger_name, logpath, self.logpath))
                return


        # create the directory
        logdir = os.path.dirname(logpath)
        if logdir:
            cmd = "mkdir -p " + logdir
            os.system(cmd)

        # logfile keep all level's log info
        fh = logging.FileHandler(logpath, mode)
        fh.setLevel(logging.DEBUG)

        # logfile format
        fmt_fh = logging.Formatter("[%(levelname)-8s %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        fh.setFormatter(fmt_fh)

        # add handler in logger
        self.logger.addHandler(fh)

        # .wf logfile - print warning(or higher) level info
        fh_wf = logging.FileHandler(logpath+".wf", mode)
        fh_wf.setLevel(logging.WARNING)

        # .wf logfile format
        fmt_fh_wf = logging.Formatter("[%(levelname)-8s %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        fh_wf.setFormatter(fmt_fh_wf)

        # add handler in logger
        self.logger.addHandler(fh_wf)

        # save logpath in order to unpickle
        self.logpath = logpath

    # log print functions
    def debug(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "0")    # white
        self.logger.debug(msg, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "36")   # blue
        self.logger.info(msg, **kwargs)

    def success(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "32")   # green
        self.logger.log(SUCCESS, msg, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "33")   # yellow
        self.logger.warning(msg, **kwargs)

    def diagnose(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "35")   # pink
        self.logger.log(DIAGNOSE, msg, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "31")   # red
        self.logger.error(msg, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        #msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "41")   # red backgroud
        self.logger.critical(msg, **kwargs)

    # find caller
    def __update_caller(self, kwargs):
        '''
        @summary: update caller info in kwargs
        @attention:
         - must be called by debug() directly
         - cannot be overwrite by child class
         '''
        # set nest_level
        if "nest_level" in kwargs:
            nest = kwargs["nest_level"]
            del kwargs["nest_level"]
        else:
            nest = 0    # default 0

        # get correct stack info
        try:
            frame = inspect.stack()[2+nest]     # go to 2 higher level default, __update_caller <- log functions <- log invoker
            _, fn, lno, func, _, _ = frame
            fn = os.path.basename(fn)
        except Exception:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"

        # set xtra dict
        if not "extra" in kwargs:
            # NO extra dict in kwargs, create it
            kwargs["extra"] = {}

        kwargs["extra"]["myfn"] = fn
        kwargs["extra"]["mylno"] = lno
        kwargs["extra"]["myfunc"] = func

    # msg hanlde function
    def __indent_msg(self, msg, args):
        '''@summary: indent msg from second line'''
        msg_lines = msg.splitlines(True)
        if not msg_lines:
            msg_lines = [""]

        msg_indent_lines = []
        msg_indent_lines.append(msg_lines[0])
        msg_indent_lines.extend(["  - " + line for line in msg_lines[1:]] )

        return "".join(msg_indent_lines)

    # kwargs hanlde function
    def _update_kwargs(self, kwargs, colorcode):
        # set extra dict
        kwargs["extra"]["colorcode"] = colorcode

        # set tagname in kwargs dict
        if "tag_name" in kwargs:
            tagname = kwargs["tag_name"]
            del kwargs["tag_name"]
        else:
            tagname = self.tag_name
        kwargs["extra"]["tagname"] = tagname

        # delete illegal keys
        self.__clean_kwargs(kwargs)

    def __clean_kwargs(self, kwargs):
        '''@summary: delter illegal keys in kwargs'''
        for key in kwargs.keys():
            if key not in ("exc_info", "extra"):
                del kwargs[key]


class LogProxy(object):
    '''@summary: logger proxy class, Globally unique'''
    def __init__(self, inst):
        self.set_instance(inst)

    def set_instance(self, inst):
        self.inst = inst

    def __getattr__(self, name):
        '''@summary: transfer to self.inst if the visiting not exist'''
        return getattr(self.inst, name)


# xzlog global hanlder print to STDOUT default
xzlog = LogProxy(XZLog())
xzlog.init_stream_handler()


def _test():
    xzlog.init_logger("./test.log")

    xzlog.debug("debug log")
    xzlog.info("info %s log\n break line")
    try:
        raise Exception, "except exception" # this is a exception comments
    except Exception:
        xzlog.warning("warning %s", "log", exc_info=True)
    xzlog.diagnose("error %slog", "format string")
    xzlog.critical("critical log")

if __name__ == "__main__":
    _test()
