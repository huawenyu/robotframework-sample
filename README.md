Pre-requirement
===============
- python3-venv: `sudo apt install -y python3-venv`
- Auto setup python env by [direnv](https://github.com/direnv/direnv): `sudo apt install -y direnv`

## direnv: auto start python env

	### everytime, when change .envrc, should allow it by: direnv allow
	$ cat .envrc
		python3 -m venv venv/
		source venv/bin/activate

		# To avoid direnv: "Unable to override PS1 with direnv"
		# Must be bottom
		unset PS1


Install Robotframework
======================
``` Shell
$ sudo pip install robotframework
$ sudo pip install docutils
$ sudo pip install robotframework-selenium2library
$ sudo pip install robotframework-ride
$ sudo apt-get install python-tk        <<< used by Diaglog
$ sudo apt-get install python-wxgtk2.8	<<< used by RIDE
$ ride.py		<<< GUI
```

Run
===

`$ robot -A config`

Sample: Hello world
===================
1. Run RIDE (GUI)
2. New Project “HelloWorld”
3. New Test Suite “HelloWorld”, Select Fold + Text type
4. New Test Case “HelloWorld”, Keep the default: File + Text
5. Click Text Edit, and copy&paste

```TXT
*** Settings ***
Library           OperatingSystem

*** Variables ***
${MESSAGE}        Hello, world!

*** Test Cases ***
My Test
    [Documentation]    Example test
    Log    ${MESSAGE}
    My Keyword    /tmp

Another Test
    Should Be Equal    ${MESSAGE}    Hello, world!

*** Keywords ***
My Keyword
    [Arguments]    ${path}
    Directory Should Exist    ${path}
```

6. Select the test case from left-tree, and click QuickButton ‘run’
Use F5 to list current all available KeyWord

Run from command line
=====================

https://bitbucket.org/robotframework/webdemo/wiki/Home#rst-header-running-demo

Given a Login Page verify that when the correct username and password are supplied, it is possible to login.

```Shell
$ cd WebDemo
$ python demoapp/server.py	<<< run the test web server
$ pybot login_tests		<<< run test suite

$ pybot login_tests/valid_login.txt
$ pybot --test InvalidUserName --loglevel DEBUG login_tests

$ pybot --variable BROWSER:Chrome login_tests
$ pybot --variable BROWSER:IE login_tests
```
