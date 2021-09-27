import pprint
from netmiko import ConnectHandler

# https://jcfsz.wordpress.com/2020/05/05/connecting-to-network-devices-using-netmiko/
# cisco_260 = {'device_type':"linux", 'host':'test', 'username':"test", 'password':"test", global_delay_factor=2, 'secret':'test', 'port':'22' }
#
# from netmiko import ConnectHandler
# my_connection = ConnectHandler(device_type='cisco_ios', host='10.10.10.101',
#                                username='admin', password='admin', secret='cisco')
#

cisco_260 = {
        'device_type': "linux",
        'host':'test',
        'username': "test",     # should add the user to sudoer, since enable() needed: sudo usermod -aG sudo test
        'password': "test",
        'secret': 'test',       # the password use by: enable() auto send command 'sudo -s'
        'port': '22',
        'session_log': 'my_output.txt',  # toubleshooting: check the debug file by 'tail -f my_output.txt'
        }

net_connect = ConnectHandler(**cisco_260)

net_connect.enable()
#print(net_connect.find_prompt())

output = net_connect.send_command("ls -lrt")
output = net_connect.send_command("pwd")
output = net_connect.send_command("ip addr")
print(output)
output = net_connect.send_command("arp -a", use_textfsm=True)
pprint.pprint(output)

# # https://codingnetworker.com/2015/08/parse-cli-outputs-textfsm/
# # Template file and TextFSM index
# index_file = 'index'
# template_dir = '/home/kbyers/NTC_ANS/templates'

#  # Create CliTable object
# cli_table = clitable.CliTable(index_file, template_dir)
# attrs = {'Command': command, 'platform': device_type}

# # Dynamically parse the output from the router against the template
# cli_table.ParseCmd(rawtxt, attrs)

# # Convert from clitable format to list-dict format
# structured_data = clitable_to_dict(cli_table)

# print
# pprint(structured_data)
# print
