from netmiko import ConnectHandler
import requests
from getpass import getpass
import re


def cisco_cli_query (host, command):
	"""
	Open a connection to the Host CLI via Netmiko
	The command parameter will be sent to the CLI and the response will be returned
	"""
	
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

def structurize_arp_table (arp_table_raw):
	"""
	Parse the raw unstructured CLI output from a 'show ip arp' command
	The regular expression below is designed to extract the IP Address, MAC Address, and Interface	
	"""
	
	arp_rex = '(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}).+(\\w{4}\\.\\w{4}.\\w{4}).+?(\\S+)$'
	arp_table = re.findall(arp_rex, arp_table_raw, re.MULTILINE)
	return arp_table


def cli_arp_table_example():
	"""
	Sample execution comparing raw output and parsed output
	"""
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