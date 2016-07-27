# -*- coding: utf-8 -*-
from robot.api import logger
from ConfigParser import SafeConfigParser
import pexpect
import sys, time, re, os
import logging

AT_CONFIG = None
AT_DEBUG = True
AT_DUTS = {}
ansi_escape = None
logger = None

def PrintE(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logger.info("%s %s %d", str(exc_type), fname, exc_tb.tb_lineno)
    #print("%s %s %d" % (exc_type, fname, exc_tb.tb_lineno))
    raise

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
        global logger

        self.expect_list = []
        sys.stdout = Unbuffered(sys.stdout)
        ansi_escape = re.compile(r'\x1b[^m]*m')

        import logging.config
        if (os.path.isfile('log.conf')):
            print "Loading Log configure 'log.conf'"
            logging.config.fileConfig('log.conf')
            logger = logging.getLogger(__name__)
        else:
            raise Exception('log.config not exists.')

        self._check_config()

    def _check_config(self):
        global AT_CONFIG
        global logger

        AT_CONFIG = SafeConfigParser()
        AT_CONFIG.read('config')
        dut_ids = AT_CONFIG.sections()
        for dut_id in dut_ids:
            if (not AT_CONFIG.get(dut_id, 'type')):
                raise Exception('Config invalid: DUT ' % dut_id
                                % ' should have type: linux|box.')
            if (not AT_CONFIG.get(dut_id, 'host')):
                raise Exception('Config invalid: DUT ' % dut_id
                                % ' should have host: Ip-Addr.')
            if (not AT_CONFIG.get(dut_id, 'command')):
                raise Exception('Config invalid: DUT ' % dut_id
                                % ' should have command used to login.')
            if (not AT_CONFIG.get(dut_id, 'username')):
                raise Exception('Config invalid: DUT ' % dut_id
                                % ' should have username used as login user.')
            if (not AT_CONFIG.get(dut_id, 'prompt')):
                raise Exception('Config invalid: DUT ' % dut_id
                                % ' should have prompt used as output end str.')
        logger.info("Check config succ ...")

    def sendline(self, dut_id, line):
        global AT_DUTS
        global ansi_escape
        global logger

        logger.debug("Sendline '%s' '%s'.", dut_id, line)
        try:
            if (not AT_DUTS.has_key(dut_id)):
                self._login(dut_id, AT_CONFIG.get(dut_id, 'command'),
                        AT_CONFIG.get(dut_id, 'username'),
                        AT_CONFIG.get(dut_id, 'password'),
                        AT_CONFIG.get(dut_id, 'prompt'))

            dut = AT_DUTS.get(dut_id, None)
            if (not dut):
                raise Exception('DUT ' % dut_id % ' not connect.')

            ret = dut.sendline(line)
            ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                            AT_CONFIG.get(dut_id, 'prompt') + ' # ',
                            r"'" + AT_CONFIG.get(dut_id, 'prompt') + "\(.*\) # '",
                              ],
                            timeout=2)
            logger.debug("Dump(%d):\n------\nbefore=[%s]\nmatch=[%s]\nafter=[%s]\n------\n",
                         ret, dut.before, str(dut.match.group()), dut.after)
            #logger.debug(ansi_escape.sub('', dut.before))
            if (ret == 0): # eof, timeout
                logger.info("  Sendline Fail: eof")
                raise Exception('Sendline ' % dut_id % ' ' %  line % ' fail: eof.')
            elif (ret == 1): # eof, timeout
                logger.info("  Sendline Fail: timeout")
                raise Exception('Sendline ' % dut_id % ' ' %  line % ' fail: timeout.')
            elif (ret == 2 or ret == 3): # prompt
                pass

        except Exception as e:
            PrintE(e)

    def __login_parser(self, dut, dut_id, username, passwd, prompt):
        global AT_DUTS
        global logger

        try:
            if (not self.expect_list):
                self.expect_list = [pexpect.EOF, pexpect.TIMEOUT,
                                    'login:',
                                    'password:', 'Password:',
                                    'Welcome '];

            ret = dut.expect(self.expect_list, timeout=3)
            logger.debug("Login command response ...")
            if ret >= 2:
                if ret == 2: # login
                    dut.sendline(username)
                    logger.debug("  send username '%s'", username)
                elif ret == 3 or ret == 4: # passwd
                    if passwd:
                        dut.sendline(passwd)
                    else:
                        dut.sendline('\n')
                    logger.debug("  send password")
                elif ret == 5: # welcome
                    # change prompt
                    self.__login_prompt(dut, dut_id, prompt)
                    #self.expect_list.append(prompt + " # ")
            return ret;

        except Exception as e:
            PrintE(e)

    def _login(self, dut_id, command, username, passwd, prompt):
        global AT_DUTS
        global logger

        logger.info("Login '%s@%s' with '%s'.", username, dut_id, command)
        try:
            dut = pexpect.spawn(command)
            dut.logfile = open("logs/" + dut_id, "w")
            AT_DUTS[dut_id] = dut;
            while True:
                ret = self.__login_parser(dut, dut_id, username, passwd, prompt)
                logger.debug("  parser ret=%d", ret)
                if (ret < 2): # eof, timeout
                    logger.info("Login Fail ...")
                    raise Exception('Login DUT ' % dut_id % ' fail.')
                    break
                elif (ret == 3 or ret == 4): # send password
                    logger.info("Login Succ ...")
                elif (ret == 5): # send password
                    logger.info("Welcome ...")
                    time.sleep(1)
                    break
                elif (ret == 6): # send password
                    logger.info("Set prompt Succ ...")
                    break

        except Exception as e:
            PrintE(e)

    def __login_prompt(self, dut, dut_id, prompt):
        global AT_CONFIG
        global logger

        dut_type = AT_CONFIG.get(dut_id, 'type')
        if dut_type == 'linux':
            logger.debug("Change linux prompt to '" + prompt + "'")
            dut.sendline("PS1='" % prompt % " # '")
        elif dut_type == 'dut':
            logger.debug("Change dut hostname to '" + prompt +  "'")
            dut.sendline("config system global")
            dut.sendline("set host " + prompt)
            dut.sendline("set admintime 480")
            dut.sendline("end")


def main ():
    global logger

    try:
        test_obj1 = MyRemote()
        #test_obj1.sendline('linux-1', 'ls -l')
        #test_obj1.sendline('linux-1', 'uname -a')
        test_obj1.sendline('vm-cache-2', 'get system status')
    except Exception as e:
        PrintE(e)

if __name__ == '__main__':
    main ()
