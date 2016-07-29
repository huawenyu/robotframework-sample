# -*- coding: utf-8 -*-
#from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from ConfigParser import SafeConfigParser
import pexpect
import sys, time, re, os, uuid
import logging

class DutState:
        Init, Connect, Username, Passwd, Welcome, SetPrompt, Fail = range(7)

AT_CONFIG = None
AT_DEBUG = True
AT_DUTS = {} # {'dut_id': {'dut': dut_connect, 'state': DutState.Init}, }
ansi_escape = None
logger = None
type_list = ['linux', 'dut']
echo_list = ['fnsysctl echo', 'sysctl echo', 'echo']

def PrintE(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #logger.info("%s:%d %s: %s", fname, exc_tb.tb_lineno, str(exc_type), e.args)
    print("%s %s %d" % (exc_type, fname, exc_tb.tb_lineno))
    raise

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

class AtRemote:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        global AT_CONFIG
        global ansi_escape
        global logger

        sys.stdout = Unbuffered(sys.stdout)
        ansi_escape = re.compile(r'\x1b[^m]*m')

        import logging.config
        if __name__ == '__main__':
            log_conf = 'log.conf'
        else:
            log_conf = BuiltIn().get_variable_value('${LOG_CONF_FILE}', default='log.conf')
        if (os.path.isfile(log_conf)):
            log_config = (os.path.join(os.getcwd(), log_conf))
            logging.config.fileConfig(log_config)
            logger = logging.getLogger(__name__)
            BuiltIn().log_to_console("Loading log config %s" % (log_config))
        else:
            raise Exception('Log config not exist.')

        self._check_config()

    def _check_config(self):
        global AT_CONFIG
        global logger
        global type_list

        if __name__ == '__main__':
            dut_conf = 'dut.conf'
        else:
            dut_conf = BuiltIn().get_variable_value('${DUT_CONF_FILE}', default='dut.conf')
        if (os.path.isfile(dut_conf)):
            AT_CONFIG = SafeConfigParser()
            config_file = (os.path.join(os.getcwd(), dut_conf))
            AT_CONFIG.read(config_file)
            dut_ids = AT_CONFIG.sections()
            logger.info("Loading config %s: %s", config_file, dut_ids)
            BuiltIn().log_to_console("Loading config %s" % (config_file))
        else:
            raise Exception('config not exist.')

        for dut_id in dut_ids:
            if (not AT_CONFIG.get(dut_id, 'type') or AT_CONFIG.get(dut_id, 'type') not in type_list):
                raise Exception("Config invalid: DUT '%s' \
                                should have type: %s." % (dut_id, type_list))
            if (not AT_CONFIG.get(dut_id, 'host')):
                raise Exception("Config invalid: DUT '%s' \
                                should have host: Ip-Addr." % (dut_id))
            if (not AT_CONFIG.get(dut_id, 'command')):
                raise Exception("Config invalid: DUT '%s' \
                                should have command used to login." % (dut_id))
            if (not AT_CONFIG.get(dut_id, 'username')):
                raise Exception("Config invalid: DUT '%s' \
                                should have username used as login user." % (dut_id))
            if (not AT_CONFIG.get(dut_id, 'prompt')):
                raise Exception("Config invalid: DUT '%s' \
                                should have prompt used as output end str." % (dut_id))
        logger.info("  check config succ ...")

    def get_config(self, dut_id, item):
        global AT_CONFIG

        return AT_CONFIG.get(dut_id, item)

    def expect_string(self, dut_id, simple_str):
        dut = self.__resolve_dut(dut_id)['dut']
        #BuiltIn().log_to_console(dut.before)
        if dut.before.find(simple_str) == -1:
            raise Exception("DUT '%s' search fail: '%s'." % (dut_id, simple_str))

    def expect_dump(self, dut_id):
        dut = self.__resolve_dut(dut_id)['dut']
        BuiltIn().log_to_console("\nDump(%s):\n------\n%s\n------\n" % (dut_id, dut.before))
        logger.info("\nDump(%s):\n------\n%s\n------\n", dut_id, dut.before)

    def flush(self, dut_id):
        self.anchor(dut_id)

    def anchor(self, dut_id):
        global AT_DUTS
        global AT_CONFIG
        global ansi_escape
        global logger
        global echo_list

        try:
            dut_info = self.__resolve_dut(dut_id)
            if (not dut_info):
                raise Exception("DUT '%s' not connect." % (dut_id))

            uid = uuid.uuid1() #creating UUID
            uid_str = str(uid.hex)
            dut = dut_info['dut']

            if (AT_DUTS[dut_id]['echo'] in echo_list):
                loc_echo_list = [ AT_DUTS[dut_id]['echo'], ]
            else:
                loc_echo_list = echo_list

            for echo in loc_echo_list:
                AT_DUTS[dut_id]['echo'] = echo
                logger.debug("Anchor '%s' '%s' '%s'.",
                            dut_id, echo, uid_str)
                ret = dut.sendline(echo + ' ' + uid_str)
                ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                                uid_str, ], timeout=1)
                ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                                uid_str, ], timeout=1)
                if (ret == 1 or ret > 2):
                    continue
                elif ret == 2:
                    ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                                AT_CONFIG.get(dut_id, 'prompt') + ' # ',
                                r"'" + AT_CONFIG.get(dut_id, 'prompt') + "\(.*\) # '",
                                ],
                                timeout=1)
                    logger.debug("  '%s' anchor succ ret=%d",
                                AT_DUTS[dut_id]['echo'], ret)
                    break

        except Exception as e:
            PrintE(e)


    def __resolve_dut(self, dut_id):
        global AT_DUTS
        global AT_CONFIG
        global ansi_escape
        global logger

        try:
            dut_info = AT_DUTS.get(dut_id, None)
            if (not dut_info):
                self._login(dut_id, AT_CONFIG.get(dut_id, 'command'),
                        AT_CONFIG.get(dut_id, 'username'),
                        AT_CONFIG.get(dut_id, 'password'),
                        AT_CONFIG.get(dut_id, 'prompt'))
                dut_info = AT_DUTS.get(dut_id, None)

            return dut_info
        except Exception as e:
            PrintE(e)

    def sendline(self, dut_id, lines):
        #BuiltIn().log_to_console(lines)
        line_list = lines.split('\n')
        for line in line_list:
            self._sendline(dut_id, line.strip("'\r\n"))

    def _sendline(self, dut_id, line):
        global AT_DUTS
        global AT_CONFIG
        global ansi_escape
        global logger

        try:
            dut_info = self.__resolve_dut(dut_id)
            if (not dut_info):
                raise Exception("DUT '%s' not connect." % (dut_id))

            logger.debug("Sendline '%s' '%s'.", dut_id, line)
            #BuiltIn().log_to_console("Sendline '%s' '%s'." % (dut_id, line))
            dut = dut_info['dut']
            dut.flush()
            ret = dut.sendline(line)
            # VM64Cache (policy) # edit 3
            prompt_regex = r'.*' + re.escape(AT_CONFIG.get(dut_id, 'prompt')) + r' \(.*\) # '

            while True:
                ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                                  '\[sudo\] password ',
                                  AT_CONFIG.get(dut_id, 'prompt') + ' # ',
                                  #r'VM64Cache \(.*\) # ',
                                  prompt_regex,
                                  ],
                                 timeout=2)

                logger.debug("Dump(%d):\n", ret)
                if (ret == 0): # eof, timeout
                    logger.info("  Sendline Fail: eof")
                    raise Exception("Sendline fail(eof): '%s', '%s'" % (dut_id, line))
                elif (ret == 1): # eof, timeout
                    logger.info("  Sendline Fail: timeout")
                    raise Exception("Sendline fail(timeout): '%s', '%s'" % (dut_id, line))
                elif (ret == 2): # sudo password
                    logger.info("    sudo password")
                    dut.sendline(AT_CONFIG.get(dut_id, 'password'))
                elif (ret == 3 or ret == 4): # prompt
                    #logger.debug(ansi_escape.sub('', dut.before))
                    logger.debug("------\nbefore=[%s]\nmatch=[%s]\nafter=[%s]\n------\n",
                                dut.before, str(dut.match.group()), dut.after)
                    break

        except Exception as e:
            PrintE(e)

    def __login_parser(self, dut, dut_id, username, passwd, prompt):
        global AT_DUTS
        global logger

        login_finish = False;
        try:
            ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT,
                                    'Last login: ', 'Welcome ',
                                    'password: ', 'Password: ',
                                    ' login: ',
                                    ], timeout=3)
            logger.debug("  response %d", ret)
            if ret >= 2:
                if ret == 6: # login
                    if AT_DUTS[dut_id]['state'] < DutState.Username:
                        AT_DUTS[dut_id]['state'] = DutState.Username;
                        dut.sendline(username)
                        logger.debug("  send username '%s'", username)
                elif ret == 4 or ret == 5: # passwd
                    if AT_DUTS[dut_id]['state'] < DutState.Passwd:
                        AT_DUTS[dut_id]['state'] = DutState.Passwd;
                        if passwd:
                            dut.sendline(passwd)
                        else:
                            dut.sendline('\n')
                        logger.debug("  send password")
                elif ret == 2 or ret == 3: # welcome
                    if AT_DUTS[dut_id]['state'] < DutState.Welcome:
                        AT_DUTS[dut_id]['state'] = DutState.Welcome;
                        logger.info("  welcome ...")

                        # change prompt
                        if self.__login_prompt(dut, dut_id, prompt):
                            login_finish = True
                            self.anchor(dut_id)
            else:
                login_finish = True
                AT_DUTS[dut_id]['state'] = DutState.Fail;
                raise Exception("DUT '%s' login fail." % (dut_id))
            return login_finish;

        except Exception as e:
            PrintE(e)
            return login_finish;

    def __login_prompt(self, dut, dut_id, prompt):
        global AT_CONFIG
        global AT_DUTS
        global logger

        # change prompt
        dut.sendline('\n')
        ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT, prompt + " # "], timeout=1)
        if ret == 2:
            return True

        if AT_DUTS[dut_id]['state'] < DutState.SetPrompt:
            AT_DUTS[dut_id]['state'] = DutState.SetPrompt;

            dut_type = AT_CONFIG.get(dut_id, 'type')
            if dut_type == 'linux':
                logger.debug("  linux set PS1 '%s'", prompt)
                dut.sendline("PS1='" + prompt + " # '")
            elif dut_type == 'dut':
                logger.debug("  dut set hostname '%s'", prompt)
                dut.sendline("config system global\n")
                dut.sendline("set host " + prompt + "\n")
                dut.sendline("set admintime 480\n")
                dut.sendline("end\n")

            dut.sendline('\n')
            ret = dut.expect([pexpect.EOF, pexpect.TIMEOUT, prompt + " # "], timeout=1)
            if ret == 2:
                return True
        return False

    def _login(self, dut_id, command, username, passwd, prompt):
        global AT_DUTS
        global AT_CONFIG
        global logger

        logger.info("Login '%s@%s' with '%s'.", username, dut_id, command)
        try:
            dut = pexpect.spawn(command)

            if __name__ == '__main__':
                  log_dir = 'logs'
            else:
                  log_dir = BuiltIn().get_variable_value('${LOG_DIR}', default='logs')
            # logfile_read() will ONLY log the network device's echo'd output.
            #   It will not log p.sendline() characters. This is the desired
            #   result the original poster was looking for.
            #dut.logfile = open(log_dir + "/" + dut_id, "w")
            dut.logfile_read = open(log_dir + '/' + dut_id, "w")

            AT_DUTS[dut_id] = {'dut': dut, 'state': DutState.Connect, 'echo': AT_CONFIG.get(dut_id, 'echo')};

            login_finish = False
            while (not login_finish):
                login_finish = self.__login_parser(dut, dut_id, username, passwd, prompt)
                logger.debug("  state %d: finish=%s", AT_DUTS[dut_id]['state'], login_finish)

        except Exception as e:
            PrintE(e)


def main():
    global logger
    global AT_CONFIG

    try:
        test_obj1 = MyRemote()
        #test_obj1.sendline('linux-1', 'ls -l')
        #test_obj1.sendline('linux-1', 'uname -a')
        #test_obj1.sendline('linux-1', 'uname -a')
        test_obj1.sendline('vm-cache', 'get system status')
        #test_obj1.sendline('vm-cache-2', 'get system status')
        test_obj1.anchor('vm-cache')
    except Exception as e:
        PrintE(e)

if __name__ == '__main__':
    main()

