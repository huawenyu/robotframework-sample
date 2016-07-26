from robot.api import logger

class ExampleLibrary:

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._counter = 0

    def count(self):
        self._counter += 1
        print self._counter

    def clear_counter(self):
        self._counter = 0

    def log_test(self):
        print 'Hello from a library.'
        print '*WARN* Warning from a library.'
        print '*ERROR* Something unexpected happen that may indicate a problem in the test.'
        print '*INFO* Hello again!'
        print 'This will be part of the previous message.'
        print '*INFO* This is a new message.'
        print '*INFO* This is <b>normal text</b>.'
        print '*HTML* This is <b>bold</b>.'
        print '*HTML* <a href="http://robotframework.org">Robot Framework</a>'

    def hello(self, name):
        print "Hello, %s!" % name
        logger.console('Got arg %s' % name)

    def do_nothing(self):
        pass

    def do_nothing2(self):
        raise AssertionError("*HTML* <a href='robotframework.org'>Robot Framework</a> rulez!!")


    def no_arguments(self):
        print "Keyword got no arguments."

    def one_argument(self, arg):
        print "Keyword got one argument '%s'." % arg

    def three_arguments(self, a1, a2, a3):
        print "Keyword got three arguments '%s', '%s' and '%s'." % (a1, a2, a3)


    def return_string(self):
        return "Hello, world!"

    def return_object(self, name):
        return MyObject(name)

    def return_two_values(self):
        return 'first value', 'second value'

    def return_multiple_values(self):
        return ['a', 'list', 'of', 'strings']

