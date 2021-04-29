from netmiko import ConnectHandler
import requests
from getpass import getpass
import re


#Get a response from a Cisco IOS-XE device CLI
def cisco_cli_query (host, command):
	csr = {
		'device_type': 'cisco_ios',
		'host': host,
		'username': username,
		'password': password
		}
	try:
		csr_connection = ConnectHandler(**csr)
		output = csr_connection.send_command(command)
		return output
	except:
		print('CLI query failed - program will exit')
		quit()

#Extra data from the output string
def structurize_arp_table (arp_table_raw):
	arp_rex = '(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}).+(\\w{4}\\.\\w{4}.\\w{4}).+?(\\S+)$'
	arp_table = re.findall(arp_rex, arp_table_raw, re.MULTILINE)
	return arp_table


#Calls the above functions and displays the output
def cli_arp_table_example():
	raw_arp_table = cisco_cli_query(host, 'show ip arp')
	
	print('This is the raw(unstructured) CLI response:')
	print(raw_arp_table)
	
	arp_table = structurize_arp_table(raw_arp_table)
	
	print('\nThis is the parsed structured data:')
	print(*arp_table, sep='\n')
	
if __name__ == '__main__':

	#We will use Cisco's public Devnet lab CSR (that means you can run this code yourself - credentials are developer/C1sco12345
	host = 'sandbox-iosxe-latest-1.cisco.com'
	
	#prompt for credentials - password does not echo
	username = input('Username:')
	password = getpass('Password:')
	
	cli_arp_table_example()