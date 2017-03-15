#!/usr/bin/python3
# vim: set fileencoding=utf-8:

"""A template script for command-line programs.
"""

from __future__ import print_function
import ctypes
import enum
import time
import fcntl
import struct
import sys
from collections import namedtuple


__author__ = "Bruce Duncan"
__copyright__ = "Copyright 2017, Bruce Duncan"
__licence__ = "GPL"
__version__ = "trunk"
__maintainer__ = "Bruce Duncan"
__email__ = "Bruce.Duncan@ed.ac.uk"
__status__ = "Development"


class fcntl_lock(enum.IntEnum):
    F_SETLK = 0
    F_SETLKW = 1
    F_GETLK = 2


class flock_type(enum.IntEnum):
    F_RDLCK = 0
    F_WRLCK = 1
    F_UNLCK = 2


class os_whence(enum.IntEnum):
    SEEK_SET = 0
    SEEK_CUR = 1
    SEEK_END = 2


struct_flock = struct.Struct('hhLLL')
flock_tuple = namedtuple('flock', 'type whence start len pid')


class flock(flock_tuple):
    def __repr__(self):
        v = self._asdict()
        v.update({'type': flock_type(v['type'])})
        v.update({'whence': os_whence(v['whence'])})
        s = ', '.join('{}={!r}'.format(name, v[name]) for name in self._fields)
        return "%s(%s)" % (self.__class__.__name__, s)


class FcntlLock(object):
    def __init__(self, fd):
        if hasattr(fd, 'fileno'):
            self.fd = fd.fileno()
        else:
            self.fd = fd

    def _fcntl_flock(self, op, l_type, start=0, whence=0, length=0, pid=0):
        return flock(*struct_flock.unpack(fcntl.fcntl(self.fd, op, struct_flock.pack(*flock(l_type, start, whence, length, pid)))))

    def unlock(self, pid=0):
        return self._fcntl_flock(fcntl.F_SETLK, fcntl.F_UNLCK)

    def lock(self, pid=0):
        return self._fcntl_flock(fcntl.F_SETLK, fcntl.F_WRLCK)

    def get_lock(self):
        return self._fcntl_flock(fcntl.F_GETLK, fcntl.F_WRLCK)

    def __enter__(self):
        self.lock()

    def __exit__(self, exctype=None, excinst=None, exctb=None):
        self.unlock()

    def __repr__(self):
        return '%s(fd=%s)' % (self.__class__.__name__, self.fd)


def main(args):
    libc = ctypes.CDLL('libc.so.6')
    with open(args[0], 'w') as f:
        db_lock = FcntlLock(f)
        print(db_lock)
        print(db_lock.unlock())
        print(db_lock.get_lock())
        print(db_lock.lock())
        libc.pause()

if __name__ == '__main__':
    main(sys.argv[1:])
