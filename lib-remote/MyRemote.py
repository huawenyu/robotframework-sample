# -*- coding: utf-8 -*-
from robot.api import logger
from ConfigParser import SafeConfigParser
import pexpect
import sys, time, re, os

AT_CONFIG = None
AT_DEBUG = True
AT_DUTS = {}
ansi_escape = None

def PrintE(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

class MyRemote:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        global AT_CONFIG
        global ansi_escape
        sys.stdout = Unbuffered(sys.stdout)
        ansi_escape = re.compile(r'\x1b[^m]*m')
        AT_CONFIG = SafeConfigParser()
        AT_CONFIG.read('config')
        print 'Config:'
        print AT_CONFIG.get('linux-1', 'host')
        print AT_CONFIG.get('linux-1', 'username')

    def sendline(self, dut_id, line):
        global AT_DUTS
        global ansi_escape
        print "Sendline '%s', '%s'." % (dut_id, line)
        try:
            if (not AT_DUTS.has_key(dut_id)):
                self._login(dut_id, AT_CONFIG.get(dut_id, 'command'),
                        AT_CONFIG.get(dut_id, 'username'),
                        AT_CONFIG.get(dut_id, 'password'))

            dut = AT_DUTS.get(dut_id, None)
            if (not dut):
                raise Exception('DUT ' % dut_id % ' login fail.')

            ret = dut.sendline(line)
            ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                            ],
                            timeout=0.5)
            print(dut.before)
            #print(ansi_escape.sub('', dut.before))
        except Exception as e:
            PrintE(e)

    def __login_parser(self, dut_id, dut, username, passwd):
        global AT_DUTS
        print "Login parser ..."
        try:
            ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                            'login:', 'password:', 'Password:'],
                            timeout=3)
            print "Login response ..."
            if ret == 0:
                print('restarting login')
            elif ret == 1:
                print('TIMEOUT in login command...')
            else:
                AT_DUTS[dut_id] = dut;
                if ret == 2: # login
                    dut.sendline(username)
                    print "send username '%s'" % (username)
                elif ret == 3 or ret == 4: # passwd
                    print "send password"
                    if passwd:
                        dut.sendline(passwd)
                    else:
                        dut.sendline('\n')
                print "Login '%s' OK ..." % (dut_id)
            return ret;

        except Exception as e:
            PrintE(e)

    def _login(self, dut_id, command, username, passwd):
        global AT_DUTS
        print "Login '%s@%s' with '%s'." % (username, dut_id, command)
        try:
            dut = pexpect.spawn(command)
            while True:
                ret = self.__login_parser(dut_id, dut, username, passwd)
                print "login parser ret=%d" % (ret)
                if (ret == 3 or ret == 4):
                    print("Ligin Succ...")
                    break

        except Exception as e:
            PrintE(e)

def main ():
    try:
        dut = MyRemote()
        dut.sendline('linux-1', 'ls -l')
        dut.sendline('linux-1', 'uname -a')
        #dut.sendline('vm-cache', 'get system status')
    except Exception as e:
        PrintE(e)

if __name__ == '__main__':
    main ()
