# rfdemo

Demo for Network Test Automation by  Robot Framework + Netmiko + textfsm

	### Install textfsm templates
	$ cd
	$ git clone git@github.com:networktocode/ntc-templates.git
	$ export NET_TEXTFSM=/home/wilson/proj/ntc-templates/ntc_templates/

	$ python testlinux.py
	$ python testnetmiko.py
	$ robot -v IP:192.168.1.34 -v user:test -v pass:test -v hostname:xrv1 -v ifname:Gi0/0/0/0 ifshut_noshut.robot

## Error: ModuleNotFoundError: No module named 'clitable'

	pip list
		Package       Version
		------------- -------
		textfsm       1.1.2    <=== downgrade to 0.4.1 to fix the issue

	pip install --upgrade textfsm==0.4.1

# Run

	robot -v IP:192.168.1.34 -v user:test -v pass:test -v hostname:xrv1 -v ifname:Gi0/0/0/0 ifshut_noshut.robot

## netmiko work with robotframework

If the file you posted is the same file you run, then I guess you're not using the correct
function to print to the console. That said, as this is a rather small example I formatted as
a library for you. As I don't have the option to run Netmiko I was unable to test is properly.

```python
import netmiko

class NetmikoLibrary(object):

    ROBOT_LIBRARY_VERSION = 1.0

    def __init__(self):
        pass

    def display_cmd(self, cmd = 'whoami\n'):
        '''
            This is my Netmiko keyword to execute a command.
        '''
        mydevice = {
        'device_type': 'linux',
        'ip': '127.0.0.1',
        'username': 'gns3',
        'password': 'gns3',
        'verbose':True
        }

        conn = netmiko.ConnectHandler(**mydevice)

        output = conn.send_command(cmd)
        return output
```

This does mean that you can to load your library slightly different: Library         NetmikoLibrary.
